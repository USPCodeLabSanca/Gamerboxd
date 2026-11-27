import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import Card from "../../components/gameCard";
import Review from "../../components/gameReview";
import { useGames, useAllGames } from "../../hooks/useGames";
import { toCardGame } from "../../services/gameService";

const PAGE_SIZE = 15;


function useDebounce(value, delay = 400) {
    const [debounced, setDebounced] = useState(value);

    useEffect(() => {
        const t = setTimeout(() => setDebounced(value), delay);
        return () => clearTimeout(t);
    }, [value, delay]);

    return debounced;
}


const getYear = (g) => {
    const y = parseInt(String(g.year ?? "").slice(0, 4));
    return Number.isNaN(y) ? null : y;
};

const getters = {
    year: getYear,
    rating: (g) => g.gamerboxd_rating ?? null,
    likes: (g) => g.like_count ?? null,
    reviews: (g) => g.review_count ?? null,
};


const FILTERS = [
    { key: "year", name: "Ano", kind: "sort", options: [
        { label: "Mais novos", value: "year:desc" },
        { label: "Mais antigos", value: "year:asc" },
    ] },
    { key: "rating", name: "Rating", kind: "sort", options: [
        { label: "Melhores", value: "rating:desc" },
        { label: "Piores", value: "rating:asc" },
    ] },
    { key: "likes", name: "Curtidas", kind: "sort", options: [
        { label: "Mais curtidos", value: "likes:desc" },
    ] },
    { key: "reviews", name: "Avaliações", kind: "sort", options: [
        { label: "Mais avaliados", value: "reviews:desc" },
    ] },
    { key: "decade", name: "Década", kind: "decade", options: [
        { label: "Anos 2020", value: 2020 },
        { label: "Anos 2010", value: 2010 },
        { label: "Anos 2000", value: 2000 },
        { label: "Anos 1990", value: 1990 },
        { label: "Anos 80 e antes", value: 1980 },
    ] },
];


function sortGames(games, sort) {
    if (!sort) return games;

    const [field, dir] = sort.split(":");
    const get = getters[field];
    const mult = dir === "asc" ? 1 : -1;

    return [...games].sort((a, b) => {
        const va = get(a), vb = get(b);
        if (va === null && vb === null) return 0;
        if (va === null) return 1;
        if (vb === null) return -1;
        return (va - vb) * mult;
    });
}

function inDecade(game, decade) {
    const y = getYear(game);
    if (y === null) return false;
    return decade === 1980 ? y < 1990 : y >= decade && y < decade + 10;
}

export default function Games() {
    const [search, setSearch] = useState("");
    const [showAll, setShowAll] = useState(false);
    const [sort, setSort] = useState(null);      
    const [decade, setDecade] = useState(null);  

    const debouncedSearch = useDebounce(search.trim(), 400);
    const searching = debouncedSearch !== "";
    const hasFilter = sort !== null || decade !== null;

    // busca vazia = jogos mais populares
    const { data: popular } = useGames({ pageSize: 8 });
    const popularGames = (popular?.games ?? []).map(toCardGame);

    const clearFilters = () => {
        setSort(null);
        setDecade(null);
    };

    let content;
    if (hasFilter) {
        content = (
            <FilteredGrid
                key={`${debouncedSearch}|${sort}|${decade}`}
                search={debouncedSearch}
                sort={sort}
                decade={decade}
                onBack={searching ? undefined : clearFilters}
            />
        );
    } else if (searching) {
        content = (
            <GameGrid
                key={debouncedSearch}
                search={debouncedSearch}
                title={`Resultados para "${debouncedSearch}"`}
            />
        );
    } else if (showAll) {
        content = <GameGrid key="all" title="Todos os jogos" onBack={() => setShowAll(false)} />;
    } else {
        content = (
            <div className="flex flex-col">
                <PopularGames games={popularGames} onShowAll={() => setShowAll(true)} />
                <PopularReviews game={popularGames[0]} />
            </div>
        );
    }

    return (
        <div className="bg-linear-to-b from-cinza to-black pt-28 pl-20 pr-20 min-h-screen">
            <div className="flex flex-wrap items-center justify-between gap-4">
                <Filter
                    sort={sort}
                    decade={decade}
                    onSort={setSort}
                    onDecade={setDecade}
                    onClear={clearFilters}
                    hasFilter={hasFilter}
                />
                <Search value={search} onChange={setSearch} />
            </div>

            {content}
        </div>
    );
}

function Filter({ sort, decade, onSort, onDecade, onClear, hasFilter }) {
    const [open, setOpen] = useState(null);
    const barRef = useRef(null);

    // fecha o menu ao clicar fora ou apertar Esc
    useEffect(() => {
        if (open === null) return;

        const onDown = (e) => {
            if (!barRef.current?.contains(e.target)) setOpen(null);
        };
        const onKey = (e) => {
            if (e.key === "Escape") setOpen(null);
        };

        document.addEventListener("mousedown", onDown);
        document.addEventListener("keydown", onKey);
        return () => {
            document.removeEventListener("mousedown", onDown);
            document.removeEventListener("keydown", onKey);
        };
    }, [open]);

    const selectedOf = (filter) =>
        filter.kind === "decade" ? decade : (sort?.startsWith(`${filter.key}:`) ? sort : null);

    function pick(filter, value) {
        if (filter.kind === "decade") onDecade(value);
        else onSort(value);
        setOpen(null);
    }

    const item = "flex h-full items-center gap-1.5 px-4 py-2 text-xs font-medium uppercase tracking-wider cursor-pointer transition-colors duration-200";
    const itemIdle = "text-white/80 hover:bg-white/10 hover:text-white";
    const itemActive = "bg-roxo font-semibold text-white";

    return (
        <div ref={barRef} className="flex flex-wrap items-center gap-3">
            <span className="text-sm text-white/60">Filtrar por</span>

            <div className="flex items-stretch divide-x divide-white/15 rounded-md bg-neutral-700/80 ring-1 ring-white/10">
            {FILTERS.map((filter, i) => {
                const selected = selectedOf(filter);
                const isOpen = open === filter.key;

                return (
                    <div key={filter.key} className="relative">
                        <button
                            className={`${item} ${selected !== null ? itemActive : itemIdle} ${i === 0 ? "rounded-l-md" : ""} ${i === FILTERS.length - 1 ? "rounded-r-md" : ""}`}
                            onClick={() => setOpen(isOpen ? null : filter.key)}
                            aria-expanded={isOpen}
                        >
                            {filter.name}
                            <svg
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2.5"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                aria-hidden="true"
                                className={`h-3 w-3 transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
                            >
                                <path d="m6 9 6 6 6-6" />
                            </svg>
                        </button>

                        {isOpen && (
                            <ul className="absolute left-0 top-full z-30 mt-1 max-h-64 min-w-48 overflow-y-auto rounded-md bg-neutral-700/95 py-1 shadow-xl ring-1 ring-white/10 backdrop-blur">
                                {filter.options.map((o) => {
                                    const isSelected = o.value === selected;

                                    return (
                                        <li key={o.value}>
                                            <button
                                                className={`flex w-full cursor-pointer items-center justify-between gap-3 px-4 py-2 text-left text-sm transition-colors hover:bg-roxo hover:text-white ${isSelected ? "bg-roxo font-semibold text-white" : "text-white"}`}
                                                onClick={() => pick(filter, o.value)}
                                            >
                                                {o.label}
                                                {isSelected && (
                                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className="h-4 w-4">
                                                        <path d="M20 6 9 17l-5-5" />
                                                    </svg>
                                                )}
                                            </button>
                                        </li>
                                    );
                                })}

                                {selected !== null && (
                                    <li className="mt-1 border-t border-white/15 pt-1">
                                        <button
                                            className="w-full cursor-pointer px-4 py-2 text-left text-sm text-white/60 transition-colors hover:bg-white/10 hover:text-white"
                                            onClick={() => pick(filter, null)}
                                        >
                                            Limpar
                                        </button>
                                    </li>
                                )}
                            </ul>
                        )}
                    </div>
                );
            })}
            </div>

            {hasFilter && (
                <button
                    onClick={onClear}
                    className="flex cursor-pointer items-center gap-1.5 text-base font-medium text-white/80 transition-colors hover:text-white"
                >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className="h-4 w-4">
                        <path d="M18 6 6 18M6 6l12 12" />
                    </svg>
                    Limpar filtros
                </button>
            )}
        </div>
    );
}

function Search({ value, onChange }) {
    return (
        <label className="relative block">
            <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
                className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/60"
            >
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
            </svg>
            <input
                type="text"
                placeholder="Buscar"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="w-64 rounded-2xl bg-white/10 py-2 pl-9 pr-4 text-sm text-white placeholder-white/50 outline-none ring-1 ring-white/10 transition focus:ring-2 focus:ring-roxo"
            />
        </label>
    );
}

function GameCard({ game }) {
    return (
        <Link to={`/games/${game.id}`}>
            <Card game={game} status={true} />
        </Link>
    );
}

function PopularGames({ games, onShowAll }) {

    const animatedLink = "text-white text-sm hover:cursor-pointer relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-4 py-1 rounded-2xl"

    return (
        <div>
            <div className="mt-10 w-full border-b border-white flex flex-row items-center justify-between py-2 mb-4">
                <p className="text-white text-sm">Jogos populares da semana</p>
                <button className={animatedLink} onClick={onShowAll}>
                    Todos os jogos
                </button>
            </div>

            {games.length > 0 && (
                <div className="grid grid-cols-6 gap-6 w-full">
                    <div className="col-span-2 row-span-2 mt-2">
                        <GameCard game={games[0]} />
                    </div>
                    {games.slice(1).map((game) => (
                        <GameCard key={game.id} game={game} />
                    ))}
                </div>
            )}
        </div>
    )
}

function GridView({ title, onBack, games, page, totalPages, onPage, isLoading, isError }) {
    const arrow = "text-white text-4xl px-4 py-2 rounded-full hover:bg-roxo transition-colors cursor-pointer disabled:opacity-30 disabled:hover:bg-transparent disabled:cursor-default";

    return (
        <div className="mt-10 pb-10">
            <div className="w-full border-b border-white flex flex-row items-center justify-between py-2 mb-6">
                <p className="text-white text-sm">{title}</p>
                {onBack && (
                    <button onClick={onBack} className="text-white text-sm cursor-pointer hover:text-roxo">
                        ← Voltar
                    </button>
                )}
            </div>

            {isLoading && <p className="text-white text-center">Carregando...</p>}
            {isError && <p className="text-white text-center">Erro ao carregar os jogos.</p>}
            {!isLoading && !isError && games.length === 0 && (
                <p className="text-white text-center">Nenhum jogo encontrado.</p>
            )}

            {!isLoading && games.length > 0 && (
                <div className="flex flex-row items-center gap-4">
                    <button className={arrow} disabled={page === 1} onClick={() => onPage(page - 1)}>
                        ‹
                    </button>

                    <div className="grid grid-cols-5 gap-6 flex-1">
                        {games.map((game) => (
                            <GameCard key={game.id} game={game} />
                        ))}
                    </div>

                    <button className={arrow} disabled={page >= totalPages} onClick={() => onPage(page + 1)}>
                        ›
                    </button>
                </div>
            )}

            <p className="text-white/70 text-sm text-center mt-6">
                Página {page} de {totalPages}
            </p>
        </div>
    )
}

function GameGrid({ search = "", title, onBack }) {
    const [page, setPage] = useState(1);

    const { data, isLoading, isError } = useGames({ search, page, pageSize: PAGE_SIZE });
    const games = (data?.games ?? []).map(toCardGame);
    const totalPages = Math.max(1, Math.ceil((data?.total ?? 0) / PAGE_SIZE));

    return (
        <GridView
            title={title}
            onBack={onBack}
            games={games}
            page={page}
            totalPages={totalPages}
            onPage={setPage}
            isLoading={isLoading}
            isError={isError}
        />
    )
}


function activeFilterLabels(sort, decade) {
    return FILTERS.flatMap((f) => {
        const value = f.kind === "decade" ? decade : (sort?.startsWith(`${f.key}:`) ? sort : null);
        if (value === null) return [];

        return [{ name: f.name, label: f.options.find((o) => o.value === value)?.label }];
    });
}

function ActiveFilters({ sort, decade }) {
    return (
        <span className="flex flex-wrap items-center gap-y-1">
            {activeFilterLabels(sort, decade).map(({ label }, i) => (
                <span key={label} className={i > 0 ? "ml-4 border-l border-white/20 pl-4" : ""}>
                    {label}
                </span>
            ))}
        </span>
    );
}

function FilteredGrid({ search, sort, decade, onBack }) {
    const [page, setPage] = useState(1);

    const { data: all = [], isLoading, isError } = useAllGames({ search });

    const filtered = sortGames(
        decade === null ? all : all.filter((g) => inDecade(g, decade)),
        sort
    );

    const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    const games = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE).map(toCardGame);

    return (
        <GridView
            title={<ActiveFilters sort={sort} decade={decade} />}
            onBack={onBack}
            games={games}
            page={page}
            totalPages={totalPages}
            onPage={setPage}
            isLoading={isLoading}
            isError={isError}
        />
    )
}

function PopularReviews({ game }) {

    const animatedLink = "text-white text-sm hover:cursor-pointer relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-4 py-1 rounded-2xl"

    const reviews = [
        { id: 1, complete: false, content: "Esse jogo é incrível! A história é envolvente e os gráficos são de tirar o fôlego. Recomendo para todos os fãs de jogos de ação.", author: { username: "Gamer123", avatar: "https://i.pravatar.cc/150?img=1" } },
        { id: 2, complete: false, content: "Não gostei muito desse jogo. Achei a jogabilidade confusa e a história fraca. Não recomendo.", author: { username: "Player456", avatar: "https://i.pravatar.cc/150?img=2" } },
        { id: 3, complete: true, content: "Esse jogo é mediano. Tem seus momentos bons, mas também tem muitos problemas técnicos. Vale a pena jogar se você for fã do gênero.", author: { username: "GameLover789", avatar: "https://i.pravatar.cc/150?img=3" } },
    ]

    return (
        <div className="mb-10">
            <div className="mt-20 w-full border-b border-white flex flex-row items-center justify-between py-2">
                <p className="text-white text-sm">Avaliações populares da semana</p>
                <a
                    className={animatedLink}
                >Mostrar mais</a>
            </div>
            <div className="flex flex-col gap-6 mt-4">
                {game && reviews.map((review) => {
                    return (
                        <Review key={review.id} review={review} game={game} gameClassName="w-40" />
                    )
                })}
            </div>
        </div>
    )
}