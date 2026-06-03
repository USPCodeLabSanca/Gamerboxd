import React, { useState } from "react";
import Card from "../../components/gameCard";
import Review from "../../components/gameReview";
import gtaImg from "../../assets/imgs/gta.png"
import gowImg from "../../assets/imgs/ragnarok.png"
import silksongImg from "../../assets/imgs/silksong.png"
import rdr2Img from "../../assets/imgs/rdr2.jpg"
import cyberpunkImg from "../../assets/imgs/cyberpunk2077.png"
import clairImg from "../../assets/imgs/clair-obscure.png"

export default function Games() {
    return (
        <div className="bg-linear-to-b from-cinza to-black pt-28 pl-20 pr-20">
            <div className="flex flex-row items-center justify-between">
                <Filter />
                <Search />
            </div>
            <div className="flex flex-col">
                <PopularGames games={smallGames}/>
                <PopularReviews />
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
            <span className="text-white font-semibold text-2xl">Filtrar por</span>
            <div className="rounded-2xl border-b border-l border-roxo text-white/80 px-4 py-2 min-w-min gap-2 flex flex-row items-center justify-around">
                {filters.map((filter) => {
                    const isSelected = activeFilter === filter.name;

                    return (
                        <button 
                        key={filter.name} 
                        className={isSelected ? "text-roxo scale-105" : "bg-transparent hover:cursor-pointer hover:scale-105 hover:text-roxo transition-transform"}
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

function Search (){
    return (
        <div>
            <input 
                type="text" 
                placeholder="Buscar"
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
                    <Card game={games[0]} status={true}/>
                </div>
                {games.map((game) => {
                    return (
                       <Card key={game.id} game={game} status={true}/>
                    )
                })}

            </div>
            
        </div>
    )
}

function PopularReviews () {

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
                        <Review key={review.id} review={review} game={smallGames[0]} gameClassName="w-40" />
                    )
                })}
            </div>
        </div>
    )
}

const smallGames = [
        { id: 1, title: "GTA VI", url: gtaImg, jogou: true, liked: true, nota: 5, complete: true    },
        { id: 2, title: "God of War", url: gowImg, jogou: true, liked: true, nota: 5, complete: true },
        { id: 3, title: "God of War II", url: rdr2Img, jogou: true, liked: true, nota: 5, complete: true },
        { id: 4, title: "Silksong Small", url: silksongImg, jogou: true, liked: true, nota: 4.5, complete: true },
        { id: 5, title: "Expedition 33", url: clairImg, jogou: true, liked: true, nota: 4.5, complete: true },
        { id: 6, title: "Expedition 33 II", url: cyberpunkImg, jogou: true, liked: true, nota: 3.5, complete: true },
        { id: 7, title: "Expedition 33 II", url: cyberpunkImg, jogou: true, liked: true, nota: 3.5, complete: true },
        { id: 8, title: "Expedition 33 II", url: cyberpunkImg, jogou: true, liked: true, nota: 3.5, complete: true },
    ];