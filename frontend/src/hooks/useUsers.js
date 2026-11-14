import { useQuery, useMutation, useQueryClient} from '@tanstack/react-query';
import { deleteProfile, editProfile, followUser, getUser, unfollowUser } from '../services/userService';

export function useUser(userId) {
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

export function useGetFollowers() {

}

export function useGetFollowing() {

}

export function useBlockUser() {

}

export function useUnblockUser() {

}

export function useGetBlocks() {
    
}