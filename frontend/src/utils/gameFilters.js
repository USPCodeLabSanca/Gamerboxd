const getYear = (game) => {
    const year = parseInt(String(game.year ?? '').slice(0, 4));
    return Number.isNaN(year) ? null : year;
};

const getters = {
    year: getYear,
    rating: (game) => game.gamerboxd_rating ?? null,
    likes: (game) => game.like_count ?? null,
    completed: (game) => game.completed_count ?? null,
};

export function sortGames(games, sort) {
    if (!sort) return games;
    const [field, direction] = sort.split(':');
    const get = getters[field];
    if (!get) return games;
    return [...games].sort((a, b) => {
        const first = get(a), second = get(b);
        if (first === null && second === null) return 0;
        if (first === null) return 1;
        if (second === null) return -1;
        return (first - second) * (direction === 'asc' ? 1 : -1);
    });
}

export function inDecade(game, decade) {
    const year = getYear(game);
    if (year === null) return false;
    return decade === 1980 ? year < 1990 : year >= decade && year < decade + 10;
}
