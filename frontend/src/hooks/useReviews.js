import { useState } from "react";
import api from "../api/axios";

export function useReviews() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createReview = async ({ game, rating_num, rating_text, is_private, time_played, liked, completed }) => {
    setLoading(true);
    try {
      await api.post("/review/", { game, rating_num, rating_text, is_private, time_played, liked, completed });
    } catch (err) {
      setError(err.response?.data?.detail);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteReview = async (gameId) => {
    await api.delete(`/review/${gameId}`);
  };

  const likeReview = async (username, gameId) => {
    await api.post(`/review/like/${username}/${gameId}`);
  };

  const unlikeReview = async (username, gameId) => {
    await api.post(`/review/unlike/${username}/${gameId}`);
  };

  return { createReview, deleteReview, likeReview, unlikeReview, loading, error };
}