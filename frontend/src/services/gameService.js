import data from "../data/games.json";

const games = [...data].sort((a, b) => b.relevancy - a.relevancy).map((game) => ({
    game_id: game.game_id,
    title: game.name,
    picture: game.picture,
    year: game.release_date ? Number(game.release_date.slice(0, 4)) : null,
}));

export async function getGames({search = "", page = 1, pageSize = 20} = {}) {
    const filtered = games.filter((game) => game.title.toLocaleLowerCase().includes(search.trim().toLocaleLowerCase()));
    const content = filtered.slice((page - 1) * pageSize, page * pageSize);

    return {count: content.length, games: content};
}

export async function getGame(gameId) {
    return games.find((game) => game.game_id === Number(gameId)) ?? null;
}
