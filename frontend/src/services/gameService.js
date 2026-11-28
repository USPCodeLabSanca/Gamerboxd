import api from "../api/client";

export async function getGames({ search = "", page = 1, pageSize = 20, detail = false, signal } = {}) {
    const res = await api.get("/games", {
        params: { search, page, page_size: pageSize, detail },
        signal,
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

export async function getAllGames({ search = "", detail = true, signal } = {}) {
    const all = [];
    const knownIds = new Set();
    let total;

    for (let page = 1; ; page++) {
        const res = await getGames({ search, page, pageSize: 50, detail, signal });
        total ??= res.total;
        for (const game of res.games) {
            if (knownIds.has(game.game_id)) throw new Error("O catálogo mudou durante a consulta. Tente novamente.");
            knownIds.add(game.game_id);
        }
        if (total !== res.total) throw new Error("O catálogo mudou durante a consulta. Tente novamente.");
        all.push(...res.games);
        if (all.length === res.total) break;
        if (res.games.length === 0 || all.length > res.total) {
            throw new Error("Não foi possível carregar todos os jogos para ordenar.");
        }
    }

    return all;
}
