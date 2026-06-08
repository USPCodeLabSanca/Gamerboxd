// src/pages/lists/[id].jsx  →  coloca em src/pages/listDetail/index.jsx
import React, { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import Card from "../../components/gameCard";

import gtaImg from "../../assets/imgs/gta.png";
import gowImg from "../../assets/imgs/ragnarok.png";
import silksongImg from "../../assets/imgs/silksong.png";
import rdr2Img from "../../assets/imgs/rdr2.jpg";
import cyberpunkImg from "../../assets/imgs/cyberpunk2077.png";
import clairImg from "../../assets/imgs/clair-obscure.png";

const mockGames = [
  { id: 1, title: "GTA VI", url: gtaImg, year: 2025, genre: "Ação / Mundo Aberto", nota: 5, liked: true, jogou: true, complete: true },
  { id: 2, title: "God of War", url: gowImg, year: 2022, genre: "Ação / Aventura", nota: 5, liked: true, jogou: true, complete: true },
  { id: 3, title: "God of War II", url: rdr2Img, year: 2023, genre: "Ação / Aventura", nota: 5, liked: true, jogou: true, complete: true },
  { id: 4, title: "Silksong", url: silksongImg, year: 2024, genre: "Metroidvania", nota: 4.5, liked: true, jogou: true, complete: true },
  { id: 5, title: "Expedition 33", url: clairImg, year: 2025, genre: "RPG / Aventura", nota: 4.5, liked: true, jogou: true, complete: true },
  { id: 6, title: "Cyberpunk 2077", url: cyberpunkImg, year: 2020, genre: "RPG / Mundo Aberto", nota: 3.5, liked: true, jogou: true, complete: false },
];

const mockLists = [
  { id: "1", name: "Melhores jogos de 2025", description: "Os jogos mais marcantes do ano, na minha opinião.", author: "gamer123", saved: false, saves: 142, is_mine: true, games: [mockGames[0], mockGames[4], mockGames[1], mockGames[2]] },
  { id: "2", name: "Jogos que me fizeram chorar", description: "Histórias que ficam na memória.", author: "player456", saved: true, saves: 87, is_mine: false, games: [mockGames[1], mockGames[3], mockGames[4]] },
  { id: "3", name: "Open worlds imperdíveis", description: null, author: "gamelover789", saved: false, saves: 204, is_mine: false, games: [mockGames[0], mockGames[5], mockGames[2]] },
];

const BookmarkIcon = ({ filled }) => (
  <svg viewBox="0 0 24 24" fill={filled ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 11.186 0Z" />
  </svg>
);

const TrashIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
  </svg>
);

const XIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
  </svg>
);

const MinusIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
    <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14" />
  </svg>
);

// Banner collage das capas
function CoverBanner({ games }) {
  const covers = games.slice(0, 5);
  return (
    <div className="w-full h-52 sm:h-72 relative overflow-hidden rounded-2xl mb-8">
      <div className="flex h-full">
        {covers.map((game, i) => (
          <div key={game.id} className="flex-1 relative overflow-hidden"
            style={{ filter: `brightness(${0.9 - i * 0.1})` }}>
            <img src={game.url} alt={game.title} className="h-full w-full object-cover scale-110" />
          </div>
        ))}
      </div>
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />
      <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-transparent to-transparent" />
    </div>
  );
}

export default function ListDetail() {
  const { id } = useParams();
  const [list, setList] = useState(() => mockLists.find(l => l.id === id) ?? mockLists[0]);
  const [saved, setSaved] = useState(list.saved);
  const [saves, setSaves] = useState(list.saves);

  const handleSaveToggle = () => {
    setSaved(s => !s);
    setSaves(s => saved ? s - 1 : s + 1);
  };

  const handleRemoveGame = (gameId) => {
    setList(l => ({ ...l, games: l.games.filter(g => g.id !== gameId) }));
  };

  if (!list) return (
    <div className="min-h-screen bg-gradient-to-b from-cinza to-black flex items-center justify-center">
      <p className="text-white/40 text-xl">Lista não encontrada.</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-cinza to-black pt-24 pb-16 px-6 sm:px-12 lg:px-24">

      {/* Banner */}
      <CoverBanner games={list.games} />

      {/* Info header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-6 mb-10">
        <div>
          <h1 className="text-white font-bold text-3xl sm:text-4xl leading-tight mb-2">{list.name}</h1>
          {list.description && <p className="text-white/50 text-sm mb-3 max-w-xl">{list.description}</p>}
          <p className="text-white/40 text-sm">
            Por <Link to={`/members/${list.author}`} className="text-roxo hover:underline">{list.author}</Link>
            {" · "}{list.games.length} {list.games.length === 1 ? "jogo" : "jogos"}
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          {/* Save (não é o dono) */}
          {!list.is_mine && (
            <button onClick={handleSaveToggle}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 border ${saved ? "bg-roxo/20 border-roxo/40 text-roxo" : "border-white/10 text-white/50 hover:border-white/30 hover:text-white"}`}>
              <BookmarkIcon filled={saved} />
              {saves} {saves === 1 ? "save" : "saves"}
            </button>
          )}

          {/* Ações do dono */}
          {list.is_mine && (
            <button className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium text-red-400 border border-red-400/20 hover:bg-red-400/10 transition-all">
              <TrashIcon />
              Deletar lista
            </button>
          )}
        </div>
      </div>

      {/* Grid de jogos */}
      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-3">
        <AnimatePresence>
          {list.games.map((game, i) => (
            <motion.div key={game.id}
              initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }} transition={{ delay: i * 0.05 }}
              className="relative group">
              <Card game={game} status={false} />
              {/* Botão de remover — só aparece pra dono */}
              {list.is_mine && (
                <button
                  onClick={() => handleRemoveGame(game.id)}
                  className="absolute top-1.5 right-1.5 w-6 h-6 bg-black/80 hover:bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-200 z-10 text-white">
                  <MinusIcon />
                </button>
              )}
              <p className="text-white/60 text-xs mt-1.5 truncate text-center">{game.title}</p>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Slot vazio pra adicionar — só pra dono */}
        {list.is_mine && (
          <Link to="/games" className="aspect-[4/5] rounded-2xl border-2 border-dashed border-white/15 hover:border-roxo/50 flex items-center justify-center transition-colors duration-200 group">
            <span className="text-white/20 group-hover:text-roxo text-3xl transition-colors">+</span>
          </Link>
        )}
      </div>
    </div>
  );
}
