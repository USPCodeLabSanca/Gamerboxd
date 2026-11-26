import { useQuery, keepPreviousData } from '@tanstack/react-query';
import { getGames, getGame, getAllGames } from '../services/gameService';

export function useGames({ search = "", page = 1, pageSize = 20, detail = false } = {}) {
    return useQuery({
        queryKey: ['games', { search, page, pageSize, detail }],
        queryFn: () => getGames({ search, page, pageSize, detail }),
        retry: false,
        placeholderData: keepPreviousData, 
    })
}

export function useGame(gameId) {
    return useQuery({
        queryKey: ['game', gameId],
        queryFn: () => getGame(gameId),
        enabled: !!gameId,
        retry: false,
    })
}

export function useAllGames({ search = "", detail = true } = {}) {
    return useQuery({
        queryKey: ['games', 'all', { search, detail }],
        queryFn: () => getAllGames({ search, detail }),
        retry: false,
        staleTime: 60_000,
    })
}