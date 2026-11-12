import { useQuery } from '@tanstack/react-query';
import { getGame, getGames } from '../services/gameService';

export function useGames(search = '', page = 1) {
    return useQuery({
        queryKey: ['games', search, page],
        queryFn: () => getGames({search: search, page: page}),
        retry: false,
    });
}

export function useGame(gameId) {
    return useQuery({
        queryKey: ['game', gameId],
        queryFn: () => getGame(gameId),
        enabled: !!gameId,
        retry: false,
    });
}
