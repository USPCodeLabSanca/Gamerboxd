import { formatNumber } from "../utils/formatters";

import likedIcon from "../assets/icons/liked.svg";
import jogouIcon from "../assets/icons/jogou.svg";
import listaIcon from "../assets/icons/lista.svg";

export default function MemberCard({ player }) {
  return (
    <div
      className="
        flex
        flex-col
        md:flex-row
        md:items-center
        md:justify-between
        gap-4
        py-5
        border-b
        border-zinc-800
        hover:bg-white/5
        transition-colors
        px-2
        rounded-md
      "
    >
      <div className="flex items-center gap-4">
        <img
          src={player.profilePicture}
          alt={player.name}
          className="w-12 h-12 rounded-full object-cover"
        />

        <div>
          <h4 className="text-white font-medium">
            {player.name}
          </h4>

          <p className="text-zinc-400 text-sm">
            {player.reviews} reviews
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-4 md:gap-0 text-zinc-400 text-sm">
        <div className="w-auto md:w-24 flex items-center gap-2">
          <img src={jogouIcon} className="w-5"></img>
          <span>{formatNumber(player.gamesPlayed)}</span>
        </div>

        <div className="w-auto md:w-24 flex items-center gap-2">
          <img src={listaIcon} className="w-5"></img>
          <span>{formatNumber(player.reviews)}</span>
        </div>

        <div className="w-auto md:w-24 flex items-center gap-2">
          <img src={likedIcon} className="w-5"></img>
          <span>{formatNumber(player.likes)}</span>
        </div>
      </div>
    </div>
  );
}
