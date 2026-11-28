import assert from 'node:assert/strict';
import { randomBytes } from 'node:crypto';
import { mkdir } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { test } from 'node:test';
import { pathToFileURL } from 'node:url';

const { chromium } = await import(process.env.PLAYWRIGHT_MODULE ? pathToFileURL(process.env.PLAYWRIGHT_MODULE).href : 'playwright-core');
const apiUrl = process.env.REVIEW_API_URL ?? 'http://localhost:8000';
const frontUrl = process.env.REVIEW_FRONT_URL ?? 'http://localhost:5173';
const screenshots = process.env.REVIEW_SCREENSHOT_DIR ?? path.join(os.tmpdir(), 'gamerboxd-rating-browser');

test('seleciona e persiste meias notas no Chrome, na criação, edição e perfil', { timeout: 120_000 }, async () => {
    const browser = await chromium.launch({
        executablePath: process.env.CHROME_PATH ?? 'C:/Program Files/Google/Chrome/Application/chrome.exe',
        headless: true,
    });
    const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, locale: 'pt-BR' });
    await context.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: frontUrl });
    const page = await context.newPage();
    let userId;
    let reviewId;
    const likeRequests = [];
    page.on('request', (request) => {
        if (new URL(request.url()).pathname === `/reviews/like/${reviewId}` && ['POST', 'DELETE'].includes(request.method())) {
            likeRequests.push(request.method());
        }
    });
    const draft = 'Uma aventura de exploração com muitos caminhos e detalhes para descobrir. '.repeat(3).slice(0, 210) + ' ' + 'exploracao'.repeat(8);
    let expectedFields = { liked: true, completed: true, time_played: 12, privacy: 40 };

    async function api(method, endpoint, data) {
        const cookies = await context.cookies(apiUrl);
        let response;
        try {
            response = await context.request.fetch(`${apiUrl}${endpoint}`, {
                method,
                data,
                headers: { Cookie: cookies.map((cookie) => `${cookie.name}=${cookie.value}`).join('; ') },
            });
        } catch {
            throw new Error(`${method} ${endpoint}: não foi possível conectar à API`);
        }
        assert.equal(response.status(), 200, `${method} ${endpoint}: ${response.status()} ${await response.text()}`);
        return response.json();
    }

    async function assertFill(scope, expected) {
        const clips = await scope.locator('img[style*="clip-path"]').evaluateAll((images) =>
            images.map((image) => Number(image.style.clipPath.match(/ (\d+)%/)[1]))
        );
        assert.deepEqual(clips, expected);
    }

    async function assertLike(liked, count) {
        const label = liked ? 'Descurtir review' : 'Curtir review';
        await page.locator(`button[aria-label="${label}"]:enabled`).waitFor();
        const button = page.getByRole('button', { name: label, exact: true });
        assert.equal(await button.getAttribute('aria-pressed'), String(liked));
        assert.equal(await button.locator('svg').getAttribute('fill'), liked ? 'currentColor' : 'none');
        assert.equal((await button.locator('[aria-live]').textContent()).trim(), `${count} ${count === 1 ? 'curtida' : 'curtidas'}`);
        const saved = await api('GET', `/reviews/${reviewId}`);
        assert.equal(saved.like_count, count);
        return button;
    }

    async function save(method, expectedRating) {
        const responsePromise = page.waitForResponse((response) =>
            new URL(response.url()).pathname === (method === 'POST' ? '/reviews' : `/reviews/${reviewId}`)
            && response.request().method() === method
        );
        await page.getByRole('button', { name: 'Salvar review', exact: true }).click();
        const response = await responsePromise;
        assert.equal(response.status(), 200, `${method} /reviews: ${response.status()}`);
        const payload = response.request().postDataJSON();
        assert.equal(typeof payload.rating_num, 'number');
        assert.equal(payload.rating_num, expectedRating);
        assert.deepEqual(Object.keys(payload).sort(), ['completed', 'liked', 'privacy', 'rating_num', 'rating_text', 'time_played', ...(method === 'POST' ? ['game_id'] : [])].sort());
        for (const [field, value] of Object.entries(expectedFields)) assert.equal(payload[field], value);
        assert.equal(payload.rating_text, draft);
        const body = await response.json();
        if (method === 'POST') reviewId = body.review_id;
        await page.getByRole('dialog').waitFor({ state: 'hidden' });
        const persisted = await api('GET', `/reviews/${reviewId}`);
        assert.equal(persisted.rating_num, expectedRating);
        for (const [field, value] of Object.entries(expectedFields)) assert.equal(persisted[field], value);
        assert.equal(persisted.rating_text, draft);
        console.info(JSON.stringify({ method, status: response.status(), rating_num: payload.rating_num, payloadType: typeof payload.rating_num }));
    }

    async function assertMobile(dialog, name) {
        for (const [width, height] of [[390, 844], [320, 568]]) {
            await page.setViewportSize({ width, height });
            const bounds = await dialog.boundingBox();
            assert.ok(bounds.x >= 0 && bounds.x + bounds.width <= width, 'Modal deve caber na largura da tela');
            assert.ok(bounds.y >= 0 && bounds.y + bounds.height <= height, 'Modal deve caber na altura da tela');
            assert.equal(await dialog.evaluate((element) => element.scrollWidth <= element.clientWidth), true, 'Modal não deve ter rolagem horizontal');
            await dialog.getByLabel('Review', { exact: true }).scrollIntoViewIfNeeded();
            assert.equal(await dialog.getByLabel('Review', { exact: true }).inputValue(), draft);
            await dialog.screenshot({ path: path.join(screenshots, `${name}-${width}-texto.png`) });
            await dialog.getByRole('button', { name: 'Salvar review', exact: true }).scrollIntoViewIfNeeded();
            const saveBounds = await dialog.getByRole('button', { name: 'Salvar review', exact: true }).boundingBox();
            assert.ok(saveBounds.y >= 0 && saveBounds.y + saveBounds.height <= height, 'Botão Salvar deve ser alcançável');
            await dialog.screenshot({ path: path.join(screenshots, `${name}-${width}-acoes.png`) });
        }
        await page.setViewportSize({ width: 1440, height: 1100 });
    }

    async function assertCardPresentation(name, gameId) {
        const card = page.getByRole('article');
        const author = card.locator(`a[href="/profile/${userId}"]`);
        assert.ok((await author.innerText()).startsWith('por '));
        assert.equal(await author.locator('img').count(), 0);
        for (const [width, height] of [[1440, 1100], [390, 844], [320, 568]]) {
            await page.setViewportSize({ width, height });
            await card.scrollIntoViewIfNeeded();
            assert.equal(await card.evaluate((element) => element.scrollWidth <= element.clientWidth), true, 'Card não deve ter rolagem horizontal');
            const bounds = await card.boundingBox();
            assert.ok(bounds.x >= 0 && bounds.x + bounds.width <= width + 1, 'Card deve caber na largura da tela');
            for (const label of ['Curtir review', 'Compartilhar', 'Editar', 'Excluir']) {
                const box = await card.getByRole('button', { name: label, exact: true }).boundingBox();
                assert.ok(box.width >= 44 && box.height >= 44, `${label} deve ter área de clique confortável`);
            }
            await card.screenshot({ path: path.join(screenshots, `${name}-${width}.png`) });
        }
        await page.setViewportSize({ width: 1440, height: 1100 });
        const share = card.getByRole('button', { name: 'Compartilhar', exact: true });
        await share.scrollIntoViewIfNeeded();
        const before = await card.boundingBox();
        await share.click();
        const status = card.getByRole('status');
        await status.waitFor();
        assert.equal(await status.innerText(), 'Link copiado!');
        assert.equal(await page.evaluate(() => navigator.clipboard.readText()), `${frontUrl}/games/${gameId}?review=${reviewId}`);
        assert.deepEqual(await card.boundingBox(), before, 'Aviso de cópia não deve deslocar o card');
        const shareBox = await share.boundingBox();
        const statusBox = await status.boundingBox();
        assert.ok(Math.abs(shareBox.x + shareBox.width / 2 - statusBox.x - statusBox.width / 2) < 2);
        assert.ok(shareBox.y - statusBox.y - statusBox.height >= 0 && shareBox.y - statusBox.y - statusBox.height <= 16);
        await card.screenshot({ path: path.join(screenshots, `${name}-copiado.png`) });
        await status.waitFor({ state: 'hidden', timeout: 5000 });
        assert.deepEqual(await card.boundingBox(), before);
        await share.focus();
        await page.keyboard.press('Tab');
        assert.equal(await card.getByRole('button', { name: 'Editar', exact: true }).evaluate((element) => element === document.activeElement), true);
        await card.getByRole('button', { name: 'Excluir', exact: true }).click();
        await card.getByRole('button', { name: 'Cancelar', exact: true }).click();
        assert.equal(await card.getByRole('button', { name: 'Confirmar exclusão', exact: true }).count(), 0);
    }

    try {
        await mkdir(screenshots, { recursive: true });
        const suffix = Date.now().toString(36);
        const account = await api('POST', '/users', {
            username: `ratingtest${suffix}`,
            email: `ratingtest${suffix}@gmail.com`,
            password: `${randomBytes(16).toString('hex')}Aa1!`,
        });
        userId = account.user_id;
        const catalog = await api('GET', '/games?search=Minecraft&detail=true&page_size=1');
        assert.ok(catalog.games.length > 0, 'Minecraft deve existir no catálogo real');
        const gameId = catalog.games[0].game_id;

        await page.goto(`${frontUrl}/games/${gameId}`);
        await page.getByRole('button', { name: 'AVALIE', exact: true }).click();
        let dialog = page.getByRole('dialog', { name: 'Criar review' });
        await dialog.waitFor();
        assert.equal(await dialog.getByText('Cada metade vale 0,5. Use as setas para ajustar.', { exact: true }).count(), 0);
        assert.equal(await dialog.getByRole('radio', { name: '0 de 5', exact: true }).isChecked(), true);
        assert.equal(await dialog.getByRole('spinbutton').count(), 1);
        for (const note of ['0,5', '5', '0']) {
            const option = dialog.getByRole('radio', { name: `${note} de 5`, exact: true });
            await option.click();
            assert.equal(await option.isChecked(), true);
        }
        await dialog.getByRole('radio', { name: '2,5 de 5', exact: true }).click();
        await dialog.getByLabel('Review', { exact: true }).fill(draft);
        await dialog.getByText('Gostei', { exact: true }).click();
        const complete = dialog.getByRole('checkbox', { name: 'Completei o jogo', exact: true });
        await complete.focus();
        await page.keyboard.press('Space');
        assert.equal(await complete.isChecked(), true);
        await dialog.getByLabel('Tempo jogado (horas)').fill('12');
        await dialog.getByLabel('Privacidade').selectOption('40');
        assert.equal(await dialog.getByLabel('Review', { exact: true }).inputValue(), draft);
        assert.equal(await dialog.getByRole('button', { name: 'Jogou', exact: true }).count(), 0);
        await assertFill(dialog.getByRole('radiogroup', { name: 'Nota', exact: true }), [0, 0, 50, 100, 100]);
        await dialog.screenshot({ path: path.join(screenshots, 'criacao-2-5.png') });
        await assertMobile(dialog, 'criacao');
        await dialog.getByRole('button', { name: 'Salvar review' }).focus();
        await page.keyboard.press('Tab');
        assert.equal(await dialog.getByRole('button', { name: 'Fechar' }).evaluate((element) => element === document.activeElement), true);
        await page.keyboard.press('Shift+Tab');
        assert.equal(await dialog.getByRole('button', { name: 'Salvar review' }).evaluate((element) => element === document.activeElement), true);
        await save('POST', 2.5);

        await page.reload();
        let display = page.getByRole('img', { name: 'Nota: 2,5 de 5', exact: true });
        await display.waitFor();
        await assertFill(display, [0, 0, 50, 100, 100]);
        const likeButton = await assertLike(false, 0);
        const cardText = await page.getByRole('article').innerText();
        assert.doesNotMatch(cardText, /Curtiu o jogo|Completado|·/);
        assert.ok(cardText.includes('12 horas jogadas'));
        assert.equal((await api('GET', `/reviews/${reviewId}`)).completed, true);
        await page.getByRole('article').screenshot({ path: path.join(screenshots, 'review-zero-curtidas.png') });
        await assertCardPresentation('card-jogo', gameId);
        const likedResponse = page.waitForResponse((response) => new URL(response.url()).pathname === `/reviews/like/${reviewId}` && response.request().method() === 'POST');
        await likeButton.evaluate((button) => { button.click(); button.click(); });
        assert.equal((await likedResponse).status(), 200);
        await assertLike(true, 1);
        assert.deepEqual(likeRequests, ['POST']);
        assert.equal((await api('GET', `/reviews/${reviewId}`)).liked, true);
        await page.reload();
        await assertLike(true, 1);
        await page.getByRole('article').screenshot({ path: path.join(screenshots, 'review-uma-curtida.png') });
        const unlikedResponse = page.waitForResponse((response) => new URL(response.url()).pathname === `/reviews/like/${reviewId}` && response.request().method() === 'DELETE');
        await page.getByRole('button', { name: 'Descurtir review', exact: true }).click();
        assert.equal((await unlikedResponse).status(), 200);
        await assertLike(false, 0);
        await page.reload();
        await assertLike(false, 0);
        assert.deepEqual(likeRequests, ['POST', 'DELETE']);
        assert.equal(await page.getByText('A API não oferece uma listagem de reviews de outros usuários por jogo.', { exact: true }).count(), 0);
        await page.goto(`${frontUrl}/profile/${userId}`);
        await page.getByRole('img', { name: 'Nota: 2,5 de 5', exact: true }).waitFor();
        const profileText = await page.getByRole('article').innerText();
        assert.doesNotMatch(profileText, /Curtiu o jogo|Completado|·/);
        assert.ok(profileText.includes('12 horas jogadas'));
        await assertLike(false, 0);
        await page.getByRole('article').screenshot({ path: path.join(screenshots, 'review-perfil-2-5.png') });
        await assertCardPresentation('card-perfil', gameId);
        await page.goto(`${frontUrl}/games/${gameId}?review=${reviewId}`);
        await assertLike(false, 0);
        await page.getByRole('button', { name: 'Editar', exact: true }).click();
        dialog = page.getByRole('dialog', { name: 'Editar review' });
        const savedOption = dialog.getByRole('radio', { name: '2,5 de 5', exact: true });
        assert.equal(await savedOption.isChecked(), true);
        assert.equal(await dialog.getByRole('checkbox', { name: 'Completei o jogo' }).isChecked(), true);
        assert.equal(await dialog.getByRole('checkbox', { name: 'Curti o jogo' }).isChecked(), true);
        assert.equal(await dialog.getByLabel('Tempo jogado (horas)').inputValue(), '12');
        assert.equal(await dialog.getByLabel('Privacidade').inputValue(), '40');
        await dialog.screenshot({ path: path.join(screenshots, 'edicao-2-5.png') });
        await savedOption.focus();
        await page.keyboard.press('ArrowRight');
        assert.equal(await dialog.getByRole('radio', { name: '3 de 5', exact: true }).isChecked(), true);
        await page.keyboard.press('ArrowRight');
        assert.equal(await dialog.getByRole('radio', { name: '3,5 de 5', exact: true }).isChecked(), true);
        await page.keyboard.press('ArrowLeft');
        assert.equal(await dialog.getByRole('radio', { name: '3 de 5', exact: true }).isChecked(), true);
        await page.keyboard.press('ArrowRight');
        await dialog.getByText('Completado', { exact: true }).click();
        await dialog.getByText('Gostei', { exact: true }).click();
        await dialog.getByLabel('Tempo jogado (horas)').fill('18');
        await dialog.getByLabel('Privacidade').selectOption('0');
        expectedFields = { liked: false, completed: false, time_played: 18, privacy: 0 };
        assert.equal(await dialog.getByLabel('Review', { exact: true }).inputValue(), draft);
        await assertFill(dialog.getByRole('radiogroup', { name: 'Nota', exact: true }), [0, 0, 0, 50, 100]);
        await dialog.screenshot({ path: path.join(screenshots, 'edicao-3-5.png') });
        await assertMobile(dialog, 'edicao');
        await save('PUT', 3.5);

        await page.reload();
        display = page.getByRole('img', { name: 'Nota: 3,5 de 5', exact: true });
        await display.waitFor();
        await assertFill(display, [0, 0, 0, 50, 100]);
        await page.getByRole('article').screenshot({ path: path.join(screenshots, 'review-jogo-3-5.png') });
        const guest = await browser.newContext();
        try {
            const guestPage = await guest.newPage();
            let guestLikeRequests = 0;
            guestPage.on('request', (request) => {
                if (new URL(request.url()).pathname === `/reviews/like/${reviewId}` && request.method() === 'POST') guestLikeRequests++;
            });
            await guestPage.goto(`${frontUrl}/games/${gameId}?review=${reviewId}`);
            await guestPage.getByRole('button', { name: 'Curtir review', exact: true }).click();
            await guestPage.waitForURL(`${frontUrl}/login`);
            assert.equal(guestLikeRequests, 0);
        } finally {
            await guest.close();
        }
        await page.goto(`${frontUrl}/profile/${userId}`);
        display = page.getByRole('img', { name: 'Nota: 3,5 de 5', exact: true });
        await display.waitFor();
        await assertFill(display, [0, 0, 0, 50, 100]);
        await page.getByRole('article').screenshot({ path: path.join(screenshots, 'review-perfil-3-5.png') });
        await page.getByRole('button', { name: 'Editar', exact: true }).click();
        dialog = page.getByRole('dialog', { name: 'Editar review' });
        assert.equal(await dialog.getByRole('radio', { name: '3,5 de 5', exact: true }).isChecked(), true);
        await dialog.getByRole('radio', { name: '5 de 5', exact: true }).click();
        await save('PUT', 5);
        await page.getByRole('img', { name: 'Nota: 5 de 5', exact: true }).waitFor();
        await page.getByRole('button', { name: 'Excluir', exact: true }).click();
        const deleteResponse = page.waitForResponse((response) => new URL(response.url()).pathname === `/reviews/${reviewId}` && response.request().method() === 'DELETE');
        await page.getByRole('button', { name: 'Confirmar exclusão', exact: true }).click();
        assert.equal((await deleteResponse).status(), 200);
        await page.getByRole('article').waitFor({ state: 'hidden' });
        assert.equal((await context.request.get(`${apiUrl}/reviews/${reviewId}`)).status(), 404);
        reviewId = null;
        console.info(JSON.stringify({ verified: ['mouse', 'teclado', 'criacao', 'edicao', 'recarga', 'perfil', 'curtidas-0-1-0', 'cliques-duplicados', 'login-visitante', 'compartilhar-e-aviso-temporario', 'card-responsivo-texto-longo', 'excluir-pelo-card'], screenshots }));
    } finally {
        try {
            try {
                if (reviewId) {
                    await api('DELETE', `/reviews/${reviewId}`);
                    const deleted = await context.request.get(`${apiUrl}/reviews/${reviewId}`);
                    assert.equal(deleted.status(), 404);
                }
            } finally {
                if (userId) await api('DELETE', '/users');
            }
        } finally {
            await browser.close();
        }
    }
});
