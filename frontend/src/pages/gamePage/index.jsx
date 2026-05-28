import React, { useState, useEffect} from "react";
import { useParams } from "react-router-dom";

import Card from "../../components/gameCard";

import gtaImg from "../../assets/imgs/gta.png";
import gowImg from "../../assets/imgs/ragnarok.png";
import silksongImg from "../../assets/imgs/silksong.png";
import rdr2Img from "../../assets/imgs/rdr2.jpg";
import cyberpunkImg from "../../assets/imgs/cyberpunk2077.png";
import clairImg from "../../assets/imgs/clair-obscure.png";

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

export default function GamePage() {

  const { id } = useParams();
  const [game, setGame] = useState(null);
  const [reviews, setReviews] = useState([]);

  useEffect(() => {
    
    const foundGame = mockGames.find(g => g.id === Number(id));
    setGame(foundGame);

    const foundReviews = mockReviews.filter(r => r.gameId === Number(id));
    setReviews(foundReviews);
  }, [id])

  if (!game) return (
    <div className="bg-linear-to-b from-cinza to-black min-h-screen flex items-center justify-center">
      <p className="text-white text-4xl">Carregando...</p>
    </div>
  )

  return (
    <div className="h-screen bg-linear-to-b from-cinza to-black pt-28 pl-20 pr-20">
      <div className="flex flex-row gap-4 h-[50%] relative">
            <div className="w-[20%]">
                <Card game={game} status={true} />
            </div>
            <div className="flex flex-col gap-4">
                <h1 className="text-white text-5xl font-bold z-50">Nome do jogo</h1>
                <p className="text-white">Sinopse</p>
            </div>
            <div className="absolute right-50 top-5 h-full w-[60%] overflow-hidden z-5">
                <img src={game.url} alt={game.title} className="h-full w-full object-cover opacity-80 mask-x-from-70% mask-x-to-100% mask-y-from-70% mask-y-to-100%" />
            </div>
      </div>
    </div>
  );
}