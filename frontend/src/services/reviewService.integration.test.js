// @vitest-environment node
import { expect, it } from 'vitest';
import process from 'node:process';
import { appendFileSync } from 'node:fs';
import api from '../api/client';
import { register, deleteProfile } from './userService';
import { getGame, getAllGames } from './gameService';
import { createReview, deleteReview, editReview, findUserGameReview, getReview, getUserReviews, hasLikedReview, setReviewLike } from './reviewService';
import { sortGames } from '../utils/gameFilters';

const apiUrl = process.env.REVIEW_API_URL;

it.skipIf(!apiUrl)('persiste o ciclo de uma review e atualiza os agregados na API real', async () => {
    api.defaults.baseURL = apiUrl;
    api.defaults.adapter = 'http';
    api.defaults.timeout = 15_000;
    let catalogRequests = 0;
    const record = (entry) => {
        const line = JSON.stringify({ timestamp: new Date().toISOString(), ...entry });
        if (process.env.REVIEW_HTTP_LOG) appendFileSync(process.env.REVIEW_HTTP_LOG, `${line}\n`);
        console.info(line);
    };
    const recordResponse = (config, response, code) => {
        const path = api.getUri(config);
        const isCatalog = config.method === 'get' && config.url === '/games';
        if (isCatalog) catalogRequests++;
        const body = response?.data;
        const entry = { method: config.method.toUpperCase(), url: path, status: response?.status ?? null, code };
        if (process.env.REVIEW_HTTP_LOG) {
            appendFileSync(process.env.REVIEW_HTTP_LOG, `${JSON.stringify({ timestamp: new Date().toISOString(), ...entry, body })}\n`);
        }
        console.info(JSON.stringify({ ...entry, body: isCatalog && body?.games ? { total: body.total, count: body.count } : body }));
    };
    const cookies = new Map();
    const requestInterceptor = api.interceptors.request.use((config) => {
        config.headers.Cookie = [...cookies].map(([key, value]) => `${key}=${value}`).join('; ');
        return config;
    });
    const responseInterceptor = api.interceptors.response.use((response) => {
        recordResponse(response.config, response);
        for (const cookie of response.headers['set-cookie'] ?? []) {
            const [pair] = cookie.split(';');
            const separator = pair.indexOf('=');
            cookies.set(pair.slice(0, separator), pair.slice(separator + 1));
        }
        return response;
    }, (error) => {
        recordResponse(error.config, error.response, error.code);
        const response = error.response && { status: error.response.status, data: error.response.data };
        throw Object.assign(new Error(`${error.config.method.toUpperCase()} ${api.getUri(error.config)}: ${response?.status ?? error.code} ${JSON.stringify(response?.data ?? null)}`), { response, code: error.code });
    });
    let account;
    let reviewId;
    try {
        record({ event: 'start', apiUrl });
        const suffix = Date.now().toString(36);
        const username = `reviewtest${suffix}`;
        account = await register(username, `${username}@gmail.com`, `Review!${suffix}Aa9`);
        const catalog = await getAllGames();
        record({ event: 'catalog-loaded', total: catalog.length, getGamesRequests: catalogRequests });
        expect(catalog.length).toBeGreaterThan(0);
        const original = catalog.at(-1);
        const values = { game_id: original.game_id, rating_num: 3.5, rating_text: 'Review descartável de integração', privacy: 0, time_played: 2, liked: true, completed: true };
        ({ review_id: reviewId } = await createReview(values));
        const reloaded = await getReview(reviewId);
        const { game_id: gameId, ...edit } = values;
        expect(reloaded).toMatchObject(edit);
        expect(reloaded.game.game_id).toBe(gameId);
        expect(reloaded.reviewer.user_id).toBe(account.user_id);
        const assertListedReview = async (expected) => {
            const page = await getUserReviews(account.user_id);
            expect(page).toMatchObject({ total: 1, page_len: 1, next_url: null });
            expect(typeof page.current_url).toBe('string');
            expect(page.content).toHaveLength(1);
            const listed = page.content[0];
            expect(listed).toMatchObject({
                review_id: reviewId,
                reviewer: { user_id: account.user_id, username, pfp: null },
                game: reloaded.game,
                created_at: reloaded.created_at,
                privacy: 0,
                liked: true,
                ...expected,
            });
            expect(listed.created_at).toMatch(/^\d{2}\/\d{2}\/\d{4}$/);
            expect(Number.isInteger(listed.like_count)).toBe(true);
            expect(listed).not.toHaveProperty('creator');
            return listed;
        };
        await assertListedReview({ rating_num: 3.5, rating_text: values.rating_text, like_count: 0, rel: 40 });
        await assertListedReview({ rating_num: 3.5, like_count: 0, rel: 40 });
        const found = await findUserGameReview(account.user_id, { id: gameId, title: original.title });
        expect(found?.review_id).toBe(reviewId);
        await editReview({ reviewId, review: { ...edit, rating_num: 4, rating_text: 'Review editada' } });
        expect(await getReview(reviewId)).toMatchObject({ rating_num: 4, rating_text: 'Review editada' });
        await assertListedReview({ rating_num: 4, rating_text: 'Review editada', like_count: 0, rel: 40 });
        const current = await getGame(gameId);
        expect(current.review_count).toBe(original.review_count + 1);
        expect(current.like_count).toBe(original.like_count + 1);
        expect(current.completed_count).toBe(original.completed_count + 1);
        await setReviewLike({ reviewId, liked: true });
        expect((await getReview(reviewId)).like_count).toBe(1);
        expect(await hasLikedReview(reviewId, { username, user_id: account.user_id })).toBe(true);
        await assertListedReview({ like_count: 1, rel: 90 });
        await setReviewLike({ reviewId, liked: false });
        expect((await getReview(reviewId)).like_count).toBe(0);
        expect(await hasLikedReview(reviewId, { username, user_id: account.user_id })).toBe(false);
        await assertListedReview({ like_count: 0, rel: 40 });
        const previousCatalogRequests = catalogRequests;
        const updatedCatalog = await getAllGames();
        record({ event: 'catalog-reloaded', total: updatedCatalog.length, getGamesRequests: catalogRequests - previousCatalogRequests });
        for (const [sort, field] of [['rating:desc', 'gamerboxd_rating'], ['likes:desc', 'like_count'], ['reviews:desc', 'review_count'], ['completed:desc', 'completed_count']]) {
            const sorted = sortGames(updatedCatalog, sort);
            expect(sorted).toHaveLength(updatedCatalog.length);
            const numbers = sorted.map((game) => game[field]).filter((value) => value !== null);
            for (let index = 1; index < numbers.length; index++) expect(numbers[index - 1]).toBeGreaterThanOrEqual(numbers[index]);
            record({ event: 'filter-verified', sort, total: sorted.length, reviewedGameId: gameId, reviewedGamePosition: sorted.findIndex((game) => game.game_id === gameId) + 1 });
        }
        await deleteReview(reviewId);
        await expect(getReview(reviewId)).rejects.toMatchObject({ response: { status: 404 } });
        reviewId = null;
        expect(await getUserReviews(account.user_id)).toMatchObject({ total: 0, page_len: 0, content: [], next_url: null });
        expect(await getGame(gameId)).toMatchObject({ review_count: original.review_count, like_count: original.like_count, completed_count: original.completed_count, gamerboxd_rating: original.gamerboxd_rating });
    } finally {
        record({ event: 'cleanup', reviewId, userId: account?.user_id, getGamesRequests: catalogRequests });
        try {
            if (reviewId) {
                await deleteReview(reviewId);
                await expect(getReview(reviewId)).rejects.toMatchObject({ response: { status: 404 } });
            }
        } finally {
            try {
                if (account) await deleteProfile();
            } finally {
                api.interceptors.request.eject(requestInterceptor);
                api.interceptors.response.eject(responseInterceptor);
            }
        }
    }
}, 180_000);
