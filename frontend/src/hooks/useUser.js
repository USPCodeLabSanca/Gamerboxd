import { useState, useEffect } from "react";
import api from "../api/axios";

export function useUser(username) {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!username) return;
        
        setLoading(true);
        api.get(`/user/view/${username}`)
        .then((res) => setProfile(res.data))
        .catch((err) => setError(err.response?.data?.detail))
        .finally(() => setLoading(false));
    }, [username]);

    return {profile, loading, error};

}