import api from "../api/client";

export async function login(email_or_username, password){
    const res = await api.post("/auth/login", {
        email_or_username: email_or_username,
        password: password,
    });

    return res.data;    // { message, user_id}
}

export async function logout(){
    const res = await api.delete("/auth/login");

    return res.data;    // {message}
}

export async function get_me(){
    try {
        const res = await api.get("/auth/me");
        return res.data;
    } catch (error) {
        if (error.response?.status === 401) return null; // Apenas verifica que não está logado
        throw error;
    }
}