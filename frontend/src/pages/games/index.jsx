import React, { useState } from "react";
import Card from "../../components/gameCard";
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
                <PopularGames />
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

function PopularGames () {

    const animatedLink = "text-white text-sm hover:cursor-pointer relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-4 py-1 rounded-2xl"

    const smallGames = [
        { id: 1, title: "GTA VI", url: gtaImg },
        { id: 2, title: "God of War", url: gowImg },
        { id: 3, title: "God of War II", url: rdr2Img },
        { id: 4, title: "Silksong Small", url: silksongImg },
        { id: 5, title: "Expedition 33", url: clairImg },
        { id: 6, title: "Expedition 33 II", url: cyberpunkImg },
    ];
   

    return (
        <div>
            <div className="mt-20 w-full border-b border-white flex flex-row items-center justify-between py-2 mb-4">
                <p className="text-white text-sm">Jogos populares da semana</p>
                <a 
                className={animatedLink}
                >Todos os jogos</a>
            </div>

            {/* O TABULEIRO (Grid Principal de 5 Colunas) */}
            <div className="grid grid-cols-5 gap-4">
                <div className="col-span-2 row-span-2">
                    <Card card={smallGames[0]}/>
                </div>
                {smallGames.map((game) => {
                    return (
                       <Card card={game}/>
                    )
                })}

            </div>
            
        </div>
    )
}

function PopularReviews () {

    const animatedLink = "text-white text-sm hover:cursor-pointer relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-4 py-1 rounded-2xl"

    return (
        <div>
            <div className="mt-20 w-full border-b border-white flex flex-row items-center justify-between py-2">
                <p className="text-white text-sm">Avaliações populares da semana</p>
                <a
                    className={animatedLink}
                >Todas as Avaliações</a>
            </div>
        </div>
    )
}