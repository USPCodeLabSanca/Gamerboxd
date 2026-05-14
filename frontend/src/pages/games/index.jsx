import React from "react";

export default function Games() {
    return (
        <div className="h-screen bg-linear-to-b from-cinza to-black">
            <div>
                <Filter />
                <Search />
            </div>
            <PopularGames />
            <PopularReviews />
        </div>
    );
}

function Filter () {

    const filters = [
        {name: "Ano"},
        {name: "Rating"},
        {name: "Gênero"},
        {name: "Plataforma"},
        {name: "Serviços"},
        {name: "Outro"}
    ]

    return (
        <div className="flex flex-row gap-2 items-center">
            <span className="text-white">Filtre por</span>
            <div className="rounded-2xl bg-white px-4 py-2 w-[30%] flex flex-row items-center justify-around">
                {filters.map((filter) => (
                    <button key={filter.name} className="bg-transparent">{filter.name}</button>
                ))}
            </div>
        </div>
    )
}

function Search (){

}

function PopularGames () {

}

function PopularReviews () {
    
}