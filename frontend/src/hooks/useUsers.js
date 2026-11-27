import { useQuery, useMutation, useQueryClient} from '@tanstack/react-query';
import { deleteProfile, editProfile, followUser, getUser } from '../services/userService';

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
        onSuccess: () => queryClient.invalidateQueries({queryKey: ['user', id], queryKey: ['me']})
    })
}

export function useDeleteProfile() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => deleteProfile(),
        onSuccess: () => queryClient.setQueriesData({
            queryKey: ['user', id],
            queryKey: ['me']
        }, null
    )
    })
}

export function useFollowUser(userId) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => followUser(userId),
        onSuccess: () => queryClient.invalidateQueries({queryKey: ['user', id]})
    })
}