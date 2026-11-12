import { describe, expect, it } from 'vitest';
import { getGame, getGames } from './gameService';

describe('Catálogo local', () => {
    it('retorna os jogos no formato da API preservando os IDs fornecidos', async () => {
        const result = await getGames();
        expect(result.count).toBe(7);
        expect(result.games.map((game) => game.game_id)).toEqual([2, 3, 7, 151, 13, 14, 26]);
        expect(result.games[0]).toEqual({
            game_id: 2,
            title: 'Minecraft',
            picture: 'https://images.igdb.com/igdb/image/upload/t_cover_big/co8fu7.jpg',
            year: 2011,
        });
    });

    it('busca por nome e pagina mantendo a ordem de relevância', async () => {
        expect((await getGames({search: '  MINECRAFT  '})).games.map((game) => game.game_id)).toEqual([2]);
        expect((await getGames({page: 1, pageSize: 2})).games.map((game) => game.game_id)).toEqual([2, 3]);
        expect((await getGames({page: 2, pageSize: 2})).games.map((game) => game.game_id)).toEqual([7, 151]);
        expect(await getGames({page: 5, pageSize: 2})).toEqual({count: 0, games: []});
    });

    it('consulta pelo ID fornecido e não reutiliza um ID antigo dos mocks', async () => {
        expect(await getGame('151')).toMatchObject({game_id: 151, title: 'Fortnite', year: 2017});
        expect(await getGame(6)).toBeNull();
    });
});
