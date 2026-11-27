import api from "../api/client";

export async function register(username, email, password) {
    const res = await api.post("/users", {
        username: username,
        email: email,
        password: password,
    });

    return res.data;     // { message, user_id }
}

export async function getUser (userId) {
    const res = await api.get(`/users/${userId}`);

    return res.data;        // Schema USER_FULL
}

export async function editProfile ({username, email, pfp, banner, bio}) {
    const res = await api.put("/users", {
        username: username,
        email: email,
        pfp: pfp,
        banner: banner,
        bio: bio,
    });

    return res.data;    // Schema USER_FULL
}

export async function deleteProfile () {
    const res = await api.delete("/users");

    return res.data;    // { message }
}

export async function followUser (userId) {
    const res = await api.post(`/users/follow/${userId}`);

    return res.data;    // { message }
}

export async function unfollowUser (userId) {
    const res = await api.delete(`/users/follow/${userId}`);

    return res.data;    // { message }
}

export async function getFollowers (userId, {pageSize, cursor, search, order} = {}) {
    const res = await api.get(`/users/follow/followers/${userId}`, {
        params: {
            page_size: pageSize,
            cursor: cursor,
            search: search,
            order: order,
        }
    });

    return res.data;    // Schema PAGE_RESULT com lista de schemas USER
}

export async function getFollowings (userId, {pageSize, cursor, search, order} = {}) {
    const res = await api.get(`/users/follow/followings/${userId}`, {
        params: {
            page_size: pageSize,
            cursor: cursor,
            search: search,
            order: order,
        }
    });

    return res.data;    // Schema PAGE_RESULT com lista de schemas USER
}

export async function blockUser (userId) {
    const res = await api.post(`/users/block/${userId}`);

    return res.data;
}

export async function unblockUser (userId) {
    const res = await api.delete(`/users/block/${userId}`);

    return res.data;
}

export async function getBlocks ({pageSize, cursor, search, order} = {}) {
    const res = await api.get(`/users/block`, {
        params: {
            page_size: pageSize,
            cursor: cursor,
            search: search,
            order: order,
        }
    });

    return res.data;
}