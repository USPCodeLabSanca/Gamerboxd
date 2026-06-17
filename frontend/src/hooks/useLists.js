import { use, useContext, useState } from "react";
import api from "../api/axios";

export function useLists() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const createList = async (name, description, privada = false) => {
        setLoading(true);
        try {
            await api.post("/list/", {
                name, 
                description, 
                is_private: isPrivate
            })
        } catch (err) {
            setError(err.response?.data?.detail);
            throw err;
        } finally {
            setLoading(false);
        }
    }

    const getMyList = async (listName) => {
        const res = await api.get(`/list/${listName}`);
        return res.data;
    }

    const getUserList = async (creator, listName) => {
        const res = await api.get(`/list/${creator}/${listName}`);
        return res.data;
    }

    const addGame = async (listName, gameId) => {
        await api.post(`list/add/${listName}/${gameId}`);
    }

    const removeGame = async (listName, gameId) => {
        await api.post(`/list/rem/${listName}/${gameId}`);
    };

    const saveList = async (creator, listName) => {
        await api.post(`/list/save/${creator}/${listName}`);
    };

    return { createList, getMyList, getUserList, addGame, removeGame, saveList, loading, error };
    
}