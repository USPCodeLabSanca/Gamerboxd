import React, { useState } from "react";
import { useParams } from "react-router-dom";

import Card from "../../components/gameCard";
import Review from "../../components/gameReview";
import List from "../../components/List";
import ReviewModal from "../../components/ReviewModal";

import { useGame } from "../../hooks/useGames";
import { toCardGame } from "../../services/gameService";

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

const compact = new Intl.NumberFormat("pt-BR", { notation: "compact" });
const fmt = (n) => compact.format(n ?? 0);

const animatedLink =
  "text-white text-sm hover:cursor-pointer relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-4 py-1 rounded-2xl";

export default function GamePage() {
  const { id } = useParams();
  const { data, isLoading, isError } = useGame(id);
  const game = data ? toCardGame(data) : null;

  const [modalOpen, setModalOpen] = useState(false);
  const [wishlist, setWishlist] = useState(false);
  const [completo, setCompleto] = useState(false);

  if (isLoading) return (
    <div className="bg-linear-to-b from-cinza to-black min-h-screen flex items-center justify-center">
      <p className="text-white text-4xl">Carregando...</p>
    </div>
  );

  if (isError || !game) return (
    <div className="bg-linear-to-b from-cinza to-black min-h-screen flex items-center justify-center">
      <p className="text-white text-4xl">Jogo não encontrado</p>
    </div>
  );

  return (
    <>
      <ReviewModal
        game={game}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={(data) => console.log("Review enviada:", data)}
      />

      <div className="relative min-h-screen overflow-x-hidden bg-linear-to-b from-cinza to-black">
        <Backdrop src={game.url} />

        <div className="relative z-10 mx-auto max-w-7xl px-6 lg:px-20 pt-36 pb-16">
          <GameHero
            game={game}
            onAvaliar={() => setModalOpen(true)}
            wishlist={wishlist}
            onWishlist={() => setWishlist((w) => !w)}
            completo={completo}
            onCompleto={() => setCompleto((c) => !c)}
          />

          <div className="mt-20 grid gap-12 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <PopularReviews game={game} />
            </div>
            <GameLists />
          </div>
        </div>
      </div>
    </>
  );
}


function Backdrop({ src }) {
  if (!src) return null;

  const fade = "linear-gradient(to bottom, black 30%, transparent)";

  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-x-0 top-0 h-[34rem] overflow-hidden"
      style={{ maskImage: fade, WebkitMaskImage: fade }}
    >
      <img src={src} alt="" className="h-full w-full scale-100 object-cover opacity-40 blur-3xl saturate-150" />
    </div>
  );
}

function GameHero({ game, onAvaliar, wishlist, onWishlist, completo, onCompleto }) {
  const [hovered, setHovered] = useState(null);

  const hoverProps = (name) => ({
    onMouseEnter: () => setHovered(name),
    onMouseLeave: () => setHovered(null),
    onFocus: () => setHovered(name),
    onBlur: () => setHovered(null),
  });

  const fx = (name) => (hovered === name ? "scale-105" : "");

  return (
    <div className="flex flex-col items-center gap-10 md:flex-row md:items-start">
      {}
      <div className="w-60 shrink-0">
        <Card game={game} status={true} />
        <div className="mt-3 flex justify-center gap-5 text-xs text-white/70">
          <Counter icon={<IconCheck />} value={game.totalCompleted} label="completaram" />
          <Counter icon={<IconMessage />} value={game.totalReviews} label="avaliações" />
          <Counter icon={<IconHeart />} value={game.totalLikes} label="curtidas" />
        </div>
      </div>

      {}
      <div className="flex w-full flex-1 flex-col gap-6 md:pt-24">
        <h1 className="text-3xl font-bold leading-tight text-white md:text-4xl">
          {game.title}
          {game.year && <span className="ml-3 text-xl font-normal text-white/60">{game.year}</span>}
        </h1>
        <RatingBox game={game} onAvaliar={onAvaliar} />
      </div>

      {}
      <div className="flex w-full flex-col gap-2 text-sm font-semibold text-white md:w-72 md:shrink-0 md:pt-24">
        <button
          onClick={onAvaliar}
          {...hoverProps("avalie")}
          className={`h-11 w-full cursor-pointer rounded-sm bg-roxo/80 shadow-md transition-all duration-200 hover:bg-roxo ${fx("avalie")}`}
        >
          AVALIE
        </button>

        <button
          onClick={onWishlist}
          {...hoverProps("wishlist")}
          className={`h-11 w-full cursor-pointer rounded-sm shadow-md transition-all duration-200 ${wishlist ? "bg-turquesa font-bold" : "bg-turquesa/80 hover:bg-turquesa"} ${fx("wishlist")}`}
        >
          {wishlist ? "✓ NA WISHLIST" : "QUERO JOGAR"}
        </button>

        <button
          onClick={onCompleto}
          {...hoverProps("completei")}
          className={`group relative flex h-11 w-full cursor-pointer items-center justify-center overflow-hidden rounded-sm shadow-md transition-all duration-200 ${completo ? "bg-amarelo font-bold" : "bg-amarelo/90"} ${fx("completei")}`}
        >
          {!completo && (
            <span className="absolute inset-0 block h-full w-full -translate-x-full -skew-x-12 bg-linear-to-r from-transparent via-white/80 to-transparent transition-transform duration-1000 ease-out group-hover:translate-x-full" />
          )}
          <span className="relative z-10">{completo ? "✓ COMPLETEI" : "COMPLETEI"}</span>
        </button>

        <button
          {...hoverProps("lista")}
          className={`flex h-11 w-full cursor-pointer items-center justify-center gap-2 rounded-sm bg-verde/90 shadow-md transition-all duration-200 hover:bg-verde ${fx("lista")}`}
        >
          <img src={list} alt="" className="h-5" />
          ADICIONAR À LISTA
        </button>
      </div>
    </div>
  );
}

function RatingBox({ game, onAvaliar }) {
  const hasRating = typeof game.avgNota === "number" && game.avgNota > 0;

  return (
    <div className="w-full max-w-md">
      <p className="border-b border-white/30 pb-1 text-sm text-white/60">Avaliação média</p>

      {hasRating ? (
        <div className="mt-3 flex items-center justify-between">
          <Stars value={game.avgNota} className="text-3xl" />
          <span className="text-4xl font-semibold text-white">{game.avgNota.toFixed(1)}</span>
        </div>
      ) : (
        <p className="mt-3 text-white/70">
          Ninguém avaliou ainda.{" "}
          <button onClick={onAvaliar} className="cursor-pointer text-turquesa hover:underline">
            Seja o primeiro a avaliar
          </button>
        </p>
      )}
    </div>
  );
}


function Stars({ value = 0, className = "" }) {
  const pct = (Math.max(0, Math.min(5, value)) / 5) * 100;

  return (
    <span
      className={`relative inline-block whitespace-nowrap leading-none tracking-wider ${className}`}
      role="img"
      aria-label={`Nota ${value.toFixed(1)} de 5`}
    >
      <span className="text-white/20">★★★★★</span>
      <span className="absolute inset-0 overflow-hidden whitespace-nowrap text-amarelo" style={{ width: `${pct}%` }}>
        ★★★★★
      </span>
    </span>
  );
}

function Counter({ icon, value, label }) {
  return (
    <span className="flex items-center gap-1.5" title={`${value ?? 0} ${label}`}>
      {icon}
      {fmt(value)}
    </span>
  );
}

const iconProps = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: "h-4 w-4",
  "aria-hidden": true,
};

const IconCheck = () => (
  <svg {...iconProps}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><path d="m9 11 3 3L22 4" /></svg>
);
const IconMessage = () => (
  <svg {...iconProps}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
);
const IconHeart = () => (
  <svg {...iconProps}><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" /></svg>
);

function SectionHeader({ title }) {
  return (
    <div className="flex w-full flex-row items-center justify-between border-b border-white py-2">
      <p className="text-sm text-white">{title}</p>
      <a className={animatedLink}>Mostrar mais</a>
    </div>
  );
}

function PopularReviews({ game }) {
  const reviews = [
    {
      id: 1,
      complete: false,
      content:
        "Esse jogo é incrível! A história é envolvente e os gráficos são de tirar o fôlego. Recomendo para todos os fãs de jogos de ação.",
      author: { username: "Gamer123", avatar: "https://i.pravatar.cc/150?img=1" },
    },
    {
      id: 2,
      complete: false,
      content:
        "Não gostei muito desse jogo. Achei a jogabilidade confusa e a história fraca. Não recomendo.",
      author: { username: "Player456", avatar: "https://i.pravatar.cc/150?img=2" },
    },
    {
      id: 3,
      complete: true,
      content:
        "Esse jogo é mediano. Tem seus momentos bons, mas também tem muitos problemas técnicos. Vale a pena jogar se você for fã do gênero.",
      author: { username: "GameLover789", avatar: "https://i.pravatar.cc/150?img=3" },
    },
  ];

  return (
    <div>
      <SectionHeader title="Avaliações populares da semana" />
      <div className="mt-4 flex flex-col gap-6">
        {reviews.map((review) => (
          <Review key={review.id} review={review} game={game} gameClassName="w-28" />
        ))}
      </div>
    </div>
  );
}

function GameLists() {
  return (
    <div>
      <SectionHeader title="Suas listas com esse jogo" />
      <div className="mt-4">
        <List lists={mockLists} />
      </div>
    </div>
  );
}