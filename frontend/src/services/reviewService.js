import api from "../api/client";

export async function createReview({game_id, rating_num, rating_text, privacy, time_played, liked, completed}) {
    const res = await api.post("/reviews", {
        game_id: game_id,
        rating_num: rating_num,
        rating_text: rating_text,
        privacy: privacy,
        time_played: time_played,
        liked: liked,
        completed: completed,
    });
    return res.data;
}

export async function getReview(reviewId) {
    const res = await api.get(`/reviews/${reviewId}`);
    return res.data;
}

export async function editReview(reviewId, {rating_num, rating_text, privacy, time_played, liked, completed}) {
    const res = await api.put(`/reviews/${reviewId}`, {
        rating_num: rating_num,
        rating_text: rating_text,
        privacy: privacy,
        time_played: time_played,
        liked: liked,
        completed: completed,
    });
    return res.data;
}

export async function deleteReview(reviewId) {
    const res = await api.delete(`/reviews/${reviewId}`);
    return res.data;
}

export async function getCreatedReviews(userId, {pageSize, cursor, search, order} = {}) {
    const res = await api.get(`/reviews/created/${userId}`, {
        params: {
            page_size: pageSize,
            cursor: cursor,
            search: search,
            order: order,
        }
    });
    return res.data;
}

export async function likeReview(reviewId) {
    const res = await api.post(`/reviews/like/${reviewId}`);
    return res.data;
}

export async function unlikeReview(reviewId) {
    const res = await api.delete(`/reviews/like/${reviewId}`);
    return res.data;
}

export async function getReviewLikes(reviewId, {pageSize, cursor, search, order} = {}) {
    const res = await api.get(`/reviews/like/users/${reviewId}`, {
        params: {
            page_size: pageSize,
            cursor: cursor,
            search: search,
            order: order,
        }
    });
    return res.data;
}

export async function getLikedReviews({pageSize, cursor, search, order} = {}) {
    const res = await api.get("/reviews/like/reviews", {
        params: {
            page_size: pageSize,
            cursor: cursor,
            search: search,
            order: order,
        }
    });
    return res.data;
}
