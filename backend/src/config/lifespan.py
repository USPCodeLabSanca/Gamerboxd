import aiohttp
import asyncpg
from contextlib import asynccontextmanager
from fastapi import FastAPI
import json
from pathlib import Path

from ..models import create_tables
from ..models.schemas.game import GameOverview
from ..services.db_services.game import DB_create_game, DB_read_last_game, DB_delete_game

class LifespanConfig():

    def __init__(self, env: dict):
        self.env = env


    async def conn(self):
        """Estabelece uma conexão singular com a vm"""

        return await asyncpg.connect(
            user=self.vm_user, 
            password=self.vm_pass, 
            host=self.db_host,
            port=self.db_port
        )


    def read_env(self):
        """Processa as constantes do .env"""

        env_keys = [
            "IS_TESTING", "VM_USER", "VM_PASS", "DB_USER", "DB_PASS", "DB_NAME",
            "DB_HOST", "DB_PORT", "JWT_KEY", "RAWG_KEY", "FRONT_URL", "BACK_URL",
            "LOAD_GAMES"
        ]

        for val in env_keys:
            if val not in self.env.keys():
                raise ValueError(f"Campo {val} faltando no .env!")

        for key, value in self.env.items():
            val = int(value) if value.isdigit() else value
            setattr(self, key.lower(), val)

        if self.load_games not in ["all", "skip", "new"]:
            raise ValueError('O campo LOAD_GAMES tem que ser "all", "skip" ou "new"!')


    async def create_database(self, conn): 
        """Cria o usuário que realiza as operações na vm e o bd, caso eles já não existirem"""
       
        # Verifica se o usuário que realiza as operações na vm já não existe
        role_exists = await conn.fetchval("SELECT 1 FROM pg_roles WHERE rolname = $1", self.db_user)

        if not role_exists: 
            # Cria o usuário que vai fazer as operações na vm
            query = f"""
                CREATE ROLE {self.db_user} WITH
                    LOGIN
                    SUPERUSER
                    CREATEDB
                    CREATEROLE
                    INHERIT
                    NOREPLICATION
                    NOBYPASSRLS
                    CONNECTION LIMIT -1
                    PASSWORD '{self.db_pass}';
                """
            
            await conn.execute(query)


        # Verifica se o banco de dados já não existe
        db_exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", self.db_name)

        if not db_exists:
            # Cria o banco de dados
            query = f"""
                CREATE DATABASE {self.db_name}
                    WITH
                    OWNER = {self.db_user}
                    ENCODING = 'UTF8'
                    LOCALE_PROVIDER = 'libc'
                    CONNECTION LIMIT = 30
                    IS_TEMPLATE = False;
            """
            await conn.execute(query)


    async def create_internal_pool(self):
        """Cria o pool de conexões com o banco de dados"""

        return await asyncpg.create_pool(
            dsn = f'postgresql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}',
            min_size = 5,
            max_size = 15,
            max_inactive_connection_lifetime = 300,
        )

             
    async def create_external_pool(self):
        """Cria o pool de conexões externas"""

        return aiohttp.ClientSession()


    async def load_games_into_db(self, conn):
        """Joga os games do JSON para a tabela de games"""

        json_path = Path.cwd().parent / "data"
        games_json = [f for f in json_path.iterdir() if f.is_file() and f.suffix == ".json"][0]

        with open(games_json, "r", encoding="utf-8") as file:
            data = json.load(file)

        total_games = data["total"]
        last_game_in_DB = (await DB_read_last_game(conn) or 0)
        offset = last_game_in_DB if self.load_games != "all" else 0

        for i in range(offset, total_games):
            g = data["games"][i]

            new_game = GameOverview(
                game_id = g["game_id"],
                title = g["title"],
                picture = g["picture"],
                year = g["release_date"][0:4]
            )

            await DB_create_game(conn, new_game, g["relevancy"])

        for i in range(total_games, last_game_in_DB):
            await DB_delete_game(conn, i)


    @asynccontextmanager
    async def __call__(self, app: FastAPI):

        conn = None

        try:          
            # Lê o .env
            self.read_env()

            # Cria o DB
            conn = await self.conn()  
            await self.create_database(conn)

            # Armazena no app as chaves e os pools de conexão
            app.state.internal_pool = await self.create_internal_pool()
            app.state.external_pool = await self.create_external_pool()
            app.state.jwt_key = self.jwt_key
            app.state.rawg_key = self.rawg_key

            # Cria as tabelas
            async with app.state.internal_pool.acquire() as pool_conn:
                await create_tables(pool_conn)

                if self.load_games != "skip":
                    await self.load_games_into_db(pool_conn)

        except Exception as e:
            raise RuntimeError(str(e))

        finally:
            if conn is not None:
                await conn.close()

        yield   # Roda o app

        # Fecha os pools de conexão
        await app.state.internal_pool.close()
        await app.state.external_pool.close()         




