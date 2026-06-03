import React, { useState } from "react";
import MemberCard from "../../components/MemberCard";
import { formatNumber } from "../../utils/formatters";
import { members } from "../../mocks/members";
import { popularMembers } from "../../mocks/popularMembers";
import { ChevronDown } from "lucide-react";

export default function MembersListPage() {
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState("popularity");

  const membersPerPage = 10;

  const sortedMembers = [...members].sort((a, b) => {
    switch (sortBy) {
      case "reviews":
        return b.reviews - a.reviews;

      case "games":
        return b.gamesPlayed - a.gamesPlayed;

      case "likes":
        return b.likes - a.likes;

      default:
        return (b.likes + b.reviews) - (a.likes + a.reviews);
    }
  });

  const totalPages = Math.ceil(
    sortedMembers.length / membersPerPage
  );

  const paginatedMembers = sortedMembers.slice(
    (page - 1) * membersPerPage,
    page * membersPerPage
  );

  return (
    <div className="min-h-screen bg-linear-to-b from-cinza to-black pt-28 px-4 md:px-10 lg:px-20 pb-12">
      <div className="grid lg:grid-cols-[1fr_320px] gap-12">
        <MainContent
          paginatedMembers={paginatedMembers}
          page={page}
          totalPages={totalPages}
          setPage={setPage}
          sortBy={sortBy}
          setSortBy={setSortBy}
        />

        <SidebarPopularMembers />
      </div>
    </div>
  );
}

function MainContent({
  paginatedMembers,
  page,
  totalPages,
  setPage,
  sortBy,
  setSortBy,
}) {
  return (
    <section>
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-zinc-700 pb-3 mb-3">
        <h2 className="text-white tracking-wider text-m">
          Todos os membros
        </h2>

        <div className="relative w-full md:w-auto">
          <select
            value={sortBy}
            onChange={(e) => {
              setSortBy(e.target.value);
              setPage(1);
            }}
            className="
        w-full md:w-auto
        appearance-none
        bg-zinc-900
        text-white
        px-3 py-2
        pr-10
        rounded-md
        border border-zinc-700
        outline-none
      "
          >
            <option value="popularity">Popularidade</option>
            <option value="reviews">Reviews</option>
            <option value="games">Jogos</option>
            <option value="likes">Likes</option>
          </select>

          <ChevronDown
            size={22}
            className="
        absolute
        right-3
        top-1/2
        -translate-y-1/2
        text-roxo
        pointer-events-none
      "
          />
        </div>
      </div>

      <div className="flex flex-col">
        <div className="hidden md:flex items-center justify-between px-2 text-zinc-500 text-xs uppercase tracking-wider border-b border-zinc-700">

          <div className="flex items-center gap-4">
            <div className="w-10 h-10" />
            <span>Nome</span>
          </div>

          <div className="flex gap-4 md:gap-0 text-zinc-500 text-xs">
            <div className="w-24 flex items-center gap-2">
              Jogos
            </div>

            <div className="w-24 flex items-center gap-2">
              Reviews
            </div>

            <div className="w-24 flex items-center gap-2">
              Likes
            </div>
          </div>
        </div>
        {paginatedMembers.map((player) => (
          <MemberCard
            key={player.id}
            player={player}
          />
        ))}
      </div>

      <div className="flex items-center justify-between mt-8 mb-8">
        <button
          disabled={page === 1}
          onClick={() => setPage(page - 1)}
          className="
            px-4 py-2
            bg-zinc-800
            text-white
            rounded-md
            disabled:opacity-50
            disabled:cursor-not-allowed
            hover:bg-zinc-700
            transition-colors
            cursor-pointer
          "
        >
          Anterior
        </button>

        <span className="text-zinc-400 text-sm">
          Página {page} de {totalPages}
        </span>

        <button
          disabled={page === totalPages}
          onClick={() => setPage(page + 1)}
          className="
            px-4 py-2
            bg-zinc-800
            text-white
            rounded-md
            disabled:opacity-50
            disabled:cursor-not-allowed
            hover:bg-zinc-700
            transition-colors
            cursor-pointer

          "
        >
          Próxima
        </button>
      </div>
    </section>
  );
}

function SidebarPopularMembers() {
  return (
    <aside className="h-fit">
      <div className="border-b border-zinc-700 pb-3 mb-5">
        <h3 className="text-white tracking-wider text-m">
          Membros populares da semana
        </h3>
      </div>

      <div className="space-y-4">
        {popularMembers.map((member) => (
          <div
            key={member.id}
            className="
              flex items-center gap-3
              pb-4
              border-b border-zinc-800
            "
          >
            <img
              src={member.profilePicture}
              alt={member.name}
              className="w-12 h-12 rounded-full object-cover"
            />

            <div>
              <h4 className="text-white font-medium">
                {member.name}
              </h4>

              <p className="text-zinc-400 text-sm">
                {formatNumber(member.gamesPlayed)} jogos •{" "}
                {formatNumber(member.reviews)} reviews
              </p>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
