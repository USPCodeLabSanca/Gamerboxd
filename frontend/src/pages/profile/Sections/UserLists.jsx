import React, { useState, useMemo } from "react";
import { Link, useParams } from "react-router-dom";
import { Eye, EyeOff, Heart, Pencil, Plus, X, ArrowUpDown, Filter } from "lucide-react";

import gtaImg from "../../../assets/imgs/gta.png";
import gowImg from "../../../assets/imgs/ragnarok.png";
import silksongImg from "../../../assets/imgs/silksong.png";
import rdr2Img from "../../../assets/imgs/rdr2.jpg";
import cyberpunkImg from "../../../assets/imgs/cyberpunk2077.png";
import clairImg from "../../../assets/imgs/clair-obscure.png";

// Catálogo mock para adicionar jogos no modal 
const AVAILABLE_GAMES = [
  { id: 1, title: "GTA VI", url: gtaImg },
  { id: 2, title: "God of War", url: gowImg },
  { id: 3, title: "Red Dead Redemption 2", url: rdr2Img },
  { id: 4, title: "Hollow Knight: Silksong", url: silksongImg },
  { id: 5, title: "Clair Obscur: Expedition 33", url: clairImg },
  { id: 6, title: "Cyberpunk 2077", url: cyberpunkImg },
];

// IDs "1", "2" e "3" batem com o mock atual do ListDetail; listas extras sem ID correspondente vão para "/lists"
const INITIAL_USER_LISTS = [
  {
    id: "1",
    detailPath: "/lists/1",
    name: "Favoritos",
    author: "gamer123",
    isOwner: true,
    isPublic: true,
    likes: 15000,
    createdAt: "2026-10-15T14:00:00Z",
    interactedAt: "2026-10-15T14:00:00Z",
    games: [AVAILABLE_GAMES[1], AVAILABLE_GAMES[0], AVAILABLE_GAMES[3], AVAILABLE_GAMES[4], AVAILABLE_GAMES[5]],
  },
  {
    id: "2",
    detailPath: "/lists/2",
    name: "Jogos que me fizeram chorar",
    author: "player456",
    isOwner: false,
    isPublic: true,
    likes: 87,
    createdAt: "2026-08-10T12:00:00Z",
    interactedAt: "2026-11-18T20:00:00Z",
    games: [AVAILABLE_GAMES[1], AVAILABLE_GAMES[3], AVAILABLE_GAMES[4]],
  },
  {
    id: "3",
    detailPath: "/lists/3",
    name: "Open worlds imperdíveis",
    author: "gamelover789",
    isOwner: false,
    isPublic: true,
    likes: 204,
    createdAt: "2026-07-05T09:00:00Z",
    interactedAt: "2026-11-10T16:45:00Z",
    games: [AVAILABLE_GAMES[0], AVAILABLE_GAMES[5], AVAILABLE_GAMES[2]],
  },
  {
    id: "4",
    detailPath: "/lists",
    name: "Quero Jogar",
    author: "gamer123",
    isOwner: true,
    isPublic: false,
    likes: 1,
    createdAt: "2026-11-02T10:30:00Z",
    interactedAt: "2026-11-02T10:30:00Z",
    games: [AVAILABLE_GAMES[3], AVAILABLE_GAMES[4], AVAILABLE_GAMES[0], AVAILABLE_GAMES[2]],
  },
  {
    id: "5",
    detailPath: "/lists",
    name: "Platinados",
    author: "gamer123",
    isOwner: true,
    isPublic: true,
    likes: 10000,
    createdAt: "2026-09-20T18:15:00Z",
    interactedAt: "2026-09-20T18:15:00Z",
    games: [AVAILABLE_GAMES[1], AVAILABLE_GAMES[2], AVAILABLE_GAMES[5], AVAILABLE_GAMES[3]],
  },
];

function formatLikes(num) {
  if (num >= 1000) return `${(num / 1000).toFixed(num % 1000 === 0 ? 0 : 1)}k`;
  return String(num);
}

// Pilha horizontal de capas 
function OverlappingCovers({ games }) {
  const visible = games.slice(0, 5);
  return (
    <div className="flex items-center bg-black/25 p-1.5 rounded-lg border border-white/10 w-fit shrink-0">
      {visible.length > 0 ? (
        visible.map((game, idx) => (
          <div
            key={`${game.id}-${idx}`}
            className="w-14 h-20 sm:w-16 sm:h-24 rounded-md overflow-hidden border border-black/60 shadow-md transition-transform hover:-translate-y-1"
            style={{
              marginLeft: idx === 0 ? 0 : "-22px",
              zIndex: visible.length - idx,
            }}
          >
            <img src={game.url} alt={game.title} className="w-full h-full object-cover" />
          </div>
        ))
      ) : (
        <div className="w-28 h-20 sm:h-24 flex items-center justify-center text-xs text-white/30">
          Sem jogos
        </div>
      )}
    </div>
  );
}

// Modal de Criar / Editar Lista 
function EditListModal({ isOpen, onClose, onSave, initialData }) {
  const [name, setName] = useState("");
  const [isPublic, setIsPublic] = useState(true);
  const [gameQuery, setGameQuery] = useState("");
  const [selectedGames, setSelectedGames] = useState([]);

  React.useEffect(() => {
    if (initialData) {
      setName(initialData.name);
      setIsPublic(initialData.isPublic);
      setSelectedGames(initialData.games || []);
    } else {
      setName("");
      setIsPublic(true);
      setSelectedGames([]);
    }
    setGameQuery("");
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const searchResults = AVAILABLE_GAMES.filter((g) =>
    g.title.toLowerCase().includes(gameQuery.toLowerCase())
  );

  const handleAddGame = (game) => {
    if (!selectedGames.some((g) => g.id === game.id)) {
      setSelectedGames((prev) => [...prev, game]);
    }
  };

  const handleRemoveGame = (id) => {
    setSelectedGames((prev) => prev.filter((g) => g.id !== id));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    onSave({ name: name.trim(), isPublic, games: selectedGames });
    onClose();
  };

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4"
    >
      <form
        onSubmit={handleSubmit}
        onClick={(e) => e.stopPropagation()}
        className="bg-[#2c2c2c] border border-white/15 rounded-2xl w-full max-w-xl p-6 shadow-2xl text-white flex flex-col gap-6"
      >
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">
            {initialData ? "Editar Lista" : "Adicionar Lista"}
          </h3>
          <button type="button" onClick={onClose} className="text-white/50 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Campos superiores: Nome/Visibilidade à esquerda e Busca de jogos à direita */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div className="flex flex-col gap-4">
            <div>
              <label className="block text-xs text-white/60 mb-1.5">Nome da lista</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ex: Favoritos"
                className="w-full bg-white text-black text-sm rounded-full px-4 py-1.5 outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div className="flex items-center gap-4 text-xs text-white/80">
              <span>Público?</span>
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input
                  type="radio"
                  name="visibility"
                  checked={isPublic}
                  onChange={() => setIsPublic(true)}
                  className="accent-purple-500"
                />
                Sim
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input
                  type="radio"
                  name="visibility"
                  checked={!isPublic}
                  onChange={() => setIsPublic(false)}
                  className="accent-purple-500"
                />
                Não
              </label>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label className="block text-xs text-white/60">Nome do jogo</label>
            <input
              type="text"
              value={gameQuery}
              onChange={(e) => setGameQuery(e.target.value)}
              placeholder="Buscar jogo..."
              className="w-full bg-white text-black text-sm rounded-full px-4 py-1.5 outline-none focus:ring-2 focus:ring-purple-500"
            />
            <div className="flex gap-2 overflow-x-auto pt-1 pb-1">
              {searchResults.slice(0, 3).map((game) => (
                <div key={game.id} className="relative shrink-0 group">
                  <img
                    src={game.url}
                    alt={game.title}
                    className="w-12 h-16 object-cover rounded border border-white/20"
                  />
                  <button
                    type="button"
                    onClick={() => handleAddGame(game)}
                    title={`Adicionar ${game.title}`}
                    className="absolute -top-1.5 -right-1.5 bg-neutral-900 border border-white/40 text-white rounded-full w-5 h-5 flex items-center justify-center hover:bg-purple-600 transition-colors"
                  >
                    <Plus className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Jogos Adicionados */}
        <div>
          <p className="text-xs text-white/70 mb-2">Jogos Adicionados</p>
          {selectedGames.length > 0 ? (
            <div className="flex flex-wrap gap-2.5">
              {selectedGames.map((game) => (
                <div key={game.id} className="relative group">
                  <img
                    src={game.url}
                    alt={game.title}
                    className="w-14 h-20 object-cover rounded-md border border-white/15"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveGame(game.id)}
                    title="Remover jogo"
                    className="absolute -top-1.5 -right-1.5 bg-red-600 text-white rounded-full w-5 h-5 flex items-center justify-center opacity-90 hover:opacity-100"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-white/35 py-4 border border-dashed border-white/15 rounded-lg text-center">
              Clique no "+" nos jogos acima para adicionar à lista.
            </p>
          )}
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            className="text-sm text-white underline underline-offset-4 hover:text-purple-400 transition-colors font-medium"
          >
            Salvar Lista
          </button>
        </div>
      </form>
    </div>
  );
}

export default function UserLists() {
  const { username } = useParams();
  const [lists, setLists] = useState(INITIAL_USER_LISTS);
  const [originFilter, setOriginFilter] = useState("all"); // all | created | liked
  const [sortBy, setSortBy] = useState("recent"); // recent | oldest | alpha-asc | alpha-desc
  const [modalOpen, setModalOpen] = useState(false);
  const [editingList, setEditingList] = useState(null);

  const filteredAndSortedLists = useMemo(() => {
    const byOrigin = lists.filter((list) => {
      if (originFilter === "created") return list.isOwner;
      if (originFilter === "liked") return !list.isOwner;
      return true;
    });

    return [...byOrigin].sort((a, b) => {
      if (sortBy === "alpha-asc") return a.name.localeCompare(b.name, "pt-BR");
      if (sortBy === "alpha-desc") return b.name.localeCompare(a.name, "pt-BR");
      const dateA = new Date(a.interactedAt || a.createdAt).getTime();
      const dateB = new Date(b.interactedAt || b.createdAt).getTime();
      return sortBy === "oldest" ? dateA - dateB : dateB - dateA;
    });
  }, [lists, originFilter, sortBy]);

  const handleSaveList = (data) => {
    if (editingList) {
      setLists((prev) =>
        prev.map((l) => (l.id === editingList.id ? { ...l, ...data } : l))
      );
      setEditingList(null);
    } else {
      const now = new Date().toISOString();
      const newList = {
        id: String(Date.now()),
        detailPath: "/lists",
        ...data,
        author: username || "gamer123",
        isOwner: true,
        likes: 0,
        createdAt: now,
        interactedAt: now,
      };
      setLists((prev) => [newList, ...prev]);
    }
  };

  const openCreateModal = () => {
    setEditingList(null);
    setModalOpen(true);
  };

  const openEditModal = (list) => {
    setEditingList(list);
    setModalOpen(true);
  };

  return (
    <div className="flex flex-col gap-6 min-w-6xl">
      <EditListModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingList(null);
        }}
        onSave={handleSaveList}
        initialData={editingList}
      />

      {/* Cabeçalho da seção + Controles de Filtro (Origem e Exibição) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <h2 className="text-white/75 text-xl font-medium">Suas Listas</h2>

        <div className="flex flex-wrap items-center gap-3">
          {/* Filtro 1: Origem */}
          <div className="flex items-center gap-1.5 bg-neutral-800/90 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs">
            <Filter className="w-3.5 h-3.5 text-purple-400" />
            <span className="text-white/50">Origem:</span>
            <select
              value={originFilter}
              onChange={(e) => setOriginFilter(e.target.value)}
              className="bg-transparent text-white outline-none cursor-pointer"
            >
              <option value="all" className="bg-neutral-800">Todas as listas</option>
              <option value="created" className="bg-neutral-800">Criadas por você</option>
              <option value="liked" className="bg-neutral-800">Listas curtidas</option>
            </select>
          </div>

          {/* Filtro 2: Exibição (Ordenação) */}
          <div className="flex items-center gap-1.5 bg-neutral-800/90 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs">
            <ArrowUpDown className="w-3.5 h-3.5 text-purple-400" />
            <span className="text-white/50">Exibição:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-transparent text-white outline-none cursor-pointer"
            >
              <option value="recent" className="bg-neutral-800">Mais recentes (criação/curtida)</option>
              <option value="oldest" className="bg-neutral-800">Mais antigas</option>
              <option value="alpha-asc" className="bg-neutral-800">Ordem alfabética (A–Z)</option>
              <option value="alpha-desc" className="bg-neutral-800">Ordem alfabética (Z–A)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Lista vertical das coleções  */}
      <div className="flex flex-col gap-6">
        {filteredAndSortedLists.length > 0 ? (
          filteredAndSortedLists.map((list) => {
            const targetPath = list.detailPath || "/lists";
            return (
              <div key={list.id} className="flex flex-col gap-2">
                <div className="flex items-center gap-2">
                  <Link
                    to={targetPath}
                    className="text-white/80 hover:text-purple-400 text-sm font-medium transition-colors"
                  >
                    {list.name}
                  </Link>
                  {!list.isOwner && (
                    <span className="text-[11px] bg-purple-500/20 text-purple-300 border border-purple-500/30 px-2 py-0.5 rounded-full">
                      Curtida · @{list.author}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-4">
                  <Link to={targetPath}>
                    <OverlappingCovers games={list.games} />
                  </Link>

                  {/* Metadados laterais (Público/Privado, Curtidas, X jogos + Lápis) */}
                  <div className="flex flex-col gap-2 text-xs text-white/60">
                    <div className="flex items-center gap-1.5">
                      {list.isPublic ? (
                        <>
                          <Eye className="w-3.5 h-3.5 text-white/60" />
                          <span>Pública</span>
                        </>
                      ) : (
                        <>
                          <EyeOff className="w-3.5 h-3.5 text-white/40" />
                          <span>Privada</span>
                        </>
                      )}
                    </div>

                    <div className="flex items-center gap-1.5">
                      <Heart className="w-3.5 h-3.5 text-red-500 fill-red-500" />
                      <span>{formatLikes(list.likes)}</span>
                    </div>

                    <div className="flex items-center gap-2.5">
                      <span>{list.games.length} jogos</span>
                      {list.isOwner && (
                        <button
                          type="button"
                          onClick={() => openEditModal(list)}
                          title="Editar lista"
                          className="text-white/60 hover:text-white transition-colors"
                        >
                          <Pencil className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <p className="text-white/40 text-sm py-8 text-center">
            Nenhuma lista encontrada.
          </p>
        )}
      </div>

      {/* Botão "Adicionar Lista" alinhado à direita */}
      <div className="flex justify-end pt-4">
        <button
          type="button"
          onClick={openCreateModal}
          className="bg-neutral-500/70 hover:bg-purple-600 text-white text-sm font-medium px-5 py-2.5 rounded-md transition-colors shadow"
        >
          Adicionar Lista
        </button>
      </div>
    </div>
  );
}