import React from 'react';
import { Heart, Gamepad2 } from "lucide-react";


export default function ReviewItem() {
    const totalControls = 5;
    return (
        <div>
            <div className= "flex gap-3">
                <div className="w-24 h-32 bg-gray-700 rounded-lg flex-shrink-0"></div>
                <div className="flex flex-col gap-3">
                    <div className="text-xl font-bold">GTA IV</div>
                    <div>
                        <div></div>
                        <div>"Melhor jogo ja feito na história dos <br></br> games. Lionel Messi dos jogos"</div>
                    </div>
                    <div className="flex gap-3">
                        <Heart className="text-red-500" />
                        <div>42M</div>
                        <div className='flex gap-1.5'>
                            {Array.from({ length:totalControls}).map((_, index) =>(
                                <Gamepad2 className="text-[#836DFF]" />
                                ))}
                        </div>
                        
                    </div>
                </div>
            </div>
        </div>

    )
}