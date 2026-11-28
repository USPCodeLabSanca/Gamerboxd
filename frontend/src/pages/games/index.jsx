import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Card from "../../components/gameCard";

import { useGames, useAllGames } from "../../hooks/useGames";
import { toCardGame } from "../../services/gameService";

import { sortGames, inDecade } from "../../utils/gameFilters";

const PAGE_SIZE = 15;


function useDebounce(value, delay = 400) {
    const [debounced, setDebounced] = useState(value);

    useEffect(() => {
        const t = setTimeout(() => setDebounced(value), delay);
        return () => clearTimeout(t);
    }, [value, delay]);

    return debounced;
}


const FILTERS = [
    { key: "year", name: "Ano", kind: "sort", options: [
        { label: "Mais novos primeiro", value: "year:desc" },
        { label: "Mais antigos primeiro", value: "year:asc" },
    ] },
    { key: "rating", name: "Rating", kind: "sort", description: "Média das notas de todas as reviews de cada jogo.", options: [
        { label: "Melhores primeiro", value: "rating:desc" },
        { label: "Piores primeiro", value: "rating:asc" },
    ] },
    { key: "likes", name: "Curtidas", kind: "sort", description: "Quantidade de pessoas que marcaram que curtiram o jogo nas reviews.", options: [
        { label: "Mais curtidos primeiro (jogo)", value: "likes:desc" },
    ] },
    { key: "reviews", name: "Avaliações", kind: "sort", unavailable: "Mais avaliados por curtidas nas reviews: indisponível. A API não retorna o total dessas curtidas por jogo.", options: [
        { label: "Mais avaliados primeiro (curtidas nas reviews)", value: "reviewLikes:desc", disabled: true },
        { label: "Maior quantidade de reviews", value: "reviews:desc" },
    ] },
    { key: "completed", name: "Completados", kind: "sort", description: "Marcações de completado nas reviews de todos os usuários. Não inclui jogos adicionados diretamente às listas.", options: [
        { label: "Mais completados primeiro", value: "completed:desc" },
    ] },
    { key: "decade", name: "Década", kind: "decade", options: [
        { label: "Anos 2020", value: 2020 },
        { label: "Anos 2010", value: 2010 },
        { label: "Anos 2000", value: 2000 },
        { label: "Anos 1990", value: 1990 },
        { label: "Anos 80 e antes", value: 1980 },
    ] },
];


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
                <PopularReviews />
            </div>
        );
    }

    return (
        <div className="bg-linear-to-b from-cinza to-black pt-28 pl-20 pr-20 min-h-screen">
            <div className="flex flex-row items-center justify-between">
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

    const idle = "bg-transparent hover:cursor-pointer hover:scale-105 hover:text-roxo transition-all relative overflow-hidden after:content-[''] after:absolute after:-bottom-2 after:left-0 after:w-0 after:h-0.5 duration-300 after:bg-roxo hover:after:w-full";

    const selectedOf = (filter) =>
        filter.kind === "decade" ? decade : (sort?.startsWith(`${filter.key}:`) ? sort : null);

    function pick(filter, value) {
        if (filter.kind === "decade") onDecade(value);
        else onSort(value);   
        setOpen(null);
    }

    return (
        <div className="flex flex-row gap-2 items-center w-full">
            <span className="text-white font-semibold text-2xl">Filtrar por:</span>
            <div className="rounded-2xl text-white/80 px-4 py-2 min-w-min gap-2 flex flex-row items-center">
                {FILTERS.map((filter) => {
                    const selected = selectedOf(filter);
                    const selectedLabel = filter.options.find((o) => o.value === selected)?.label;

                    return (
                        <div key={filter.key} className="relative">
                            <button
                                className={selected !== null ? "text-roxo scale-105" : idle}
                                onClick={() => setOpen(open === filter.key ? null : filter.key)}
                            >
                                {selectedLabel ? `${filter.name}: ${selectedLabel}` : filter.name}
                            </button>

                            {open === filter.key && (
                                <ul className="absolute z-20 mt-3 max-h-64 overflow-y-auto min-w-52 rounded-lg bg-neutral-800 py-1 shadow-lg">
                                    {selected !== null && (
                                        <li>
                                            <button
                                                className="w-full text-left px-4 py-2 text-sm text-white/60 hover:bg-roxo hover:text-white cursor-pointer"
                                                onClick={() => pick(filter, null)}
                                            >
                                                Limpar
                                            </button>
                                        </li>
                                    )}
                                    {(filter.unavailable || filter.description) && <li className="px-4 py-2 text-sm text-white/60">{filter.unavailable || filter.description}</li>}
                                    {filter.options.map((o) => (
                                        <li key={o.value}>
                                            <button
                                                className={`w-full text-left px-4 py-2 text-sm hover:bg-roxo hover:text-white cursor-pointer ${o.value === selected ? "text-roxo" : "text-white"}`}
                                                disabled={!!o.disabled}
                                                onClick={() => pick(filter, o.value)}
                                            >
                                                {o.label}
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    )
                })}

                {hasFilter && (
                    <button onClick={onClear} className="text-sm text-white/60 hover:text-white cursor-pointer ml-2">
                        Limpar filtros
                    </button>
                )}
            </div>
        </div>
    )
}

function Search({ value, onChange }) {
    return (
        <div>
            <input
                type="text"
                placeholder="Buscar"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="bg-white/80 rounded-2xl px-4 py-2"
            />
        </div>
    )
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

            {!isLoading && !isError && games.length > 0 && (
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
            title={isLoading ? "Carregando todos os resultados para filtrar..." : isError ? "Não foi possível carregar todos os resultados para filtrar" : `Jogos (${filtered.length}) — todos os resultados da busca carregados`}
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

function PopularReviews() {
    return (
        <div className="mb-10 text-white">
            <div className="mt-20 w-full border-b border-white py-2"><p className="text-sm">Avaliações populares da semana</p></div>
            <p className="mt-4 text-white/60">As avaliações em destaque estarão disponíveis em breve.</p>
        </div>
    );
}
