import { createContext, useState, useEffect, useCallback } from "react";
import api from "../api/axios";

// Cria o contexto de autenticação
export const AuthContext = createContext();

export function AuthProvider({ children}) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Verifica se quando abre o site o usuário já está logado
    const checkAuth = useCallback(async () => {
        try {
            const response = await api.get("/user/");
            setUser(response.data);
        } catch {
            setUser(null);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        checkAuth();
    }, [checkAuth]);

    const login = async (emailOrUsername, senha) => {
        await api.post("/auth/login/", {
            email_or_username: emailOrUsername,
            password: senha,
        });
        await checkAuth();
    }

    const logout = async () => {
        await api.post("/auth/logout/");
        setUser(null);
    }

    const register = async (username, email, password) => {
        await api.post("/user/", { username, email, password});
        await login(email, password);
    }

    const value = {
        user, 
        loading, 
        login, 
        logout, 
        register,
        checkAuth,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    )
}