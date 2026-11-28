import api from '../api/client';

export async function getReview(reviewId) {
    const res = await api.get(`/reviews/${reviewId}`);
    return res.data;
}

export async function getUserReviews(userId, { nextUrl, search, pageSize = 10, order = '!created_at' } = {}) {
    const res = await api.get(nextUrl || `/reviews/created/${userId}`, nextUrl ? {} : {
        params: { search, page_size: pageSize, order },
    });
    return res.data;
}

export async function findUserGameReview(userId, game) {
    let nextUrl;
    do {
        const page = await getUserReviews(userId, { nextUrl, search: game.title, pageSize: 50 });
        const review = page.content.find((item) => item.game.game_id === game.id);
        if (review) return getReview(review.review_id);
        nextUrl = page.next_url;
    } while (nextUrl);
    return null;
}

export async function hasLikedReview(reviewId, user) {
    let nextUrl;
    do {
        const res = await api.get(nextUrl || `/reviews/like/users/${reviewId}`, nextUrl ? {} : {
            params: { search: user.username, page_size: 50 },
        });
        if (res.data.content.some((item) => item.user_id === user.user_id)) return true;
        nextUrl = res.data.next_url;
    } while (nextUrl);
    return false;
}

export async function createReview(review) {
    const res = await api.post('/reviews', review);
    return res.data;
}

export async function editReview({ reviewId, review }) {
    const res = await api.put(`/reviews/${reviewId}`, review);
    return res.data;
}

export async function deleteReview(reviewId) {
    const res = await api.delete(`/reviews/${reviewId}`);
    return res.data;
}

export async function setReviewLike({ reviewId, liked }) {
    const res = liked ? await api.post(`/reviews/like/${reviewId}`) : await api.delete(`/reviews/like/${reviewId}`);
    return res.data;
}
