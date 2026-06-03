// src/pages/lists/index.jsx
import React, { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

import gtaImg from "../../assets/imgs/gta.png";
import gowImg from "../../assets/imgs/ragnarok.png";
import silksongImg from "../../assets/imgs/silksong.png";
import rdr2Img from "../../assets/imgs/rdr2.jpg";
import cyberpunkImg from "../../assets/imgs/cyberpunk2077.png";
import clairImg from "../../assets/imgs/clair-obscure.png";

// ─── Mock Data ────────────────────────────────────────────────────────────────

const mockGames = [
  { id: 1, title: "GTA VI", url: gtaImg, year: 2025, genre: "Ação / Mundo Aberto" },
  { id: 2, title: "God of War", url: gowImg, year: 2022, genre: "Ação / Aventura" },
  { id: 3, title: "God of War II", url: rdr2Img, year: 2023, genre: "Ação / Aventura" },
  { id: 4, title: "Silksong", url: silksongImg, year: 2024, genre: "Metroidvania" },
  { id: 5, title: "Expedition 33", url: clairImg, year: 2025, genre: "RPG / Aventura" },
  { id: 6, title: "Cyberpunk 2077", url: cyberpunkImg, year: 2020, genre: "RPG / Mundo Aberto" },
];

const mockLists = [
  { id: 1, name: "Melhores jogos de 2025", author: "gamer123", saved: false, saves: 142, games: [mockGames[0], mockGames[4], mockGames[1], mockGames[2]] },
  { id: 2, name: "Jogos que me fizeram chorar", author: "player456", saved: true, saves: 87, games: [mockGames[1], mockGames[3], mockGames[4]] },
  { id: 3, name: "Open worlds imperdíveis", author: "gamelover789", saved: false, saves: 204, games: [mockGames[0], mockGames[5], mockGames[2]] },
  { id: 4, name: "Masterpieces do século", author: "gamer123", saved: false, saves: 391, games: [mockGames[1], mockGames[0], mockGames[4], mockGames[3]] },
  { id: 5, name: "Jogos indie que superam AAA", author: "indielover", saved: true, saves: 56, games: [mockGames[3], mockGames[4]] },
  { id: 6, name: "RPGs para iniciantes", author: "player456", saved: false, saves: 78, games: [mockGames[5], mockGames[1], mockGames[4]] },
];

// ─── Shared Components ────────────────────────────────────────────────────────

const GameStackCover = ({ games, size = "md" }) => {
  const visible = games.slice(0, 4);
  const w = size === "lg" ? 90 : 72;
  const h = size === "lg" ? 112 : 90;
  const gap = size === "lg" ? 22 : 18;
  const totalW = w + gap * (visible.length - 1) + 12;

  return (
    <div className="relative shrink-0" style={{ width: totalW, height: h + 12 }}>
      {visible.map((game, i) => (
        <div
          key={game.id}
          className="absolute rounded-xl overflow-hidden border border-white/10 shadow-lg"
          style={{
            left: `${i * gap}px`,
            top: `${i * 3}px`,
            width: w,
            height: h,
            zIndex: visible.length - i,
            transform: `rotate(${(i - 1) * 3}deg)`,
            filter: i > 0 ? `brightness(${1 - i * 0.15})` : "brightness(1)",
          }}
        >
          <img src={game.url} alt={game.title} className="h-full w-full object-cover" />
        </div>
      ))}
    </div>
  );
};

const PlusIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
  </svg>
);

const BookmarkIcon = ({ filled }) => (
  <svg viewBox="0 0 24 24" fill={filled ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" className="w-4 h-4">
    <path strokeLinecap="round" strokeLinejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 11.186 0Z" />
  </svg>
);

const TrashIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
    <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
  </svg>
);

const EditIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
    <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125" />
  </svg>
);

const XIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
  </svg>
);

// ─── Create/Edit Modal ────────────────────────────────────────────────────────

function ListModal({ isOpen, onClose, onSave, editList = null }) {
  const [name, setName] = useState(editList?.name ?? "");
  const [description, setDescription] = useState(editList?.description ?? "");
  const [isPrivate, setIsPrivate] = useState(editList?.is_private ?? false);

  const handleSave = () => {
    if (!name.trim()) return;
    onSave({ name, description, is_private: isPrivate });
    onClose();
  };

  React.useEffect(() => {
    if (editList) {
      setName(editList.name);
      setDescription(editList.description ?? "");
      setIsPrivate(editList.is_private ?? false);
    } else {
      setName(""); setDescription(""); setIsPrivate(false);
    }
  }, [editList, isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose} className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50" />
          <motion.div initial={{ opacity: 0, scale: 0.95, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }} transition={{ type: "spring", duration: 0.4 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
            <div className="bg-neutral-800/95 backdrop-blur-md rounded-2xl shadow-2xl w-full max-w-md pointer-events-auto border border-white/5 p-6"
              onClick={(e) => e.stopPropagation()}>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-white font-bold text-xl">{editList ? "Editar lista" : "Nova lista"}</h2>
                <button onClick={onClose} className="text-white/30 hover:text-white transition-colors"><XIcon /></button>
              </div>

              <div className="flex flex-col gap-4">
                <div>
                  <label className="text-white/50 text-xs mb-1.5 block">Nome da lista</label>
                  <input type="text" value={name} onChange={(e) => setName(e.target.value)}
                    placeholder="ex: Melhores jogos de 2025"
                    className="w-full bg-neutral-700/60 text-white text-sm rounded-xl px-4 py-3 outline-none border border-white/10 focus:border-roxo/60 transition-colors placeholder:text-white/25" />
                </div>
                <div>
                  <label className="text-white/50 text-xs mb-1.5 block">Descrição (opcional)</label>
                  <textarea value={description} onChange={(e) => setDescription(e.target.value)}
                    placeholder="Descreva sua lista..."
                    rows={3}
                    className="w-full bg-neutral-700/60 text-white text-sm rounded-xl px-4 py-3 outline-none border border-white/10 focus:border-roxo/60 transition-colors placeholder:text-white/25 resize-none" />
                </div>
                <label className="flex items-center gap-3 cursor-pointer select-none">
                  <div
                    onClick={() => setIsPrivate(!isPrivate)}
                    className={`w-10 h-6 rounded-full transition-colors duration-200 flex items-center px-1 ${isPrivate ? "bg-roxo" : "bg-white/20"}`}>
                    <div className={`w-4 h-4 bg-white rounded-full transition-transform duration-200 ${isPrivate ? "translate-x-4" : "translate-x-0"}`} />
                  </div>
                  <span className="text-white/70 text-sm">Lista privada</span>
                </label>
              </div>

              <div className="flex gap-3 mt-6 justify-end">
                <button onClick={onClose} className="px-5 py-2.5 text-white/50 hover:text-white text-sm transition-colors">Cancelar</button>
                <button onClick={handleSave}
                  className="relative overflow-hidden bg-roxo hover:bg-roxo/80 text-white font-semibold px-6 py-2.5 rounded-xl transition-colors text-sm shadow-lg shadow-roxo/20">
                  <span className="relative z-10">{editList ? "Salvar" : "Criar lista"}</span>
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

// ─── List Card (explorar) ─────────────────────────────────────────────────────

function ListCard({ list, onSaveToggle }) {
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}
      className="group bg-neutral-800/60 border border-white/5 hover:border-roxo/30 rounded-2xl p-5 flex gap-5 items-start transition-all duration-300 hover:bg-neutral-800/90">
      <Link to={`/lists/${list.id}`}>
        <GameStackCover games={list.games} />
      </Link>
      <div className="flex-1 min-w-0 flex flex-col gap-2">
        <Link to={`/lists/${list.id}`}>
          <h3 className="text-white font-semibold text-base group-hover:text-roxo transition-colors duration-200 leading-tight">{list.name}</h3>
        </Link>
        <p className="text-white/40 text-xs">
          {list.games.length} jogos · por <span className="text-white/60">{list.author}</span>
        </p>
        <div className="flex items-center gap-3 mt-2">
          <button
            onClick={() => onSaveToggle(list.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 ${list.saved ? "bg-roxo/20 text-roxo" : "text-white/40 hover:text-white/80 hover:bg-white/5"}`}>
            <BookmarkIcon filled={list.saved} />
            <span>{list.saves + (list.saved ? 0 : 0)}</span>
          </button>
        </div>
      </div>
    </motion.div>
  );
}

// ─── My List Row ──────────────────────────────────────────────────────────────

function MyListRow({ list, onEdit, onDelete }) {
  return (
    <motion.div initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.25 }}
      className="group flex items-center gap-5 py-3 border-b border-white/5 hover:border-roxo/30 transition-colors duration-300">
      <Link to={`/lists/${list.id}`}>
        <GameStackCover games={list.games} />
      </Link>
      <Link to={`/lists/${list.id}`} className="flex-1 min-w-0">
        <p className="text-white font-semibold text-sm group-hover:text-roxo transition-colors">{list.name}</p>
        <p className="text-white/40 text-xs mt-0.5">{list.games.length} jogos · {list.saves} saves</p>
      </Link>
      <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <button onClick={() => onEdit(list)}
          className="p-2 rounded-lg text-white/40 hover:text-white hover:bg-white/5 transition-all">
          <EditIcon />
        </button>
        <button onClick={() => onDelete(list.id)}
          className="p-2 rounded-lg text-white/40 hover:text-red-400 hover:bg-red-400/10 transition-all">
          <TrashIcon />
        </button>
      </div>
      <span className="text-white/20 group-hover:text-roxo group-hover:translate-x-1 transition-all duration-200 text-lg mr-1">→</span>
    </motion.div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

const TABS = ["Explorar", "Minhas listas"];

export default function Lists() {
  const [tab, setTab] = useState("Explorar");
  const [lists, setLists] = useState(mockLists);
  const [myLists, setMyLists] = useState(mockLists.filter(l => l.author === "gamer123"));
  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState(null);
  const [search, setSearch] = useState("");

  const handleSaveToggle = (id) => {
    setLists(ls => ls.map(l => l.id === id ? { ...l, saved: !l.saved, saves: l.saved ? l.saves - 1 : l.saves + 1 } : l));
  };

  const handleCreate = (data) => {
    const newList = { id: Date.now(), ...data, author: "gamer123", saved: false, saves: 0, games: [] };
    setMyLists(ls => [newList, ...ls]);
    setLists(ls => [newList, ...ls]);
  };

  const handleEdit = (list) => { setEditTarget(list); setModalOpen(true); };

  const handleSaveEdit = (data) => {
    setMyLists(ls => ls.map(l => l.id === editTarget.id ? { ...l, ...data } : l));
    setLists(ls => ls.map(l => l.id === editTarget.id ? { ...l, ...data } : l));
    setEditTarget(null);
  };

  const handleDelete = (id) => {
    setMyLists(ls => ls.filter(l => l.id !== id));
    setLists(ls => ls.filter(l => l.id !== id));
  };

  const filteredLists = lists.filter(l => l.name.toLowerCase().includes(search.toLowerCase()));
  const filteredMine = myLists.filter(l => l.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="min-h-screen bg-gradient-to-b from-cinza to-black pt-28 pb-16 px-6 sm:px-12 lg:px-24">
      <ListModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditTarget(null); }}
        onSave={editTarget ? handleSaveEdit : handleCreate}
        editList={editTarget}
      />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
        <div>
          <h1 className="text-white font-bold text-4xl sm:text-5xl">Listas</h1>
          <p className="text-white/40 text-sm mt-1">Coleções criadas pela comunidade</p>
        </div>
        <button
          onClick={() => { setEditTarget(null); setModalOpen(true); }}
          className="flex items-center gap-2 bg-roxo hover:bg-roxo/80 text-white font-semibold px-5 py-2.5 rounded-xl transition-colors text-sm shadow-lg shadow-roxo/20 self-start sm:self-auto">
          <PlusIcon />
          Nova lista
        </button>
      </div>

      {/* Tabs + Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div className="flex gap-1 bg-white/5 rounded-xl p-1 w-fit">
          {TABS.map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-5 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${tab === t ? "bg-roxo text-white shadow" : "text-white/50 hover:text-white"}`}>
              {t}
            </button>
          ))}
        </div>
        <input
          type="text"
          placeholder="Buscar listas..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-white/5 border border-white/10 focus:border-roxo/50 text-white placeholder:text-white/30 text-sm rounded-xl px-4 py-2.5 outline-none transition-colors w-full sm:w-64"
        />
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {tab === "Explorar" ? (
          <motion.div key="explorar" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredLists.length > 0
              ? filteredLists.map(l => <ListCard key={l.id} list={l} onSaveToggle={handleSaveToggle} />)
              : <p className="text-white/30 text-sm col-span-2 text-center py-16">Nenhuma lista encontrada.</p>}
          </motion.div>
        ) : (
          <motion.div key="minhas" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            {filteredMine.length > 0
              ? filteredMine.map(l => <MyListRow key={l.id} list={l} onEdit={handleEdit} onDelete={handleDelete} />)
              : (
                <div className="flex flex-col items-center justify-center py-24 gap-4">
                  <p className="text-white/30 text-sm">Você ainda não criou nenhuma lista.</p>
                  <button onClick={() => { setEditTarget(null); setModalOpen(true); }}
                    className="flex items-center gap-2 bg-roxo/20 hover:bg-roxo text-roxo hover:text-white font-semibold px-5 py-2.5 rounded-xl transition-all text-sm border border-roxo/40">
                    <PlusIcon /> Criar minha primeira lista
                  </button>
                </div>
              )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
