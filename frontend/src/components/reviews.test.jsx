import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import api from '../api/client';
import ReviewModal from './ReviewModal';
import Review from './gameReview';
import { useCreatedReviews } from '../hooks/useReviews';
import GamePage from '../pages/gamePage';
import RecentReviews from '../pages/profile/Sections/RecentReviews';

const game = { id: 2, title: 'Minecraft', url: '/cover.jpg', year: 2011 };
const review = {
    review_id: 'review-1',
    reviewer: { user_id: 'user-1', username: 'player', pfp: null },
    game: { game_id: game.id, title: game.title, picture: game.url, year: game.year },
    rating_num: 3.5,
    rating_text: 'Muito bom',
    time_played: 12,
    privacy: 40,
    completed: true,
    liked: false,
    like_count: 2,
    rel: 40,
};

function renderReview(component, initialEntries = ['/']) {
    const client = new QueryClient({defaultOptions: {queries: {retry: false}, mutations: {retry: false}}});
    return render(
        <QueryClientProvider client={client}>
            <MemoryRouter initialEntries={initialEntries}>{component}</MemoryRouter>
        </QueryClientProvider>
    );
}

afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
});

describe('Reviews', () => {
    it('sincroniza a página do jogo após criar e excluir a avaliação', async () => {
        let current = null;
        vi.spyOn(api, 'get').mockImplementation(async (url) => {
            if (url === '/auth/me') return {data: {user_id: 'user-1'}};
            if (url === '/reviews/review-1') return {data: current};
            if (url === '/reviews/created/user-1') return {data: {content: current ? [current] : [], total: current ? 1 : 0, next_url: null}};
            throw new Error(`Rota inesperada: ${url}`);
        });
        vi.spyOn(api, 'post').mockImplementation(async (_url, data) => {
            current = {...review, ...data};
            return {data: {review_id: current.review_id}};
        });
        vi.spyOn(api, 'delete').mockImplementation(async () => {
            current = null;
            return {data: {message: 'Review deletada com sucesso!'}};
        });
        vi.spyOn(window, 'confirm').mockReturnValue(true);
        renderReview(<Routes><Route path="/games/:id" element={<GamePage />} /></Routes>, [`/games/${game.id}`]);

        const evaluate = await screen.findByRole('button', {name: 'AVALIE'});
        await waitFor(() => expect(evaluate).toHaveAttribute('aria-busy', 'false'));
        fireEvent.click(evaluate);
        fireEvent.change(screen.getByPlaceholderText('Descreva sua aventura...'), {target: {value: 'Uma ótima aventura'}});
        fireEvent.click(screen.getByRole('button', {name: 'Enviar'}));

        await waitFor(() => expect(screen.queryByPlaceholderText('Descreva sua aventura...')).not.toBeInTheDocument());
        expect(await screen.findByText('Uma ótima aventura')).toBeInTheDocument();
        expect(screen.getByText('Avaliações populares da semana')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', {name: 'Excluir'}));

        await waitFor(() => expect(screen.queryByText('Uma ótima aventura')).not.toBeInTheDocument());
        expect(screen.queryByPlaceholderText('Descreva sua aventura...')).not.toBeInTheDocument();
    });

    it('mantém o texto após falha e fecha apenas depois de criar a review', async () => {
        const post = vi.spyOn(api, 'post').mockRejectedValueOnce({response: {status: 409, data: {message: 'Você já possui uma review desse jogo!'}}});
        const onClose = vi.fn();
        renderReview(<ReviewModal game={game} isOpen={true} onClose={onClose} />);

        fireEvent.change(screen.getByPlaceholderText('Descreva sua aventura...'), {target: {value: 'Gostei muito'}});
        fireEvent.change(screen.getByLabelText('Nota'), {target: {value: '4.5'}});
        fireEvent.click(screen.getByRole('button', {name: 'Enviar'}));

        expect(await screen.findByRole('alert')).toHaveTextContent('Você já possui uma review desse jogo!');
        expect(screen.getByPlaceholderText('Descreva sua aventura...')).toHaveValue('Gostei muito');
        expect(onClose).not.toHaveBeenCalled();

        post.mockResolvedValueOnce({data: {review_id: 'new-review'}});
        fireEvent.click(screen.getByRole('button', {name: 'Enviar'}));

        await waitFor(() => expect(onClose).toHaveBeenCalledTimes(1));
        expect(post).toHaveBeenLastCalledWith('/reviews', {
            game_id: game.id, rating_num: 4.5, rating_text: 'Gostei muito',
            liked: false, completed: false, privacy: 0, time_played: null,
        });
    });

    it('edita o texto preservando os demais campos e sem enviar game_id', async () => {
        const put = vi.spyOn(api, 'put').mockResolvedValue({data: review});
        const onClose = vi.fn();
        renderReview(<ReviewModal game={game} review={review} isOpen={true} onClose={onClose} />);

        fireEvent.change(screen.getByPlaceholderText('Descreva sua aventura...'), {target: {value: 'Novo texto'}});
        fireEvent.click(screen.getByRole('button', {name: 'Salvar'}));

        await waitFor(() => expect(onClose).toHaveBeenCalledTimes(1));
        expect(put).toHaveBeenCalledWith('/reviews/review-1', {
            rating_num: 3.5, rating_text: 'Novo texto', liked: false,
            completed: true, privacy: 40, time_played: 12,
        });
    });

    it('atualiza curtidas e remove a review da lista após excluir', async () => {
        let current = {...review};
        vi.spyOn(api, 'get').mockImplementation(async (url) => {
            if (url === '/auth/me') return {data: {user_id: 'user-1'}};
            return {data: {content: current ? [current] : [], total: current ? 1 : 0, next_url: null}};
        });
        const post = vi.spyOn(api, 'post').mockImplementation(async () => {
            current = {...current, rel: 90, like_count: 3};
            return {data: {message: 'Like adicionado com sucesso!'}};
        });
        const remove = vi.spyOn(api, 'delete').mockImplementation(async (url) => {
            current = url.includes('/like/') ? {...current, rel: 40, like_count: 2} : null;
            return {data: {message: 'Sucesso'}};
        });
        vi.spyOn(window, 'confirm').mockReturnValue(true);

        function Reviews() {
            const reviews = useCreatedReviews('user-1');
            return reviews.data?.pages[0].content.map((item) => <Review key={item.review_id} review={item} />);
        }

        renderReview(<Reviews />);
        const like = await screen.findByRole('button', {name: 'Curtir review'});
        await waitFor(() => expect(like).toBeEnabled());
        fireEvent.click(like);
        const unlike = await screen.findByRole('button', {name: 'Remover curtida'});
        expect(unlike).toHaveTextContent('3');
        expect(post).toHaveBeenCalledWith('/reviews/like/review-1');

        await waitFor(() => expect(unlike).toBeEnabled());
        fireEvent.click(unlike);
        expect(await screen.findByRole('button', {name: 'Curtir review'})).toHaveTextContent('2');
        expect(remove).toHaveBeenCalledWith('/reviews/like/review-1');

        const deleteButton = screen.getByRole('button', {name: 'Excluir'});
        await waitFor(() => expect(deleteButton).toBeEnabled());
        fireEvent.click(deleteButton);
        await waitFor(() => expect(screen.queryByText('Muito bom')).not.toBeInTheDocument());
        expect(remove).toHaveBeenCalledWith('/reviews/review-1');
    });

    it.each([
        'http://localhost:8000/reviews/created/user-1?cursor=next-cursor',
        '/reviews/created/user-1?cursor=next-cursor',
        '?cursor=next-cursor',
    ])('carrega a próxima página do perfil ao clicar em Mostrar mais: %s', async (nextUrl) => {
        const nextReview = {...review, review_id: 'review-2', rating_text: 'Segunda avaliação'};
        const get = vi.spyOn(api, 'get').mockImplementation(async (url, config) => {
            if (url === '/auth/me') return {data: {user_id: 'user-1'}};
            const nextPage = config.params.cursor === 'next-cursor';
            return {data: {
                content: nextPage ? [nextReview] : [review],
                total: 2,
                next_url: nextPage ? null : nextUrl,
            }};
        });
        renderReview(<Routes><Route path="/profile/:user_id" element={<RecentReviews />} /></Routes>, ['/profile/user-1']);

        expect(await screen.findByText('Muito bom')).toBeInTheDocument();
        expect(screen.queryByText('Segunda avaliação')).not.toBeInTheDocument();
        expect(get.mock.calls.filter(([url]) => url === '/reviews/created/user-1').every(([, config]) => config.params.cursor === undefined)).toBe(true);

        fireEvent.click(screen.getByRole('button', {name: 'Mostrar mais'}));
        expect(await screen.findByText('Segunda avaliação')).toBeInTheDocument();
        expect(screen.getByText('Muito bom')).toBeInTheDocument();
        expect(get).toHaveBeenCalledWith('/reviews/created/user-1', {params: {
            page_size: undefined, cursor: 'next-cursor', search: undefined, order: undefined,
        }});
        expect(screen.queryByRole('button', {name: 'Mostrar mais'})).not.toBeInTheDocument();
    });

    it('reencontra a review ao reabrir a página com cache vazio e usa edição', async () => {
        let current = {...review};
        vi.spyOn(api, 'get').mockImplementation(async (url) => {
            if (url === '/auth/me') return {data: {user_id: 'user-1'}};
            if (url === '/reviews/review-1') return {data: {...current, rel: null}};
            return {data: {content: [current], total: 1, next_url: null}};
        });
        const post = vi.spyOn(api, 'post');
        const put = vi.spyOn(api, 'put').mockImplementation(async (_url, data) => {
            current = {...current, ...data};
            return {data: current};
        });
        const page = <Routes><Route path="/games/:id" element={<GamePage />} /></Routes>;
        const firstRender = renderReview(page, ['/games/2']);

        expect(await screen.findByText('Muito bom')).toBeInTheDocument();
        const evaluate = await screen.findByRole('button', {name: 'AVALIE'});
        await waitFor(() => expect(evaluate).toHaveAttribute('aria-busy', 'false'));
        fireEvent.click(evaluate);
        expect(screen.getByPlaceholderText('Descreva sua aventura...')).toHaveValue('Muito bom');
        fireEvent.change(screen.getByPlaceholderText('Descreva sua aventura...'), {target: {value: 'Review editada'}});
        fireEvent.click(screen.getByRole('button', {name: 'Salvar'}));
        await waitFor(() => expect(screen.queryByPlaceholderText('Descreva sua aventura...')).not.toBeInTheDocument());
        expect(put).toHaveBeenCalledWith('/reviews/review-1', {
            rating_num: 3.5, rating_text: 'Review editada', liked: false,
            completed: true, privacy: 40, time_played: 12,
        });

        firstRender.unmount();
        renderReview(page, ['/games/2']);
        expect(await screen.findByText('Review editada')).toBeInTheDocument();
        const evaluateAgain = screen.getByRole('button', {name: 'AVALIE'});
        await waitFor(() => expect(evaluateAgain).toHaveAttribute('aria-busy', 'false'));
        fireEvent.click(evaluateAgain);
        expect(screen.getByRole('button', {name: 'Salvar'})).toBeInTheDocument();
        expect(screen.getByPlaceholderText('Descreva sua aventura...')).toHaveValue('Review editada');
        expect(post).not.toHaveBeenCalled();
    });

    it('bloqueia criação até consultar a página que contém a review existente', async () => {
        const get = vi.spyOn(api, 'get').mockImplementation(async (url, config) => {
            if (url === '/auth/me') return {data: {user_id: 'user-1'}};
            if (url === '/reviews/review-1') return {data: review};
            const nextPage = config.params.cursor === 'next-cursor';
            return {data: {
                content: nextPage ? [review] : [], total: 1,
                next_url: nextPage ? null : '/reviews/created/user-1?cursor=next-cursor',
            }};
        });
        const post = vi.spyOn(api, 'post');
        renderReview(<Routes><Route path="/games/:id" element={<GamePage />} /></Routes>, ['/games/2']);

        const nextPage = await screen.findByRole('button', {name: 'Consultar próximas avaliações'});
        fireEvent.click(screen.getByRole('button', {name: 'AVALIE'}));
        expect(screen.getByText('Consulte as próximas avaliações abaixo antes de criar uma nova.')).toBeInTheDocument();
        expect(screen.queryByPlaceholderText('Descreva sua aventura...')).not.toBeInTheDocument();
        expect(get.mock.calls.some(([, config]) => config?.params?.cursor === 'next-cursor')).toBe(false);
        fireEvent.click(nextPage);
        expect(await screen.findByText('Muito bom')).toBeInTheDocument();
        const evaluate = await screen.findByRole('button', {name: 'AVALIE'});
        await waitFor(() => expect(evaluate).toHaveAttribute('aria-busy', 'false'));
        fireEvent.click(evaluate);
        expect(screen.getByRole('button', {name: 'Salvar'})).toBeInTheDocument();
        expect(post).not.toHaveBeenCalled();
    });

    it('remove Mostrar mais quando a próxima URL repete um cursor já consultado', async () => {
        const nextReview = {...review, review_id: 'review-2', rating_text: 'Segunda avaliação'};
        const get = vi.spyOn(api, 'get').mockImplementation(async (url, config) => {
            if (url === '/auth/me') return {data: {user_id: 'user-1'}};
            return {data: {
                content: config.params.cursor ? [nextReview] : [review], total: 3,
                next_url: '/reviews/created/user-1?cursor=repeated-cursor',
            }};
        });
        renderReview(<Routes><Route path="/profile/:user_id" element={<RecentReviews />} /></Routes>, ['/profile/user-1']);

        fireEvent.click(await screen.findByRole('button', {name: 'Mostrar mais'}));
        expect(await screen.findByText('Segunda avaliação')).toBeInTheDocument();
        expect(screen.queryByRole('button', {name: 'Mostrar mais'})).not.toBeInTheDocument();
        expect(get.mock.calls.filter(([, config]) => config?.params?.cursor === 'repeated-cursor')).toHaveLength(1);
    });

    it('não libera criação quando um cursor repetido impede concluir a consulta', async () => {
        vi.spyOn(api, 'get').mockImplementation(async (url) => {
            if (url === '/auth/me') return {data: {user_id: 'user-1'}};
            return {data: {content: [], total: 1, next_url: '?cursor=repeated-cursor'}};
        });
        renderReview(<Routes><Route path="/games/:id" element={<GamePage />} /></Routes>, ['/games/2']);

        fireEvent.click(await screen.findByRole('button', {name: 'Consultar próximas avaliações'}));
        expect(await screen.findByRole('alert')).toHaveTextContent('Não foi possível concluir a consulta');
        fireEvent.click(screen.getByRole('button', {name: 'AVALIE'}));
        expect(screen.getByRole('button', {name: 'AVALIE'})).toHaveAttribute('aria-describedby', 'review-feedback');
        expect(screen.queryByPlaceholderText('Descreva sua aventura...')).not.toBeInTheDocument();
        expect(screen.queryByRole('button', {name: 'Consultar próximas avaliações'})).not.toBeInTheDocument();
    });

    it('informa a falha do servidor ao clicar em AVALIE sem abrir uma criação', async () => {
        vi.spyOn(api, 'get').mockImplementation(async (url) => {
            if (url === '/auth/me') return {data: {user_id: 'user-1'}};
            throw {response: {status: 500, data: {message: 'Erro interno'}}};
        });
        const post = vi.spyOn(api, 'post');
        renderReview(<Routes><Route path="/games/:id" element={<GamePage />} /></Routes>, ['/games/2']);

        await screen.findByRole('alert');
        fireEvent.click(screen.getByRole('button', {name: 'AVALIE'}));
        expect(screen.getByText('Não foi possível verificar sua avaliação no servidor. Tente novamente em instantes.')).toBeInTheDocument();
        expect(screen.getByRole('button', {name: 'AVALIE'})).toHaveAttribute('aria-describedby', 'review-feedback');
        expect(screen.queryByPlaceholderText('Descreva sua aventura...')).not.toBeInTheDocument();
        expect(post).not.toHaveBeenCalled();
    });

    it('encaminha para login ao clicar em AVALIE sem sessão', async () => {
        vi.spyOn(api, 'get').mockRejectedValue({response: {status: 401}});
        renderReview(<Routes>
            <Route path="/games/:id" element={<GamePage />} />
            <Route path="/login" element={<p>Entrar na conta</p>} />
        </Routes>, ['/games/2']);

        const evaluate = await screen.findByRole('button', {name: 'AVALIE'});
        await waitFor(() => expect(evaluate).toHaveAttribute('aria-busy', 'false'));
        fireEvent.click(evaluate);
        expect(await screen.findByText('Entrar na conta')).toBeInTheDocument();
    });
});
