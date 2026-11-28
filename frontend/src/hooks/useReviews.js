import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMe } from './useAuth';
import { createReview, deleteReview, editReview, findUserGameReview, getReview, getUserReviews, hasLikedReview, setReviewLike } from '../services/reviewService';

export function useReview(reviewId) {
    const { data: me } = useMe();
    return useQuery({
        queryKey: ['reviews', 'detail', reviewId, me?.user_id],
        queryFn: () => getReview(reviewId),
        enabled: !!reviewId,
        retry: false,
    });
}

export function useUserReviews(userId) {
    const { data: me } = useMe();
    return useInfiniteQuery({
        queryKey: ['reviews', 'user', userId, me?.user_id],
        queryFn: ({ pageParam }) => getUserReviews(userId, { nextUrl: pageParam }),
        initialPageParam: null,
        getNextPageParam: (page) => page.next_url ?? undefined,
        enabled: !!userId,
        retry: false,
    });
}

export function useUserGameReview(game) {
    const { data: me } = useMe();
    return useQuery({
        queryKey: ['reviews', 'game', game?.id, me?.user_id],
        queryFn: () => findUserGameReview(me.user_id, game),
        enabled: !!me && !!game,
        retry: false,
    });
}

export function useReviewLike(reviewId) {
    const { data: me } = useMe();
    return useQuery({
        queryKey: ['reviews', 'like', reviewId, me?.user_id],
        queryFn: () => hasLikedReview(reviewId, me),
        enabled: !!me && !!reviewId,
        retry: false,
    });
}

function useReviewMutation(mutationFn) {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn,
        onSuccess: () => Promise.all(['reviews', 'games', 'game', 'user'].map((key) =>
            queryClient.invalidateQueries({ queryKey: [key] })
        )),
    });
}

export function useCreateReview() { return useReviewMutation(createReview); }
export function useEditReview() { return useReviewMutation(editReview); }
export function useDeleteReview() { return useReviewMutation(deleteReview); }
export function useSetReviewLike() { return useReviewMutation(setReviewLike); }
