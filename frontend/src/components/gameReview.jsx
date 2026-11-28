import { useEffect, useId, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Heart, Pencil, Share2, Trash2 } from "lucide-react";
import Card from "./gameCard";
import ReviewModal from "./ReviewModal";
import { useMe } from "../hooks/useAuth";
import { useReview, useReviewLike, useDeleteReview, useSetReviewLike } from "../hooks/useReviews";
import { toCardGame } from "../services/gameService";
import { getErrorMessage } from "../api/errors";
import Rating from "./Rating";

export default function Review({ review: summary, gameClassName = "w-28", onDeleted }) {
    const { data: me, isPending: authPending } = useMe();
    const navigate = useNavigate();
    const likeCountId = useId();
    const likeInFlight = useRef(false);
    const shareTimer = useRef(null);
    const { data: review, isLoading, error } = useReview(summary.review_id);
    const like = useReviewLike(summary.review_id);
    const remove = useDeleteReview();
    const setLike = useSetReviewLike();
    const [editing, setEditing] = useState(false);
    const [confirmDelete, setConfirmDelete] = useState(false);
    const [shareMessage, setShareMessage] = useState("");
    useEffect(() => () => clearTimeout(shareTimer.current), []);
    if (isLoading) return <p className="text-white">Carregando review...</p>;
    if (error) return <p role="alert" className="text-white">{getErrorMessage(error)}</p>;
    if (!review) return null;
    const game = toCardGame(review.game);
    const owner = me?.user_id === review.reviewer.user_id;
    const pending = remove.isPending || setLike.isPending;
    const actionClass = "inline-flex min-h-11 min-w-11 items-center justify-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-roxo disabled:cursor-not-allowed disabled:opacity-50";
    const neutralAction = `${actionClass} border-white/15 bg-white/5 text-white/75 hover:border-roxo/50 hover:bg-roxo/10 hover:text-white`;
    const destructiveAction = `${actionClass} border-red-400/20 bg-red-400/5 text-red-300/80 hover:border-red-400/40 hover:bg-red-400/10 hover:text-red-200`;

    async function handleLike() {
        if (authPending || pending || likeInFlight.current || (me && (like.isPending || like.isError))) return;
        if (!me) {
            navigate('/login');
            return;
        }
        likeInFlight.current = true;
        try {
            await setLike.mutateAsync({ reviewId: review.review_id, liked: !like.data });
        } catch { return; }
        finally { likeInFlight.current = false; }
    }

    async function handleDelete() {
        try {
            await remove.mutateAsync(review.review_id);
            onDeleted?.();
        } catch { return; }
    }
    async function handleShare() {
        let message;
        try {
            await navigator.clipboard.writeText(`${window.location.origin}/games/${game.id}?review=${review.review_id}`);
            message = "Link copiado!";
        } catch { message = "Não foi possível copiar o link."; }
        clearTimeout(shareTimer.current);
        setShareMessage(message);
        shareTimer.current = setTimeout(() => setShareMessage(""), 3000);
    }
    return (
        <article className="flex w-full min-w-0 flex-col items-start gap-4 text-white sm:flex-row">
            <Card game={game} status={false} className={`shrink-0 ${gameClassName}`} />
            <div className="flex w-full min-w-0 flex-1 flex-col gap-3 sm:w-auto">
                <div className="flex min-w-0 flex-wrap items-center gap-x-3 gap-y-1">
                    <Link to={`/games/${game.id}`} className="min-w-0 text-2xl font-bold [overflow-wrap:anywhere] focus-visible:rounded-sm focus-visible:outline-2 focus-visible:outline-roxo">{game.title}</Link>
                    <Link to={`/profile/${review.reviewer.user_id}`} className="inline-flex min-w-0 items-center gap-1.5 rounded-sm text-xs text-white/50 transition-colors hover:text-roxo focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-roxo">
                        {review.reviewer.pfp && <img src={review.reviewer.pfp} alt="" className="h-5 w-5 shrink-0 rounded-full" />}
                        <span className="min-w-0 [overflow-wrap:anywhere]">por {review.reviewer.username}</span>
                    </Link>
                </div>
                <p className="whitespace-pre-wrap text-sm [overflow-wrap:anywhere]">{review.rating_text}</p>
                <Rating value={review.rating_num} />
                {review.time_played !== null && <p>{review.time_played} horas jogadas</p>}
                <div className="flex flex-wrap items-center gap-2">
                    <button type="button" aria-label={like.data ? "Descurtir review" : "Curtir review"} aria-describedby={likeCountId} aria-pressed={like.data === true} aria-busy={setLike.isPending} disabled={authPending || pending || (!!me && (like.isPending || like.isError))} onClick={handleLike} className={`${actionClass} ${like.data ? "border-roxo/40 bg-roxo/15 text-roxo hover:bg-roxo/25" : "border-white/15 bg-white/5 text-white/60 hover:border-roxo/50 hover:bg-roxo/10 hover:text-roxo"}`}>
                        <Heart aria-hidden="true" className="h-5 w-5" fill={like.data ? "currentColor" : "none"} />
                        <span id={likeCountId} aria-live="polite">{review.like_count}<span className="sr-only">{review.like_count === 1 ? " curtida" : " curtidas"}</span></span>
                    </button>
                    <div className="relative">
                        <button type="button" onClick={handleShare} className={neutralAction}><Share2 aria-hidden="true" className="h-4 w-4" />Compartilhar</button>
                        {shareMessage && <span role="status" aria-atomic="true" className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 w-max max-w-56 -translate-x-1/2 rounded-lg border border-roxo/30 bg-neutral-800 px-3 py-2 text-center text-xs text-white shadow-lg">{shareMessage}</span>}
                    </div>
                    {owner && <><button type="button" disabled={pending} onClick={() => setEditing(true)} className={neutralAction}><Pencil aria-hidden="true" className="h-4 w-4" />Editar</button><button type="button" disabled={pending} onClick={() => setConfirmDelete(true)} className={destructiveAction}><Trash2 aria-hidden="true" className="h-4 w-4" />Excluir</button></>}
                </div>
                {!me && <Link to="/login">Entre para curtir uma review.</Link>}
                {confirmDelete && <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-white/75"><p>Excluir esta review? O jogo também será removido dos favoritos e completados marcados nesta review.</p><div className="mt-3 flex flex-wrap gap-2"><button type="button" disabled={pending} onClick={handleDelete} className={destructiveAction}>Confirmar exclusão</button><button type="button" disabled={pending} onClick={() => setConfirmDelete(false)} className={neutralAction}>Cancelar</button></div></div>}
                {(remove.error || setLike.error || like.error) && <p role="alert">{getErrorMessage(remove.error || setLike.error || like.error)}</p>}
                <ReviewModal game={game} review={review} isOpen={editing} onClose={() => setEditing(false)} />
            </div>
        </article>
    );
}
