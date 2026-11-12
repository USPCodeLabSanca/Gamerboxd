import React, { useState } from "react";
import Card from "../../components/gameCard";
import Review from "../../components/gameReview";
import { useGames } from "../../hooks/useGames";

export default function Games() {
    const [search, setSearch] = useState("");
    const [page, setPage] = useState(1);
    const query = useGames(search, page);
    const games = (query.data?.games ?? []).map((game) => ({id: game.game_id, title: game.title, url: game.picture}));

    function handleSearch(value) {
        setSearch(value);
        setPage(1);
    }

    return (
        <div className="bg-linear-to-b from-cinza to-black pt-28 pl-20 pr-20">
            <div className="flex flex-row items-center justify-between">
                <Filter />
                <Search value={search} onChange={handleSearch} />
            </div>
            <div className="flex flex-col">
                {query.isPending && <p className="text-white mt-10">Carregando jogos...</p>}
                {query.data?.count === 0 && <p className="text-white mt-10">Nenhum jogo encontrado.</p>}
                {games.length > 0 && <PopularGames games={games} />}
                <div className="flex gap-6 text-white mt-6">
                    <button disabled={page === 1 || query.isFetching} onClick={() => setPage(page - 1)}>Anterior</button>
                    <span>Página {page}</span>
                    <button disabled={!query.data || query.data.count < 20 || query.isFetching} onClick={() => setPage(page + 1)}>Próxima</button>
                </div>
                {games.length > 0 && <PopularReviews game={games[0]} />}
            </div>
        </div>
    );
}

function Filter () {
    const [activeFilter, setActiveFilter] = useState(null);

    const filters = [
        {name: "Ano"},
        {name: "Rating"},
        {name: "Gênero"},
        {name: "Plataforma"},
        {name: "Serviços"},
        {name: "Outro"}
    ]

    return (
        <div className="flex flex-row gap-2 items-center w-full">
            <span className="text-white font-semibold text-2xl">Filtrar por:</span>
            <div className="rounded-2xl text-white/80 px-4 py-2 min-w-min gap-2 flex flex-row items-center justify-aroun">
                {filters.map((filter) => {
                    const isSelected = activeFilter === filter.name;

                    return (
                        <button 
                        key={filter.name} 
                            className={isSelected ? "text-roxo scale-105" : "bg-transparent hover:cursor-pointer hover:scale-105 hover:text-roxo transition-all relative overflow-hidden after:content-[''] after:absolute after:-bottom-2 after:left-0 after:w-0 after:h-0.5 duration-300 after:bg-roxo hover:after:w-full"}
                        onClick={() => setActiveFilter(filter.name)}
                        >
                            {filter.name}
                        </button>
                    )
                })}
            </div>
        </div>
    )
}

function Search ({value, onChange}){
    return (
        <div>
            <input 
                type="text" 
                placeholder="Buscar"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="bg-white/80 rounded-2xl px-4 py-2"
                ></input>
        </div>
    )
}

function PopularGames ({games}) {

    const animatedLink = "text-white text-sm hover:cursor-pointer relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-4 py-1 rounded-2xl"
   
    return (
        <div>
            <div className="mt-10 w-full border-b border-white flex flex-row items-center justify-between py-2 mb-4">
                <p className="text-white text-sm">Jogos populares da semana</p>
                <a 
                className={animatedLink}
                >Todos os jogos</a>
            </div>

            {/* O TABULEIRO (Grid Principal de 5 Colunas) */}
            <div className="grid grid-cols-6 gap-6 w-full">
                <div className="col-span-2 row-span-2 mt-2">
                    <Card game={games[0]} status={false}/>
                </div>
                {games.map((game) => {
                    return (
                       <Card key={game.id} game={game} status={false}/>
                    )
                })}

            </div>
            
        </div>
    )
}

function PopularReviews ({game}) {

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
                {reviews.map((review) => {
                    return (
                        <Review key={review.id} review={review} game={game} gameClassName="w-40" />
                    )
                })}
            </div>
        </div>
    )
}
