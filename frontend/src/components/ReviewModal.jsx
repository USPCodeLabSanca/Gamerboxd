import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

import likeIcon from "../assets/icons/liked.svg";
import completeIcon from "../assets/icons/complete.svg";
import notaIcon from "../assets/icons/nota.svg";
import jogouIcon from "../assets/icons/jogou.svg";

const XIcon = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
    </svg>
);

export default function ReviewModal({ game, isOpen, onClose, onSubmit }) {
    const [rating, setRating] = useState(0);
    const [hoverRating, setHoverRating] = useState(0);
    const [jogou, setJogou] = useState(false);
    const [curtiu, setCurtiu] = useState(false);
    const [completou, setCompletou] = useState(false);
    const [texto, setTexto] = useState("");
    const [tags, setTags] = useState("");
    const [jogadoEm, setJogadoEm] = useState(
        new Date().toLocaleDateString("pt-BR").split("/").reverse().join("-")
    );

    useEffect(() => {
        const handleKey = (e) => { if (e.key === "Escape") onClose(); };
        if (isOpen) window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [isOpen, onClose]);

    const handleSubmit = () => {
        onSubmit?.({ rating, jogou, curtiu, completou, texto, tags, jogadoEm });
        onClose();
    };

    const displayRating = hoverRating || rating;

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
                    />

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ type: "spring", duration: 0.4 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
                    >
                        <div
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
                                        <p className="text-white/50 text-xs mb-1">Jogado em:</p>
                                        <input
                                            type="date"
                                            value={jogadoEm}
                                            onChange={(e) => setJogadoEm(e.target.value)}
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
                                        <button onClick={onClose} className="text-white/30 hover:text-white transition-colors ml-2 shrink-0">
                                            <XIcon />
                                        </button>
                                    </div>

                                    <textarea
                                        value={texto}
                                        onChange={(e) => setTexto(e.target.value)}
                                        placeholder="Descreva sua aventura..."
                                        rows={6}
                                        className="w-full bg-neutral-700/50 text-white text-sm rounded-xl px-4 py-3 outline-none resize-none border border-white/5 focus:border-roxo/40 transition-colors placeholder:text-white/25 leading-relaxed"
                                    />

                                    <div className="flex items-center justify-between">
                                        {/* Toggles */}
                                        <div className="flex items-center gap-5">
                                            {/* 100% — ícone de complete */}
                                            <button
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

                                            {/* Jogou — ícone de nota (estrela) */}
                                            <button
                                                onClick={() => setJogou(!jogou)}
                                                className="flex flex-col items-center gap-1 hover:cursor-pointer hover:scale-105 duration-300 transition-all"
                                            >
                                                <img
                                                    src={jogouIcon}
                                                    alt="Jogou"
                                                    className="w-7 h-7 transition-all duration-200"
                                                    style={{ opacity: jogou ? 1 : 0.25, filter: jogou ? "brightness(1.2)" : "none" }}
                                                />
                                                <span className={`text-[10px] transition-colors ${jogou ? "text-turquesa" : "text-white/30"}`}>Jogou</span>
                                            </button>
                                        </div>

                                        {/* Rating com ícone de nota */}
                                        <div className="flex flex-col items-end gap-1">
                                            <span className="text-white/40 text-[10px]">
                                                Rating: {displayRating > 0 ? `${displayRating} de 5` : "—"}
                                            </span>
                                            <div className="flex gap-1">
                                                {[1, 2, 3, 4, 5].map((i) => (
                                                    <button
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

                                    <div className="flex justify-end">
                                        <button
                                            onClick={handleSubmit}
                                            className="relative overflow-hidden border-2 border-white text-white rounded-2xl px-6 py-2 opacity-80 after:content-[''] after:absolute after:top-0 after:left-0 after:w-0 after:h-full after:transition-all after:duration-300 after:bg-roxo hover:after:w-full cursor-pointer transition-colors duration-300 hover:scale-105 after:-z-10"
                                        >
                                            <span className="relative z-10 font-semibold">Enviar</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}