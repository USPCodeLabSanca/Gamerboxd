import React from "react";
import MemberCard from "../../components/MemberCard";
import { formatNumber } from "../../utils/formatters";

const popularMembers = [
  {
    id: 1,
    name: "Lucas Silva",
    gamesPlayed: 427,
    reviews: 892,
    profilePicture: "https://i.pravatar.cc/300?img=11",
  },
  {
    id: 2,
    name: "Mariana Costa",
    gamesPlayed: 381,
    reviews: 754,
    profilePicture: "https://i.pravatar.cc/300?img=5",
  },
  {
    id: 3,
    name: "Pedro Oliveira",
    gamesPlayed: 502,
    reviews: 1203,
    profilePicture: "https://i.pravatar.cc/300?img=15",
  },
  {
    id: 4,
    name: "Ana Santos",
    gamesPlayed: 295,
    reviews: 611,
    profilePicture: "https://i.pravatar.cc/300?img=20",
  },
  {
    id: 5,
    name: "João Ribeiro",
    gamesPlayed: 613,
    reviews: 1460,
    profilePicture: "https://i.pravatar.cc/300?img=33",
  },
  {
    id: 6,
    name: "Beatriz Lima",
    gamesPlayed: 348,
    reviews: 723,
    profilePicture: "https://i.pravatar.cc/300?img=47",
  },
];

const membersList = [
  {
    id: 7,
    name: "Gabriel Almeida",
    gamesPlayed: 100,
    reviews: 55,
    likes: 5000,
    profilePicture: "https://i.pravatar.cc/300?img=8",
  },
  {
    id: 8,
    name: "Carla Mendes",
    gamesPlayed: 164,
    reviews: 89,
    likes: 251,
    profilePicture: "https://i.pravatar.cc/300?img=24",
  },
  {
    id: 9,
    name: "Felipe Rocha",
    gamesPlayed: 1000,
    reviews: 708,
    likes: 900,
    profilePicture: "https://i.pravatar.cc/300?img=59",
  },
  {
    id: 10,
    name: "Juliana Martins",
    gamesPlayed: 78,
    reviews: 31,
    likes: 85,
    profilePicture: "https://i.pravatar.cc/300?img=32",
  },
  {
    id: 11,
    name: "Rafael Costa",
    gamesPlayed: 1050,
    reviews: 500,
    likes: 10000,
    profilePicture: "https://i.pravatar.cc/300?img=68",
  },
  {
    id: 12,
    name: "Larissa Gomes",
    gamesPlayed: 147,
    reviews: 98,
    likes: 184,
    profilePicture: "https://i.pravatar.cc/300?img=44",
  },
  {
    id: 13,
    name: "Thiago Ferreira",
    gamesPlayed: 404,
    reviews: 287,
    likes: 912,
    profilePicture: "https://i.pravatar.cc/300?img=52",
  },
  {
    id: 14,
    name: "Camila Souza",
    gamesPlayed: 126,
    reviews: 74,
    likes: 143,
    profilePicture: "https://i.pravatar.cc/300?img=36",
  },
];

export default function Members() {
  return (
    <div className="min-h-screen bg-linear-to-b from-cinza to-black pt-24 md:pt-32 px-4 sm:px-6 md:px-10 lg:px-20">
      <h1 className="text-center text-2xl md:text-3xl lg:text-4xl text-white font-semibold mb-12 max-w-4xl mx-auto">
        Amantes de jogos, críticos e amigos — encontre os membros mais populares essa semana
      </h1>

      <div className="flex flex-col">
        <PopularMembers />
        <MembersList />
      </div>
    </div>
  );
}

function PopularMembers() {
  const animatedLink =
    "text-white text-sm hover:cursor-pointer relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-4 py-1 rounded-2xl";

  return (
    <section>
      <div className="border-b border-zinc-700 flex items-center justify-between pb-2">
        <p className="text-white text-sm">
          Membros mais populares essa semana
        </p>

        <button className={animatedLink}>
          Mostrar mais
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-6 md:gap-8 mt-8">
        {popularMembers.map((player) => (
          <div
            key={player.id}
            className="flex flex-col items-center text-center hover:scale-105 transition-transform duration-300"
          >
            <img
              src={player.profilePicture}
              alt={player.name}
              className="w-24 h-24 md:w-32 md:h-32 rounded-full object-cover border-4 border-zinc-700 shadow-lg"
            />

            <h3 className="text-white font-semibold text-sm md:text-base mt-4">
              {player.name}
            </h3>

            <p className="text-zinc-400 text-sm">
              <span>{formatNumber(player.gamesPlayed)}</span> jogos • <span>{formatNumber(player.reviews)}</span> reviews
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

function MembersList() {
  const buttonStyle =
    "text-white font-medium relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-6 md:px-8 py-3 rounded-full border border-zinc-700 cursor-pointer";

  return (
    <section className="mt-16">
      <div className="border-b border-zinc-700 flex items-center justify-between pb-2 mb-4">
        <p className="text-white text-sm">
          Todos os membros
        </p>
      </div>

      <div className="flex flex-col">
        {membersList.map((player) => (
          <MemberCard
            key={player.id}
            player={player}
          />
        ))}
      </div>

      <div className="flex justify-center mt-10 pb-12">
        <button className={buttonStyle}>
          Ver mais
        </button>
      </div>
    </section>
  );
}
