import { useRef, useState } from "react";
import { useCreateReview, useEditReview } from "../hooks/useReviews";
import { getErrorMessage } from "../api/errors";
import Rating from "./Rating";
import completeIcon from "../assets/icons/complete.svg";
import likeIcon from "../assets/icons/liked.svg";

export default function ReviewModal({ game, review, isOpen, onClose, onSaved, completed }) {
    if (!isOpen) return null;
    return <ReviewForm key={review?.review_id ?? game.id} game={game} review={review} onClose={onClose} onSaved={onSaved} completed={completed} />;
}

function ReviewForm({ game, review, onClose, onSaved, completed }) {
    const formRef = useRef(null);
    const [rating, setRating] = useState(review?.rating_num ?? 0);
    const [texto, setTexto] = useState(review?.rating_text ?? "");
    const [curtiu, setCurtiu] = useState(review?.liked ?? false);
    const [completou, setCompletou] = useState(completed ?? review?.completed ?? false);
    const [privacy, setPrivacy] = useState(review?.privacy ?? 0);
    const [hours, setHours] = useState(review?.time_played ?? "");
    const create = useCreateReview();
    const edit = useEditReview();
    const mutation = review ? edit : create;

    async function handleSubmit(event) {
        event.preventDefault();
        const values = {
            rating_num: Number(rating), rating_text: texto || null,
            liked: curtiu, completed: completou, privacy: Number(privacy),
            time_played: hours === "" ? null : Number(hours),
        };
        try {
            const saved = review
                ? await edit.mutateAsync({ reviewId: review.review_id, review: values })
                : await create.mutateAsync({ ...values, game_id: game.id });
            onSaved?.(saved.review_id);
            onClose();
        } catch { return; }
    }

    function handleTab(event) {
        if (event.key !== "Tab" || mutation.isPending) return;
        const controls = [...formRef.current.querySelectorAll('button, input, select, textarea')].filter((control) => !control.disabled);
        const first = controls[0];
        const last = controls[controls.length - 1];
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }

    const inputClass = "w-full min-w-0 rounded-lg border border-white/10 bg-neutral-700/50 px-3 py-2 text-white outline-none focus:border-roxo focus-visible:ring-1 focus-visible:ring-roxo";
    const toggleClass = "relative flex cursor-pointer flex-col items-center gap-2 rounded-lg px-3 py-2 transition-colors focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-roxo";
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-3 backdrop-blur-sm sm:p-6" onKeyDown={(event) => { if (event.key === "Escape" && !mutation.isPending) onClose(); }}>
            <form ref={formRef} onSubmit={handleSubmit} onKeyDown={handleTab} role="dialog" aria-modal="true" aria-label={review ? "Editar review" : "Criar review"} className="relative max-h-[calc(100dvh-1.5rem)] w-full max-w-4xl overflow-y-auto overscroll-contain rounded-2xl border border-white/10 bg-neutral-800 p-5 text-white shadow-2xl sm:max-h-[calc(100dvh-3rem)] sm:p-8">
                <fieldset disabled={mutation.isPending} className="flex min-w-0 flex-col gap-6">
                    <button type="button" onClick={onClose} aria-label="Fechar" className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full text-2xl text-white/50 hover:bg-white/5 hover:text-white focus-visible:outline-2 focus-visible:outline-roxo">×</button>
                    <div className="grid min-w-0 gap-6 sm:grid-cols-[9rem_minmax(0,1fr)]">
                        <div className="flex min-w-0 items-start gap-4 pr-7 sm:block sm:pr-0">
                            <img src={game.url} alt={game.title} className="aspect-3/4 w-20 shrink-0 rounded-xl object-cover shadow-lg sm:w-full" />
                            <div className="min-w-0 sm:mt-4">
                                <h2 className="break-words text-xl font-bold leading-tight">{game.title}</h2>
                                {game.year && <p className="mt-2 text-sm text-white/40">{game.year}</p>}
                            </div>
                        </div>
                        <div className="flex min-w-0 flex-col gap-2 sm:pt-3">
                            <label className="flex min-w-0 flex-1 flex-col gap-2 text-sm text-white/60">Review<textarea aria-label="Review" autoFocus value={texto} onChange={(event) => setTexto(event.target.value)} maxLength={300} rows={7} placeholder="Descreva sua aventura..." className={`${inputClass} min-h-44 flex-1 resize-y leading-relaxed sm:min-h-64`} /></label>
                            <span className="self-end text-xs text-white/40">{texto.length}/300</span>
                        </div>
                    </div>
                    <div className="grid min-w-0 grid-cols-2 items-start gap-5 border-t border-white/10 pt-5 lg:grid-cols-[auto_auto_minmax(8rem,1fr)_minmax(0,2fr)]">
                        <div className="flex flex-col items-center gap-2">
                            <span className="text-xs text-white/50">Progresso</span>
                            <label className={`${toggleClass} ${completou ? "bg-roxo/10" : "hover:bg-white/5"}`}>
                                <input type="checkbox" aria-label="Completei o jogo" checked={completou} onChange={(event) => setCompletou(event.target.checked)} className="sr-only" />
                                <img src={completeIcon} alt="" aria-hidden="true" className={`h-8 w-8 ${completou ? "opacity-100" : "opacity-30"}`} />
                                <span aria-hidden="true" className="text-xs">Completado</span>
                            </label>
                        </div>
                        <div className="flex flex-col items-center gap-2">
                            <span className="text-xs text-white/50">Curtiu</span>
                            <label className={`${toggleClass} ${curtiu ? "bg-roxo/10" : "hover:bg-white/5"}`}>
                                <input type="checkbox" aria-label="Curti o jogo" checked={curtiu} onChange={(event) => setCurtiu(event.target.checked)} className="sr-only" />
                                <img src={likeIcon} alt="" aria-hidden="true" className={`h-8 w-8 ${curtiu ? "opacity-100" : "opacity-30"}`} />
                                <span aria-hidden="true" className="text-xs">Gostei</span>
                            </label>
                        </div>
                        <div className="col-span-2 flex min-w-0 flex-col gap-2 lg:col-span-1">
                            <label className="flex flex-col gap-2 text-xs text-white/50">Tempo jogado (horas)<input type="number" min="0" step="1" value={hours} onChange={(event) => setHours(event.target.value)} className={inputClass} /></label>
                        </div>
                        <div className="col-span-2 min-w-0 lg:col-span-1"><Rating value={rating} onChange={setRating} disabled={mutation.isPending} /></div>
                    </div>
                    {mutation.isError && <p role="alert">{getErrorMessage(mutation.error)}</p>}
                    <div className="flex flex-col gap-4 border-t border-white/10 pt-5 sm:flex-row sm:items-end sm:justify-between">
                        <label className="flex min-w-0 flex-col gap-2 text-xs text-white/50 sm:w-48">Privacidade<select value={privacy} onChange={(event) => setPrivacy(event.target.value)} className={inputClass}><option value={0}>Pública</option><option value={20}>Pessoas que sigo</option><option value={40}>Só eu</option></select></label>
                        <button type="submit" className="rounded-full border border-roxo bg-roxo/15 px-8 py-2.5 font-semibold transition-colors hover:bg-roxo focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-roxo disabled:opacity-50">{mutation.isPending ? "Salvando..." : "Salvar review"}</button>
                    </div>
                </fieldset>
            </form>
        </div>
    );
}
