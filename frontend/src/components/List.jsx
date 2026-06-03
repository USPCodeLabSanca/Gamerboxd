import React from "react";
import { Link } from "react-router-dom";

// Componente de pilha de capas
const GameStackCover = ({ games }) => {
    const visible = games.slice(0, 4);

    return (
        <div className="relative h-24 w-36 shrink-0">
            {visible.map((game, i) => (
                <div
                    key={game.id}
                    className="absolute rounded-xl overflow-hidden border border-white/10 shadow-lg"
                    style={{
                        left: `${i * 18}px`,
                        top: `${i * 3}px`,
                        width: "72px",
                        height: "90px",
                        zIndex: visible.length - i,
                        transform: `rotate(${(i - 1) * 3}deg)`,
                        filter: i > 0 ? `brightness(${1 - i * 0.15})` : "brightness(1)",
                    }}
                >
                    <img
                        src={game.url}
                        alt={game.title}
                        className="h-full w-full object-cover"
                    />
                </div>
            ))}
        </div>
    );
};

// Item individual de lista
const ListItem = ({ list }) => {
    return (
        <Link
            to={`/lists/${list.id}`}
            className="group flex items-center gap-5 py-3 border-b border-white/5 hover:border-roxo/40 transition-colors duration-300"
        >
            <GameStackCover games={list.games} />

            <div className="flex flex-col gap-1 min-w-0">
                <span className="text-white font-semibold text-sm sm:text-base group-hover:text-roxo transition-colors duration-200 truncate">
                    {list.name}
                </span>
                <span className="text-white/40 text-xs">
                    {list.games.length} {list.games.length === 1 ? "jogo" : "jogos"}
                    {list.author && (
                        <> · por <span className="text-white/60">{list.author}</span></>
                    )}
                </span>
            </div>

            {/* Seta hover */}
            <span className="ml-auto text-white/20 group-hover:text-roxo group-hover:translate-x-1 transition-all duration-200 text-lg">
                →
            </span>
        </Link>
    );
};

// Componente principal
export default function List({ title, lists = [] }) {
    if (!lists.length) return null;

    return (
        <section className="w-full">
            {/* Cabeçalho da seção */}
            <div className="flex items-center gap-3 mb-4">
                <h2 className="text-white font-bold text-base sm:text-lg whitespace-nowrap">
                    {title}
                </h2>
                <div className="flex-1 h-px bg-white/10" />
            </div>

            {/* Lista de listas */}
            <div className="flex flex-col">
                {lists.map((list) => (
                    <ListItem key={list.id} list={list} />
                ))}
            </div>
        </section>
    );
}