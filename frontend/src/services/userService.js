import api from "../api/client";

export async function register(username, email, password) {
    const res = await api.post("/users", {
        username: username,
        email: email,
        password: password,
    });

    return res.data     // { message, user_id }
}