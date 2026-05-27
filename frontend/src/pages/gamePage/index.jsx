// ─── Imports ───────────────────────────────────────────────────────────────

import React, { useState, useEffect } from "react";
// useParams é o hook do React Router que lê os parâmetros da URL
// ex: na URL /games/3, ele te dá { id: "3" }
import { useParams } from "react-router-dom";

import Card from "../../components/gameCard";
import Review from "../../components/gameReview";

// Importa as mesmas imagens que você já usa no index.jsx
import gtaImg from "../../assets/imgs/gta.png";
import gowImg from "../../assets/imgs/ragnarok.png";
import silksongImg from "../../assets/imgs/silksong.png";
import rdr2Img from "../../assets/imgs/rdr2.jpg";
import cyberpunkImg from "../../assets/imgs/cyberpunk2077.png";
import clairImg from "../../assets/imgs/clair-obscure.png";

// ─── Mock data ─────────────────────────────────────────────────────────────

// Mesma lista do index.jsx — futuramente isso vira uma chamada de API
// Os ids aqui precisam bater com os ids que você passa no <Link to={`/games/${game.id}`}>
const mockGames = [
    { id: 1, title: "GTA VI",          url: gtaImg,      jogou: true, liked: true, nota: 5,   complete: true,  avgNota: 4.7, totalLikes: 4821, totalReviews: 312, genre: "Ação / Mundo Aberto",    year: 2025 },
    { id: 2, title: "God of War",      url: gowImg,      jogou: true, liked: true, nota: 5,   complete: true,  avgNota: 4.9, totalLikes: 6103, totalReviews: 540, genre: "Ação / Aventura",        year: 2022 },
    { id: 3, title: "God of War II",   url: rdr2Img,     jogou: true, liked: true, nota: 5,   complete: true,  avgNota: 4.8, totalLikes: 5200, totalReviews: 480, genre: "Ação / Aventura",        year: 2023 },
    { id: 4, title: "Silksong",        url: silksongImg, jogou: true, liked: true, nota: 4.5, complete: true,  avgNota: 4.5, totalLikes: 3900, totalReviews: 290, genre: "Metroidvania",           year: 2024 },
    { id: 5, title: "Expedition 33",   url: clairImg,    jogou: true, liked: true, nota: 4.5, complete: true,  avgNota: 4.6, totalLikes: 2800, totalReviews: 210, genre: "RPG / Aventura",         year: 2025 },
    { id: 6, title: "Cyberpunk 2077",  url: cyberpunkImg,jogou: true, liked: true, nota: 3.5, complete: false, avgNota: 4.1, totalLikes: 7200, totalReviews: 890, genre: "RPG / Mundo Aberto",     year: 2020 },
];

// Reviews mockados separados do jogo — futuramente virão de GET /games/:id/reviews
const mockReviews = [
    { id: 1, gameId: 1, complete: false, content: "Esse jogo é incrível! A história é envolvente e os gráficos são de tirar o fôlego. Recomendo para todos os fãs de jogos de ação.", author: { username: "Gamer123", avatar: "https://i.pravatar.cc/150?img=1" } },
    { id: 2, gameId: 1, complete: false, content: "Melhor jogo da geração, sem dúvida. O mapa é enorme e cada detalhe foi cuidado com carinho.", author: { username: "Player456", avatar: "https://i.pravatar.cc/150?img=2" } },
    { id: 3, gameId: 1, complete: true,  content: "Divertido, mas esperava mais em termos de inovação. Vale muito a pena mesmo assim.", author: { username: "GameLover789", avatar: "https://i.pravatar.cc/150?img=3" } },
];

// ─── Componente principal ──────────────────────────────────────────────────

export default function GamePage() {

    // useParams lê o :id da URL e retorna como string — ex: "3"
    const { id } = useParams();

    // Estado que vai guardar o jogo encontrado (ou null enquanto não acha)
    const [game, setGame] = useState(null);

    // Estado para os reviews desse jogo
    const [reviews, setReviews] = useState([]);

    // useEffect roda assim que o componente aparece na tela
    // O array [id] no final significa: "rode de novo se o id mudar"
    // (útil se o usuário navegar de /games/1 para /games/2 sem sair da página)
    useEffect(() => {

        // Number(id) converte a string "3" para o número 3
        // porque os ids no mockGames são números
        const foundGame = mockGames.find(g => g.id === Number(id));
        setGame(foundGame);

        // Filtra só os reviews que pertencem a esse jogo
        const foundReviews = mockReviews.filter(r => r.gameId === Number(id));
        setReviews(foundReviews);

        // ─── Quando tiver API, substitui os dois blocos acima por: ───
        // async function fetchData() {
        //     const [gameRes, reviewsRes] = await Promise.all([
        //         api.get(`/games/${id}`),
        //         api.get(`/games/${id}/reviews`)
        //     ]);
        //     setGame(gameRes.data);
        //     setReviews(reviewsRes.data);
        // }
        // fetchData();

    }, [id]); // ← dependência: roda novamente se o id mudar

    // Enquanto o jogo não foi encontrado ainda, mostra loading
    if (!game) return (
        <div className="bg-linear-to-b from-cinza to-black min-h-screen flex items-center justify-center">
            <p className="text-white text-xl">Carregando...</p>
        </div>
    );

    // ─── Render ────────────────────────────────────────────────────────────

    return (
        <div className="bg-linear-to-b from-cinza to-black min-h-screen pt-28 px-20 pb-20 text-white">

            {/* ── Seção hero: capa grande + informações principais ── */}
            <div className="flex flex-row gap-12 items-start mb-16">

                {/* Card da capa — reutiliza o componente que você já tem */}
                {/* status={true} mostra os ícones de jogou/liked/nota abaixo da capa */}
                <div className="w-[20%] shrink-0">
                    <Card game={game} status={true} />
                </div>

                {/* Coluna de infos */}
                <div className="flex flex-col gap-6 justify-start">

                    {/* Gênero e ano — dados que agora vivem no objeto game */}
                    <span className="text-roxo text-sm uppercase tracking-widest">
                        {game.genre} · {game.year}
                    </span>

                    <h1 className="text-6xl font-bold leading-tight">{game.title}</h1>

                    {/* Agregados globais — calculados pelo back, não pelo usuário */}
                    <div className="flex flex-row gap-8 mt-2">
                        <div className="flex flex-col">
                            <span className="text-white/50 text-xs uppercase tracking-widest">Nota média</span>
                            <span className="text-4xl font-bold text-roxo">{game.avgNota}</span>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-white/50 text-xs uppercase tracking-widest">Likes</span>
                            {/* toLocaleString formata o número com pontos: 4821 → "4.821" */}
                            <span className="text-4xl font-bold">{game.totalLikes.toLocaleString("pt-BR")}</span>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-white/50 text-xs uppercase tracking-widest">Reviews</span>
                            <span className="text-4xl font-bold">{game.totalReviews}</span>
                        </div>
                    </div>

                </div>
            </div>

            {/* ── Seção de reviews ── */}
            <div>
                {/* Cabeçalho da seção — mesmo estilo do index.jsx */}
                <div className="w-full border-b border-white flex flex-row items-center justify-between py-2 mb-6">
                    <p className="text-white text-sm">
                        {/* reviews.length mostra quantos reviews foram encontrados */}
                        Avaliações ({reviews.length})
                    </p>
                </div>

                {/* Se não tiver reviews, mostra uma mensagem em vez de lista vazia */}
                {reviews.length === 0 ? (
                    <p className="text-white/50">Nenhuma avaliação ainda.</p>
                ) : (
                    <div className="flex flex-col gap-6">
                        {/* Mapeia os reviews — reutiliza o componente Review que você já tem */}
                        {reviews.map((review) => (
                            // key={review.id} é obrigatório no React para listas — identifica cada item unicamente
                            <Review key={review.id} review={review} game={game} />
                        ))}
                    </div>
                )}
            </div>

        </div>
    );
}