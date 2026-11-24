import { useQuery, useMutation, useQueryClient, useInfiniteQuery} from '@tanstack/react-query';
import { blockUser, deleteProfile, editProfile, followUser, getBlocks, getFollowers, getFollowings, getUser, unblockUser, unfollowUser } from '../services/userService';

export function useGetUser(userId) {
    return useQuery({
        queryKey: ['user', userId],
        queryFn: () => getUser(userId),
        retry: false,
        enabled: !!userId,
    })
}

export function useEditProfile() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: editProfile,
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ['user']});
            queryClient.invalidateQueries({queryKey: ['me']})
        }
    })
}

export function useDeleteProfile() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => deleteProfile(),
        onSuccess: () => {
            queryClient.setQueryData(['me'], null);
            queryClient.removeQueries({queryKey: ['user'], exact: false})
        }
    })
}

export function useFollowUser(userId) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => followUser(userId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['user'] });
            queryClient.invalidateQueries({ queryKey: ['followings'] });
            queryClient.invalidateQueries({ queryKey: ['followers'] });
        }
    })
}

export function useUnfollowUser(userId) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => unfollowUser(userId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['user'] });
            queryClient.invalidateQueries({ queryKey: ['followings'] });
            queryClient.invalidateQueries({ queryKey: ['followers'] });
        }
    })
}

export function useGetFollowers(userId, filters = {}) {
    return useInfiniteQuery({
        queryKey: ['followers', userId, filters],
        queryFn: ({ pageParam }) =>
            getFollowers(userId, {
                ...filters,
                nextUrl: pageParam
            }),
        initialPageParam: null,
        getNextPageParam: (lastPage) => {
            return lastPage.next_url ?? undefined;
        },
        retry: false,
        enabled: !!userId,
    });
}


export function useGetFollowings(userId, filters = {}) {
    return useInfiniteQuery({
        queryKey: ['followings', userId, filters],
        queryFn: ({ pageParam }) =>
            getFollowings(userId, {
                ...filters,
                nextUrl: pageParam
            }),
        initialPageParam: null,
        getNextPageParam: (lastPage) => {
            return lastPage.next_url ?? undefined;
        },
        retry: false,
        enabled: !!userId,
    });
}

export function useBlockUser(userId) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => blockUser(userId),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey:['user']});
            queryClient.invalidateQueries({queryKey:['blocks']});
        }
    });
}

export function useUnblockUser(userId) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => unblockUser(userId),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey:['user']});
            queryClient.invalidateQueries({queryKey:['blocks']});
        }
    });
}


export function useGetBlocks(filters = {}) {
    return useInfiniteQuery({
        queryKey: ['blocks', filters],
        queryFn: ({ pageParam }) =>
            getBlocks({
                ...filters,
                nextUrl: pageParam
            }),
        initialPageParam: null,
        getNextPageParam: (lastPage) => {
            return lastPage.next_url ?? undefined;
        },
        retry: false,
    });
}
