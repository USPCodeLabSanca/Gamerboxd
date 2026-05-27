import React from "react";
import Card from "./gameCard";
import liked from "../assets/icons/liked.svg"
import nota from "../assets/icons/nota.svg"
import complete from "../assets/icons/complete.svg"

const Review = ({review, game}) => {

    return (
        <div className="w-full flex flex-row gap-4 items-center text-white">
            <div className="w-[10%] ">
                <Card game={game} status={false}/>
            </div>
            <div className="h-full flex flex-col gap-4 justify-evenly">
                <p className="text-4xl">{game.title}</p>
                <div className="flex flex-row gap-4 items-center">
                    <img src={review.author.avatar} alt={review.author.username} className="w-15 aspect-square rounded-full"/>
                    <p className="wrap font-regular">{review.content}</p>
                </div>
                <div className="flex flex-row gap-4 ml-4">
                    {game.liked && <img src={liked} alt="Liked" className="w-5" />}
                    {game.nota % 1 === 0 ? 
                        <div className="flex flex-row">
                            {[...Array(game.nota)].map((_, index) => (
                                <img key={index} src={nota} alt="Nota" className="w-5"/>
                            ))}
                        </div>
                            :
                        <div>
                            <div className="flex flex-row">
                                {[...Array(Math.floor(game.nota))].map((_, index) => (
                                    <img key={index} src={nota} alt="Nota" className="w-5" />
                                ))}
                                <span className="text-roxo ml-1 text-sm">½</span>
                            </div>
                            
                        </div>    
                    }
                    {review.complete && <img src={complete} alt="Complete" className="w-5" />}
                </div>
            </div>
        </div>
    )
}

export default Review;