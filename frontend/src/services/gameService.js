import api from "../api/client";

export async function getGames({ search = "", page = 1, pageSize = 20, detail = false } = {}) {
    const res = await api.get("/games", {
        params: { search, page, page_size: pageSize, detail },
    });

    return res.data;    // { total, count, games }
}

export async function getGame(gameId) {
    const res = await api.get(`/games/${gameId}`);

    return res.data;    // game completo
}

export function toCardGame(g) {
    return {
        id: g.game_id,
        title: g.title,
        url: g.picture,
        year: g.year,
        avgNota: g.gamerboxd_rating,
        totalLikes: g.like_count,
        totalReviews: g.review_count,
        totalCompleted: g.completed_count,
        jogou: false,
        liked: false,
        complete: false,
        nota: 0,
    };
}

export async function getAllGames({ search = "", detail = true } = {}) {
    const all = [];

    for (let page = 1; page <= 40; page++) {
        const res = await getGames({ search, page, pageSize: 50, detail });
        all.push(...res.games);

        if (res.games.length === 0 || all.length >= res.total) break;
    }

    return all;
}