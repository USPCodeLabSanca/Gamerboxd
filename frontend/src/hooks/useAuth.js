import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMe, login, logout } from '../services/authService';
import { register } from '../services/userService';

export function useMe() {
    return useQuery({
        queryKey: ['me'],
        queryFn: getMe,
        retry: false,
    })
}

export function useLogin() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({emailOrUsername, password}) => login(emailOrUsername, password),
        onSuccess: () => queryClient.invalidateQueries({queryKey: ['me']})
    });
}

export function useRegister() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({username, email, password}) => register(username, email, password),
        onSuccess: () => queryClient.invalidateQueries({queryKey: ['me']})
    });
}

export function useLogout() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => logout(),
        onSuccess: () => queryClient.setQueryData(['me'], null)
    });
}