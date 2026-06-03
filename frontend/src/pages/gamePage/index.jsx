import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

import Card from "../../components/gameCard";
import Review from "../../components/gameReview";
import List from "../../components/List";

import gtaImg from "../../assets/imgs/gta.png";
import gowImg from "../../assets/imgs/ragnarok.png";
import silksongImg from "../../assets/imgs/silksong.png";
import rdr2Img from "../../assets/imgs/rdr2.jpg";
import cyberpunkImg from "../../assets/imgs/cyberpunk2077.png";
import clairImg from "../../assets/imgs/clair-obscure.png";

import list from "../../assets/icons/lista.svg";

const mockGames = [
  {
    id: 1,
    title: "GTA VI",
    url: gtaImg,
    jogou: true,
    liked: true,
    nota: 5,
    complete: true,
    avgNota: 4.7,
    totalLikes: 4821,
    totalReviews: 312,
    genre: "Ação / Mundo Aberto",
    year: 2025,
  },
  {
    id: 2,
    title: "God of War",
    url: gowImg,
    jogou: true,
    liked: true,
    nota: 5,
    complete: true,
    avgNota: 4.9,
    totalLikes: 6103,
    totalReviews: 540,
    genre: "Ação / Aventura",
    year: 2022,
  },
  {
    id: 3,
    title: "God of War II",
    url: rdr2Img,
    jogou: true,
    liked: true,
    nota: 5,
    complete: true,
    avgNota: 4.8,
    totalLikes: 5200,
    totalReviews: 480,
    genre: "Ação / Aventura",
    year: 2023,
  },
  {
    id: 4,
    title: "Silksong",
    url: silksongImg,
    jogou: true,
    liked: true,
    nota: 4.5,
    complete: true,
    avgNota: 4.5,
    totalLikes: 3900,
    totalReviews: 290,
    genre: "Metroidvania",
    year: 2024,
  },
  {
    id: 5,
    title: "Expedition 33",
    url: clairImg,
    jogou: true,
    liked: true,
    nota: 4.5,
    complete: true,
    avgNota: 4.6,
    totalLikes: 2800,
    totalReviews: 210,
    genre: "RPG / Aventura",
    year: 2025,
  },
  {
    id: 6,
    title: "Cyberpunk 2077",
    url: cyberpunkImg,
    jogou: true,
    liked: true,
    nota: 3.5,
    complete: false,
    avgNota: 4.1,
    totalLikes: 7200,
    totalReviews: 890,
    genre: "RPG / Mundo Aberto",
    year: 2020,
  },
];

// Reviews mockados separados do jogo — futuramente virão de GET /games/:id/reviews
const mockReviews = [
  {
    id: 1,
    gameId: 1,
    complete: false,
    content:
      "Esse jogo é incrível! A história é envolvente e os gráficos são de tirar o fôlego. Recomendo para todos os fãs de jogos de ação.",
    author: { username: "Gamer123", avatar: "https://i.pravatar.cc/150?img=1" },
  },
  {
    id: 2,
    gameId: 1,
    complete: false,
    content:
      "Melhor jogo da geração, sem dúvida. O mapa é enorme e cada detalhe foi cuidado com carinho.",
    author: {
      username: "Player456",
      avatar: "https://i.pravatar.cc/150?img=2",
    },
  },
  {
    id: 3,
    gameId: 1,
    complete: true,
    content:
      "Divertido, mas esperava mais em termos de inovação. Vale muito a pena mesmo assim.",
    author: {
      username: "GameLover789",
      avatar: "https://i.pravatar.cc/150?img=3",
    },
  },
];


const mockLists = [
  {
    id: 1,
    name: "Melhores jogos de 2025",
    author: "gamer123",
    games: [mockGames[0], mockGames[1], mockGames[4]],
  },
  {
    id: 2,
    name: "Jogos que me fizeram chorar",
    author: "player456",
    games: [mockGames[1], mockGames[3], mockGames[2]],
  },
  {
    id: 3,
    name: "Open worlds imperdíveis",
    author: "gamelover789",
    games: [mockGames[0], mockGames[5], mockGames[2]],
  },
];

export default function GamePage() {
  const { id } = useParams();
  const [game, setGame] = useState(null);
  const [reviews, setReviews] = useState([]);

  useEffect(() => {
    const foundGame = mockGames.find((g) => g.id === Number(id));
    setGame(foundGame);

    const foundReviews = mockReviews.filter((r) => r.gameId === Number(id));
    setReviews(foundReviews);
  }, [id]);

  if (!game)
    return (
      <div className="bg-linear-to-b from-cinza to-black min-h-screen flex items-center justify-center">
        <p className="text-white text-4xl">Carregando...</p>
      </div>
    );

  return (
    <>
      <div className="min-h-screen bg-linear-to-b from-cinza to-black pt-28 pl-20 pr-20 pb-5 grid grid-cols-6 grid-rows-2 gap-x-20">
        <GameHero game={game}/>
        <Details game={game}/>
        <PopularReviews />
        <GameLists game={game}/>
      </div>
    </>
  );
}

function GameHero({game}) {
  return (
    <div className="flex flex-row items-center self-center gap-4 h-[50%] relative col-span-4 row-span-1">
      <div className="w-[30%]">
        <Card game={game} status={true} />
      </div>
      <div className="flex flex-col gap-4">
        <h1 className="text-white text-5xl font-bold z-50">{game.title}</h1>
        <div className="flex flex-row gap-4 text-white">
          <p>Ano</p>
          <p>Empresa</p>
        </div>
        <p className="text-white">Sinopse</p>
        <div className="flex flex-row items-center justify-center gap-4 text-white font-semibold absolute bottom-0">
          <button className="w-40 h-10 py-2 bg-roxo/80 rounded-sm shadow-md cursor-pointer">
            AVALIE
          </button>
          <button className="w-40 h-10 py-2 bg-turquesa/80 rounded-sm shadow-md cursor-pointer">
            QUERO JOGAR
          </button>
          <button class="w-40 h-10 flex items-center group relative overflow-hidden rounded-sm bg-amarelo/90 from-slate-900 to-slate-800 px-6 py-3 border border-slate-700 shadow-md cursor-pointer">
            <span class="absolute inset-0 block w-full h-full bg-linear-to-r from-transparent via-white/80 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out -skew-x-12"></span>
            <span class="relative z-10">COMPLETEI</span>
          </button>
          <button className="h-9 aspect-square bg-verde/90 rounded-sm shadow-md hover:cursor-pointer flex items-center justify-center">
            <img src={list} alt="list icon"></img>
          </button>
        </div>
      </div>
    </div>
  );
}

function PopularReviews() {
  const animatedLink =
    "text-white text-sm hover:cursor-pointer relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-4 py-1 rounded-2xl";

  const reviews = [
    {
      id: 1,
      complete: false,
      content:
        "Esse jogo é incrível! A história é envolvente e os gráficos são de tirar o fôlego. Recomendo para todos os fãs de jogos de ação.",
      author: {
        username: "Gamer123",
        avatar: "https://i.pravatar.cc/150?img=1",
      },
    },
    {
      id: 2,
      complete: false,
      content:
        "Não gostei muito desse jogo. Achei a jogabilidade confusa e a história fraca. Não recomendo.",
      author: {
        username: "Player456",
        avatar: "https://i.pravatar.cc/150?img=2",
      },
    },
    {
      id: 3,
      complete: true,
      content:
        "Esse jogo é mediano. Tem seus momentos bons, mas também tem muitos problemas técnicos. Vale a pena jogar se você for fã do gênero.",
      author: {
        username: "GameLover789",
        avatar: "https://i.pravatar.cc/150?img=3",
      },
    },
  ];

  return (
    <div className="mb-10 col-span-4">
      <div className="mt-20 w-full border-b border-white flex flex-row items-center justify-between py-2">
        <p className="text-white text-sm">Avaliações populares da semana</p>
        <a className={animatedLink}>Mostrar mais</a>
      </div>
      <div className="flex flex-col gap-6 mt-4">
        {reviews.map((review) => {
          return (
            <Review key={review.id} review={review} game={mockGames[0]} gameClassName="w-28" />
          );
        })}
      </div>
    </div>
  );
}

function Details({game}) {
  const [isSelected, setIsSelected] = useState(["Detalhes", "Plataformas", "Studio"].map((item) => item === "Detalhes"));

  return (
    <div className = "col-span-2 row-span-1 self-center">
      <div className="flex flex-row gap-4 mb-4">
        {["Detalhes", "Plataformas", "Studio"].map((item, index) => (
          <button
            key={index}
            className={`text-sm font-semibold px-4 py-2 rounded-tl-lg rounded-tr-lg ${
              isSelected[index] ? "bg-roxo text-white" : "bg-neutral-700 text-gray-400"
            }`}
            onClick={() => {
              const newSelection = [false, false, false];
              newSelection[index] = true;
              setIsSelected(newSelection);
            }}
          >
            {item}
          </button>
        ))}
      </div>
      <div className="bg-neutral-700 p-4 rounded-b-lg text-white">
        {isSelected[0] && (
          <div>
            <p><strong>Gênero:</strong> {game.genre}</p>
            <p><strong>Ano de lançamento:</strong> {game.year}</p>
            <p><strong>Jogadores:</strong> 1</p>
            <p><strong>Linguagens:</strong> Português, Inglês</p>
          </div>
        )}
        {isSelected[1] && (
          <div>
            <p>Plataformas: PC, PS5, Xbox Series X</p>
          </div>
        )}
        {isSelected[2] && (
          <div>
            <p>Studio: Rockstar Games</p>
          </div>
        )}
      </div>  
    </div>
  )
}

function GameLists({ game }) {
  const animatedLink =
    "text-white text-sm hover:cursor-pointer relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-4 py-1 rounded-2xl";

  return (
    <div className="col-span-2 row-span-1 self-start">
      <div className="mt-20 w-full border-b border-white flex flex-row items-center justify-between py-2">
        <p className="text-white text-sm">Suas listas com esse jogo</p>
        <a className={animatedLink}>Mostrar mais</a>
      </div>
      <div className="mt-4">
        <List lists={mockLists} />
      </div>
    </div>
  );
}

