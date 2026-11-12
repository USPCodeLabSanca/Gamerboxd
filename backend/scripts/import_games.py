import argparse
import asyncio
import json
from pathlib import Path
import sys

import asyncpg
from dotenv import dotenv_values

backend = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend / "src"))

from models.schemas.game import GameOverview
from services.db_services.game import DB_create_game


async def import_games(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    games = [GameOverview(
        game_id=game["game_id"],
        title=game["name"],
        picture=game["picture"],
        year=int(game["release_date"][:4]) if game["release_date"] else None,
    ) for game in data]

    if len({game.game_id for game in games}) != len(games):
        raise ValueError("O arquivo contém IDs de jogos repetidos.")

    env = dotenv_values(backend / "src/.env")
    conn = await asyncpg.connect(
        user=env["DB_USER"], password=env["DB_PASS"], database=env["DB_NAME"],
        host=env["DB_HOST"], port=int(env["DB_PORT"]),
    )
    try:
        async with conn.transaction():
            for game in games:
                await DB_create_game(conn, game)
    finally:
        await conn.close()

    print(f"{len(games)} jogos importados.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    asyncio.run(import_games(args.file))
