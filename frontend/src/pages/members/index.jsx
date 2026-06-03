import React from "react";
import MemberCard from "../../components/MemberCard";
import { formatNumber } from "../../utils/formatters";
import { useNavigate } from "react-router-dom";
import { popularMembers } from "../../mocks//popularMembers";
import { members } from "../../mocks/members";

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
  const navigate = useNavigate()

  const animatedLink =
    "text-white text-sm hover:cursor-pointer relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-4 py-1 rounded-2xl";

  return (
    <section>
      <div className="border-b border-zinc-700 flex items-center justify-between pb-2">
        <p className="text-white text-sm">
          Membros mais populares essa semana
        </p>

        <button className={animatedLink} onClick={() => navigate("/members/all")}>
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

  const navigate = useNavigate()

  return (
    <section className="mt-16">
      <div className="border-b border-zinc-700 flex items-center justify-between pb-2 mb-4">
        <p className="text-white text-sm">
          Todos os membros
        </p>
      </div>

      <div className="flex flex-col">
        {members.slice(0, 8).map((player) => (
          <MemberCard
            key={player.id}
            player={player}
          />
        ))}
      </div>

      <div className="flex justify-center mt-10 pb-12">
        <button className={buttonStyle} onClick={() => navigate("/members/all")}>
          Ver mais
        </button>
      </div>
    </section>
  );
}
