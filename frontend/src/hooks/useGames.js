import { useState } from "react";
import api from "../api/axios";

export function useGames() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const search = async (term, page = 1) => {
    if (!term.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.get(`/game/${term}`, {
        params: { page, page_size: 20 },
      });
      setResults(res.data.games);
    } catch (err) {
      setError(err.response?.data?.detail);
    } finally {
      setLoading(false);
    }
  };

  return { results, loading, error, search };
}