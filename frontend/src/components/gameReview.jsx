import React, { useState } from "react";
import Card from "./gameCard";
import liked from "../assets/icons/liked.svg";
import nota from "../assets/icons/nota.svg";
import complete from "../assets/icons/complete.svg";
import { Link } from "react-router-dom";
import { useMe } from "../hooks/useAuth";
import { useDeleteReview, useLikeReview, useUnlikeReview, useReview } from "../hooks/useReviews";
import { getErrorMessage } from "../api/errors";
import ReviewModal from "./ReviewModal";

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

const Review = ({ review, game: previewGame, gameClassName = "", onDelete }) => {
    const { data: me } = useMe();
    const likeReview = useLikeReview(review.review_id);
    const unlikeReview = useUnlikeReview(review.review_id);
    const deleteReview = useDeleteReview(review.review_id);
    const [editing, setEditing] = useState(false);
    const detail = useReview(editing ? review.review_id : null);
    const [showShareToast, setShowShareToast] = useState(false);
    const [shareError, setShareError] = useState("");
    const likedReview = review.rel === 50 || review.rel === 90;
    const isOwner = !!review.review_id && me?.user_id === review.reviewer.user_id;
    const game = review.game ? {id: review.game.game_id, title: review.game.title, url: review.game.picture, year: review.game.year} : previewGame;
    const author = review.reviewer ?? review.author;
    const rating = review.rating_num ?? game.nota ?? 0;
    const pending = likeReview.isPending || unlikeReview.isPending || deleteReview.isPending;
    const error = likeReview.error || unlikeReview.error || deleteReview.error || detail.error;

    const handleLike = () => {
        if (!pending && review.review_id) {
            if (likedReview) unlikeReview.mutate();
            else likeReview.mutate();
        }
    };

    const handleShare = async () => {
        try {
            const url = review.review_id ? `${window.location.origin}/profile/${author.user_id}#review-${review.review_id}` : window.location.href;
            await navigator.clipboard.writeText(url);
            setShareError("");
            setShowShareToast(true);
            setTimeout(() => setShowShareToast(false), 2000);
        } catch {
            setShareError("Não foi possível copiar o link.");
        }
    };

    return (
        <div id={review.review_id ? `review-${review.review_id}` : undefined} className="w-full flex flex-row gap-4 items-start text-white group">
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
                        src={author.pfp || author.avatar || undefined}
                        alt={author.username}
                        className="w-8 h-8 rounded-full shrink-0 mt-0.5 ring-1 ring-white/20"
                    />
                    <div className="min-w-0">
                        {author.user_id ? <Link to={`/profile/${author.user_id}`} className="text-xs text-white/40 mb-1">{author.username}</Link> : <p className="text-xs text-white/40 mb-1">{author.username}</p>}
                        <p className="text-sm text-white/80 leading-relaxed line-clamp-3">{review.rating_text ?? review.content}</p>
                    </div>
                </div>

                {/* Nota + ícones do jogo */}
                <div className="flex flex-row gap-3 items-center">
                    {(review.liked ?? game.liked) && <img src={liked} alt="Liked" className="w-4 h-4 opacity-80" />}
                    <div className="flex flex-row items-center">
                        {[...Array(Math.floor(rating))].map((_, i) => (
                            <img key={i} src={nota} alt="Nota" className="w-4 h-4" />
                        ))}
                        {rating % 1 !== 0 && (
                            <span className="text-roxo ml-1 text-xs">½</span>
                        )}
                    </div>
                    {(review.completed ?? review.complete) && <img src={complete} alt="Complete" className="w-4 h-4 opacity-80" />}
                </div>

                {/* Ações de interação */}
                <div className="flex flex-row items-center gap-1 relative">
                    {/* Like */}
                    <button
                        onClick={handleLike}
                        disabled={!review.review_id || !me || pending}
                        aria-label={likedReview ? "Remover curtida" : "Curtir review"}
                        aria-pressed={likedReview}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200
                            ${likedReview
                                ? "bg-roxo/20 text-roxo"
                                : "text-white/40 hover:text-white/80 hover:bg-white/5"
                            }`}
                    >
                        <HeartIcon filled={likedReview} />
                        <span>{review.like_count ?? review.likes ?? 0}</span>
                    </button>

                    {isOwner && (
                        <>
                            <button disabled={pending} onClick={() => setEditing(true)} className="text-xs text-roxo px-3">Editar</button>
                            <button disabled={pending} onClick={() => {
                                if (window.confirm("Excluir esta review?")) deleteReview.mutate(undefined, {onSuccess: onDelete});
                            }} className="text-xs text-red-300 px-3">{deleteReview.isPending ? "Excluindo..." : "Excluir"}</button>
                        </>
                    )}
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
                {error && <p role="alert" className="text-red-300 text-sm">{getErrorMessage(error)}</p>}
                {shareError && <p role="alert" className="text-red-300 text-sm">{shareError}</p>}
                {editing && detail.isPending && <p className="text-white/50 text-sm">Carregando avaliação...</p>}
                {editing && detail.data && <ReviewModal game={game} review={detail.data} isOpen={true} onClose={() => setEditing(false)} />}
            </div>
        </div>
    );
};

export default Review;
