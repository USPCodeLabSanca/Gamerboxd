import { useQuery, useMutation, useQueryClient} from '@tanstack/react-query';
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
        onSuccess: () => queryClient.setQueryData(['me'], null)
    })
}

export function useFollowUser(userId) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => followUser(userId),
        onSuccess: () => queryClient.invalidateQueries({queryKey: ['user', userId]})
    })
}

export function useUnfollowUser(userId) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => unfollowUser(userId),
        onSuccess: () => queryClient.invalidateQueries({queryKey: ['user', userId]})
    })
}

export function useGetFollowers(userId) {
    return useQuery({
        queryKey: ['followers'],
        queryFn: getFollowers,
        retry: false,
    })
}

export function useGetFollowing() {
    return useQuery({
        queryKey: ['followings'],
        queryFn: getFollowings,
        retry: false,
    })
}

export function useBlockUser(userId) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => blockUser(userId),
        onSuccess: () => queryClient.invalidateQueries({queryKey:['user']})
    })
}

export function useUnblockUser(userId) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => unblockUser(userId),
        onSuccess: () => queryClient.invalidateQueries({queryKey: ['user']})
    })
}

export function useGetBlocks() {
    return useQuery({
        queryKey: ['blocks'],
        queryFn: getBlocks,
        retry: false,
    })
}