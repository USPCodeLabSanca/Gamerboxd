import React from "react";
import complete from "../assets/icons/complete.svg"
import jogou from "../assets/icons/jogou.svg"
import liked from "../assets/icons/liked.svg"
import nota from "../assets/icons/nota.svg"
import { Link } from "react-router-dom";


const Card = ({ game, status }) => {

    const iconCss = "w-[5%]";

    return (
        <Link to={`/games/${game.id}`} className="flex flex-col hover:cursor-pointer">
            <div
                className="group relative h-full w-auto aspect-4/5 bg-neutral-200 overflow-hidden rounded-2xl"
                >
                <img src={game.url} alt={game.title} className="h-full w-full object-cover transition-transform duration-300 hover:scale-105" />
                {/* Icones de status do jogo */}
            </div>
            {status && 
                <div className="z-50 text-white flex flex-row items-center gap-2 opacity-50 hover:opacity-100 transition-opacity duration-300 mt-2">
                    {game.jogou && <img src={jogou} alt="Jogou" className="w-[4%]" />}
                    {game.liked && <img src={liked} alt="Liked" className={iconCss} />}
                    {/* Verifica se a nota é um número inteiro, se for mostra o número em controles, se não for mostra o inteiro mais próximo e o valor */}
                    {game.nota % 1 === 0 ? 
                        <div className="flex flex-row">
                            {[...Array(game.nota)].map((_, index) => (
                                <img key={index} src={nota} alt="Nota" className="w-[7%]"/>
                            ))}
                        </div>
                            :
                        <div>
                            <div className="flex flex-row">
                                {[...Array(Math.floor(game.nota))].map((_, index) => (
                                    <img key={index} src={nota} alt="Nota" className="w-[7%]" />
                                ))}
                                <span className="text-roxo ml-1 text-sm">½</span>
                            </div>
                            
                        </div>    
                    }
                    {game.complete && <img src={complete} alt="Complete" className={iconCss} />}
                </div>
            }
        </Link>
    );
};

export default Card;
