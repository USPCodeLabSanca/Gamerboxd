import React, { useState, useEffect } from "react";
import { motion as Motion, AnimatePresence } from "framer-motion";

import likeIcon from "../assets/icons/liked.svg";
import completeIcon from "../assets/icons/complete.svg";
import notaIcon from "../assets/icons/nota.svg";
import { useCreateReview, useEditReview } from "../hooks/useReviews";
import { getErrorMessage } from "../api/errors";

const XIcon = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
    </svg>
);

export default function ReviewModal({ game, review, isOpen, onClose, onSuccess }) {
    const createReview = useCreateReview();
    const editReview = useEditReview(review?.review_id);
    const saveReview = review ? editReview : createReview;
    const [rating, setRating] = useState(review?.rating_num ?? 0);
    const [hoverRating, setHoverRating] = useState(0);
    const [curtiu, setCurtiu] = useState(review?.liked ?? false);
    const [completou, setCompletou] = useState(review?.completed ?? false);
    const [texto, setTexto] = useState(review?.rating_text ?? "");
    const [timePlayed, setTimePlayed] = useState(review?.time_played ?? "");
    const [privacy, setPrivacy] = useState(review?.privacy ?? 0);
    const close = () => { if (!saveReview.isPending) onClose(); };

    useEffect(() => {
        const handleKey = (e) => { if (e.key === "Escape" && !saveReview.isPending) onClose(); };
        if (isOpen) window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [isOpen, onClose, saveReview.isPending]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (saveReview.isPending) return;
        const data = {
            rating_num: rating,
            rating_text: texto.trim() || null,
            liked: curtiu,
            completed: completou,
            time_played: timePlayed === "" ? null : Number(timePlayed),
            privacy: privacy,
        };
        if (!review) data.game_id = game.id;
        saveReview.mutate(data, {
            onSuccess: (result) => {
                onSuccess?.(result);
                onClose();
            }
        });
    };

    const displayRating = hoverRating || rating;

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <Motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={close}
                        className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
                    />

                    <Motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ type: "spring", duration: 0.4 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
                    >
                        <form
                            onSubmit={handleSubmit}
                            className="bg-neutral-800/95 backdrop-blur-md rounded-2xl shadow-2xl w-full max-w-2xl pointer-events-auto border border-white/5"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="flex gap-6 p-6">
                                {/* Capa */}
                                <div className="shrink-0 w-32">
                                    <div className="aspect-4/5 rounded-xl overflow-hidden shadow-lg">
                                        <img src={game.url} alt={game.title} className="w-full h-full object-cover" />
                                    </div>
                                    <div className="mt-3">
                                        <p className="text-white/50 text-xs mb-1">Horas jogadas:</p>
                                        <input
                                            type="number"
                                            min="0"
                                            step="1"
                                            value={timePlayed}
                                            onChange={(e) => setTimePlayed(e.target.value)}
                                            className="w-full bg-roxo/20 text-roxo text-xs rounded-lg px-3 py-2 outline-none border border-roxo/30 focus:border-roxo transition-colors"
                                        />
                                    </div>
                                </div>

                                {/* Direita */}
                                <div className="flex-1 flex flex-col gap-4 min-w-0">
                                    <div className="flex items-start justify-between">
                                        <h2 className="text-white font-bold text-xl leading-tight">
                                            {game.title}
                                            <span className="text-white/40 font-normal text-sm ml-2">{game.year}</span>
                                        </h2>
                                        <button type="button" onClick={close} className="text-white/30 hover:text-white transition-colors ml-2 shrink-0">
                                            <XIcon />
                                        </button>
                                    </div>

                                    <textarea
                                        value={texto}
                                        onChange={(e) => setTexto(e.target.value)}
                                        placeholder="Descreva sua aventura..."
                                        rows={6}
                                        maxLength={280}
                                        className="w-full bg-neutral-700/50 text-white text-sm rounded-xl px-4 py-3 outline-none resize-none border border-white/5 focus:border-roxo/40 transition-colors placeholder:text-white/25 leading-relaxed"
                                    />

                                    <div className="flex items-center justify-between">
                                        {/* Toggles */}
                                        <div className="flex items-center gap-5">
                                            {/* 100% — ícone de complete */}
                                            <button
                                                type="button"
                                                onClick={() => setCompletou(!completou)}
                                                className="flex flex-col items-center gap-1 hover:cursor-pointer hover:scale-105 duration-300 transition-all"
                                            >
                                                <img
                                                    src={completeIcon}
                                                    alt="100%"
                                                    className="w-7 h-7 transition-all duration-200"
                                                    style={{ opacity: completou ? 1 : 0.25, filter: completou ? "brightness(1.4) sepia(1) hue-rotate(10deg) saturate(3)" : "none" }}
                                                />
                                                <span className={`text-[10px] transition-colors ${completou ? "text-amarelo" : "text-white/30"}`}>100%</span>
                                            </button>

                                            {/* Curtiu — ícone de like */}
                                            <button
                                                type="button"
                                                onClick={() => setCurtiu(!curtiu)}
                                                className="flex flex-col items-center gap-1 hover:cursor-pointer hover:scale-105 duration-300 transition-all"
                                            >
                                                <img
                                                    src={likeIcon}
                                                    alt="Curtiu"
                                                    className="w-7 h-7 transition-all duration-200"
                                                    style={{ opacity: curtiu ? 1 : 0.25}}
                                                />
                                                <span className={`text-[10px] transition-colors ${curtiu ? "text-roxo" : "text-white/30"}`}>Curtiu</span>
                                            </button>

                                        </div>

                                        {/* Rating com ícone de nota */}
                                        <div className="flex flex-col items-end gap-1">
                                            <label className="text-white/50 text-xs">
                                                Nota
                                                <input type="number" min="0" max="5" step="0.5" value={rating} onChange={(e) => setRating(Number(e.target.value))} className="ml-2 w-16 bg-neutral-700 rounded px-2 py-1" />
                                            </label>
                                            <span className="text-white/40 text-[10px]">
                                                Rating: {displayRating > 0 ? `${displayRating} de 5` : "—"}
                                            </span>
                                            <div className="flex gap-1">
                                                {[1, 2, 3, 4, 5].map((i) => (
                                                    <button
                                                        type="button"
                                                        key={i}
                                                        onMouseEnter={() => setHoverRating(i)}
                                                        onMouseLeave={() => setHoverRating(0)}
                                                        onClick={() => setRating(i === rating ? 0 : i)}
                                                        className={`transition-all duration-150 hover:cursor-pointer ${i <= displayRating ? "scale-110" : "scale-100"}`}
                                                    >
                                                        <img
                                                            src={notaIcon}
                                                            alt={`${i} estrelas`}
                                                            className="w-7 h-7"
                                                            style={{
                                                                opacity: i <= displayRating ? 1 : 0.2,
                                                                transition: "opacity 0.15s, filter 0.15s"
                                                            }}
                                                        />
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    <label className="text-white/50 text-xs">
                                        Visibilidade
                                        <select value={privacy} onChange={(e) => setPrivacy(Number(e.target.value))} className="ml-3 bg-neutral-700 text-white rounded-lg p-2">
                                            <option value={0}>Pública</option>
                                            <option value={20}>Pessoas que sigo</option>
                                            <option value={40}>Privada</option>
                                        </select>
                                    </label>
                                    {saveReview.isError && <p role="alert" className="text-red-300 text-sm">{getErrorMessage(saveReview.error)}</p>}
                                    <div className="flex justify-end">
                                        <button
                                            type="submit"
                                            disabled={saveReview.isPending}
                                            className="relative overflow-hidden border-2 border-white text-white rounded-2xl px-6 py-2 opacity-80 after:content-[''] after:absolute after:top-0 after:left-0 after:w-0 after:h-full after:transition-all after:duration-300 after:bg-roxo hover:after:w-full cursor-pointer transition-colors duration-300 hover:scale-105 after:-z-10"
                                        >
                                            <span className="relative z-10 font-semibold">{saveReview.isPending ? "Enviando..." : review ? "Salvar" : "Enviar"}</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </Motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
