import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createReview, deleteReview, editReview, getCreatedReviews, getReview, getReviewLikes, getLikedReviews, likeReview, unlikeReview } from '../services/reviewService';
import { useMe } from './useAuth';

export function useCreatedReviews(userId) {
    const { data: me } = useMe();

    return useInfiniteQuery({
        queryKey: ['reviews', 'created', userId, me?.user_id],
        queryFn: ({pageParam}) => getCreatedReviews(userId, {cursor: pageParam}),
        initialPageParam: undefined,
        getNextPageParam: (page, pages, pageParam, pageParams) => {
            if (!page.next_url) return undefined;
            const cursor = new URL(page.next_url, window.location.origin).searchParams.get('cursor');
            return cursor && !pageParams.includes(cursor) ? cursor : undefined;
        },
        enabled: !!userId,
        retry: false,
    });
}

export function useReview(reviewId) {
    const { data: me } = useMe();

    return useQuery({
        queryKey: ['reviews', 'detail', reviewId, me?.user_id],
        queryFn: () => getReview(reviewId),
        enabled: !!reviewId,
        retry: false,
    });
}

export function useCreateReview() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: createReview,
        onSuccess: () => Promise.all([
            queryClient.invalidateQueries({queryKey: ['reviews']}),
            queryClient.invalidateQueries({queryKey: ['user']}),
        ]),
    });
}

export function useEditReview(reviewId) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (review) => editReview(reviewId, review),
        onSuccess: () => Promise.all([
            queryClient.invalidateQueries({queryKey: ['reviews']}),
            queryClient.invalidateQueries({queryKey: ['user']}),
        ]),
    });
}

export function useDeleteReview(reviewId) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => deleteReview(reviewId),
        onSuccess: () => Promise.all([
            queryClient.invalidateQueries({queryKey: ['reviews']}),
            queryClient.invalidateQueries({queryKey: ['user']}),
        ]),
    });
}

export function useLikeReview(reviewId) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => likeReview(reviewId),
        onSuccess: () => queryClient.invalidateQueries({queryKey: ['reviews']}),
    });
}

export function useUnlikeReview(reviewId) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () => unlikeReview(reviewId),
        onSuccess: () => queryClient.invalidateQueries({queryKey: ['reviews']}),
    });
}

export function useReviewLikes(reviewId, params = {}) {
    const { data: me } = useMe();

    return useQuery({
        queryKey: ['reviews', 'likes', reviewId, me?.user_id, params],
        queryFn: () => getReviewLikes(reviewId, params),
        enabled: !!reviewId,
        retry: false,
    });
}

export function useLikedReviews(params = {}) {
    const { data: me } = useMe();

    return useQuery({
        queryKey: ['reviews', 'liked', me?.user_id, params],
        queryFn: () => getLikedReviews(params),
        enabled: !!me,
        retry: false,
    });
}
