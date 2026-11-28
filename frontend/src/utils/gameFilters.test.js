// @vitest-environment node
import { describe, expect, it } from 'vitest';
import { inDecade, sortGames } from './gameFilters';

describe('ordenação de jogos pelos agregados da API', () => {
    const games = [
        { game_id: 1, gamerboxd_rating: null, like_count: 8, review_count: 1, completed_count: 0 },
        { game_id: 2, gamerboxd_rating: 0, like_count: 2, review_count: 20, completed_count: 3 },
        { game_id: 3, gamerboxd_rating: 4.5, like_count: 0, review_count: 4, completed_count: 9 },
    ];
    const ids = (sort) => sortGames(games, sort).map((game) => game.game_id);

    it('mantém notas ausentes ao final nas duas direções e aceita nota zero', () => {
        expect(ids('rating:desc')).toEqual([3, 2, 1]);
        expect(ids('rating:asc')).toEqual([2, 3, 1]);
    });
    it('distingue curtidas no jogo de quantidade de reviews e completados', () => {
        expect(ids('likes:desc')).toEqual([1, 2, 3]);
        expect(ids('reviews:desc')).toEqual([2, 3, 1]);
        expect(ids('completed:desc')).toEqual([3, 2, 1]);
    });
    it('não altera a coleção e não inventa uma ordenação por curtidas nas reviews', () => {
        expect(sortGames(games, 'reviewLikes:desc')).toBe(games);
        ids('rating:desc');
        expect(games.map((game) => game.game_id)).toEqual([1, 2, 3]);
    });
    it('preserva os limites das décadas e exclui anos ausentes', () => {
        expect(inDecade({ year: '2020' }, 2020)).toBe(true);
        expect(inDecade({ year: '2030' }, 2020)).toBe(false);
        expect(inDecade({ year: '1979' }, 1980)).toBe(true);
        expect(inDecade({ year: null }, 1980)).toBe(false);
    });
});
