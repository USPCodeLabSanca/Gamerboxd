import React, { useState } from "react";
import Card from "./gameCard";
import liked from "../assets/icons/liked.svg";
import nota from "../assets/icons/nota.svg";
import complete from "../assets/icons/complete.svg";

// Ícones SVG inline para não depender de lib externa
const HeartIcon = ({ filled }) => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill={filled ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
    </svg>
);

const ShareIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" />
        <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" /><line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
    </svg>
);

const Review = ({ review, game, gameClassName = "" }) => {
    const [likedReview, setLikedReview] = useState(false);
    const [likeCount, setLikeCount] = useState(review.likes ?? Math.floor(Math.random() * 80) + 5);
    const [showShareToast, setShowShareToast] = useState(false);
    const [likeBurst, setLikeBurst] = useState(false);

    const handleLike = () => {
        setLikeBurst(true);
        setTimeout(() => setLikeBurst(false), 400);
        setLikedReview((prev) => {
            setLikeCount((c) => prev ? c - 1 : c + 1);
            return !prev;
        });
    };

    const handleShare = () => {
        navigator.clipboard?.writeText(window.location.href).catch(() => { });
        setShowShareToast(true);
        setTimeout(() => setShowShareToast(false), 2000);
    };

    return (
        <div className="w-full flex flex-row gap-4 items-start text-white group">
            {/* Capa do jogo */}
            <div className="shrink-0">
                <Card game={game} status={false} className={gameClassName} />
            </div>

            {/* Conteúdo */}
            <div className="flex-1 flex flex-col gap-3 justify-evenly min-w-0">
                {/* Título + ano */}
                <p className="text-2xl sm:text-3xl font-bold leading-tight">{game.title}</p>

                {/* Autor + texto */}
                <div className="flex flex-row gap-3 items-start">
                    <img
                        src={review.author.avatar}
                        alt={review.author.username}
                        className="w-8 h-8 rounded-full shrink-0 mt-0.5 ring-1 ring-white/20"
                    />
                    <div className="min-w-0">
                        <p className="text-xs text-white/40 mb-1">{review.author.username}</p>
                        <p className="text-sm text-white/80 leading-relaxed line-clamp-3">{review.content}</p>
                    </div>
                </div>

                {/* Nota + ícones do jogo */}
                <div className="flex flex-row gap-3 items-center">
                    {game.liked && <img src={liked} alt="Liked" className="w-4 h-4 opacity-80" />}
                    <div className="flex flex-row items-center">
                        {[...Array(Math.floor(game.nota))].map((_, i) => (
                            <img key={i} src={nota} alt="Nota" className="w-4 h-4" />
                        ))}
                        {game.nota % 1 !== 0 && (
                            <span className="text-roxo ml-1 text-xs">½</span>
                        )}
                    </div>
                    {review.complete && <img src={complete} alt="Complete" className="w-4 h-4 opacity-80" />}
                </div>

                {/* Ações de interação */}
                <div className="flex flex-row items-center gap-1 relative">
                    {/* Like */}
                    <button
                        onClick={handleLike}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200
                            ${likedReview
                                ? "bg-roxo/20 text-roxo"
                                : "text-white/40 hover:text-white/80 hover:bg-white/5"
                            } ${likeBurst ? "scale-125" : "scale-100"}`}
                    >
                        <HeartIcon filled={likedReview} />
                        <span>{likeCount}</span>
                    </button>

                    {/* Compartilhar */}
                    <div className="relative">
                        <button
                            onClick={handleShare}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-white/40 hover:text-white/80 hover:bg-white/5 transition-all duration-200"
                        >
                            <ShareIcon />
                            <span>Compartilhar</span>
                        </button>

                        {/* Toast de confirmação */}
                        <div className={`absolute bottom-full left-0 mb-2 px-3 py-1.5 bg-roxo text-white text-xs rounded-lg whitespace-nowrap pointer-events-none transition-all duration-200
                            ${showShareToast ? "opacity-100 -translate-y-1" : "opacity-0 translate-y-0"}`}>
                            Link copiado!
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Review;