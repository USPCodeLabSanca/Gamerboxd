import React from "react";
import complete from "../assets/icons/complete.svg";
import jogou from "../assets/icons/jogou.svg";
import liked from "../assets/icons/liked.svg";
import nota from "../assets/icons/nota.svg";
import { Link } from "react-router-dom";

const Card = ({ game, status, className="" }) => {
    const iconCss = "w-4 h-4 sm:w-5 sm:h-5";

    return (
        <Link to={`/games/${game.id}`} className={`flex flex-col hover:cursor-pointer transition-transform duration-300 hover:scale-105 ${className}`}>
            <div className="group relative w-full aspect-4/5 bg-neutral-200 overflow-hidden rounded-2xl ">
                <img
                    src={game.url}
                    alt={game.title}
                    className="h-full w-full object-cover"
                />
            </div>

            {status && (
                <div className="z-50 text-white flex flex-row items-center gap-1.5 sm:gap-2 opacity-50 hover:opacity-100 transition-opacity duration-300 mt-2">
                    {game.jogou && (
                        <img src={jogou} alt="Jogou" className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    )}
                    {game.liked && (
                        <img src={liked} alt="Liked" className={iconCss} />
                    )}
                    {game.nota !== undefined && (
                        <div className="flex flex-row items-center">
                            {[...Array(Math.floor(game.nota))].map((_, index) => (
                                <img
                                    key={index}
                                    src={nota}
                                    alt="Nota"
                                    className="w-3.5 h-3.5 sm:w-4 sm:h-4"
                                />
                            ))}
                            {game.nota % 1 !== 0 && (
                                <span className="text-roxo ml-0.5 text-xs sm:text-sm leading-none">½</span>
                            )}
                        </div>
                    )}
                    {game.complete && (
                        <img src={complete} alt="Complete" className={iconCss} />
                    )}
                </div>
            )}
        </Link>
    );
};

export default Card;