import aiohttp
import asyncpg
from contextlib import asynccontextmanager
from dotenv import dotenv_values
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from time import sleep

from models import create_tables

class LifespanConfig():

    async def conn(self):
        """Estabelece uma conexão singular com a vm"""

        return await asyncpg.connect(
            user=self.vm_user, 
            password=self.vm_pass, 
            host=self.db_host,
            port=self.db_port
        )

    def read_env(self):
        """Carrega constantes do .env"""

        self.env = dotenv_values(".env")

        env_keys = [
            "IS_TESTING", "VM_USER", "VM_PASS", "DB_USER", "DB_PASS", "DB_NAME",
            "DB_HOST", "DB_PORT", "JWT_KEY", "RAWG_KEY", "FRONT_URL"
        ]

        for val in env_keys:
            if val not in self.env.keys():
                raise ValueError(f"Campo {val} faltando no .env!")

        for key, value in self.env.items():
            val = int(value) if value.isdigit() else value
            setattr(self, key.lower(), val)
        
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
        """ Cria o pool de conexões externas"""

        return aiohttp.ClientSession()


    @asynccontextmanager
    async def __call__(self, app: FastAPI):

        conn = None

        try:          
            self.read_env()                     # Lê o .env

            # Cria o BD
            conn = await self.conn()  
            await self.create_database(conn)

            # Armazena no app as chaves e os pools de conexão
            app.state.internal_pool = await self.create_internal_pool()
            app.state.external_pool = await self.create_external_pool()
            app.state.jwt_key = self.jwt_key
            app.state.rawg_key = self.rawg_key


            # Cria as tabelas
            await create_tables(conn)

        except Exception as e:
            raise RuntimeError(str(e))


        finally:
            if conn is not None:
                await conn.close()
               

        yield   # Roda o app

        # Fecha os pools de conexão
        await app.state.internal_pool.close()
        await app.state.external_pool.close()         




