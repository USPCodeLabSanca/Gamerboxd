import React from "react";
import { Link } from "react-router-dom";
import Register from "../register/index.jsx";

import { motion } from "framer-motion";
import { Heart, Trophy, Star, MessageSquare } from "lucide-react";
import NumberFlow from '@number-flow/react';
import notaSvg from "../../assets/icons/nota.svg"

const reviews = [
    {
        id: 1,
        username: "lionel_messi99",
        initials: "LM",
        avatarColor: "bg-roxo/20 text-roxo",
        game: "GTA VI",
        score: 5,
        liked: true,
        complete: false,
        text: "Melhor jogo já feito na história. Rockstar superou todas as expectativas, impossível parar de jogar.",
        likes: 234,
        timeAgo: "há 2 dias",
    },
    {
        id: 2,
        username: "kratos_fan",
        initials: "KR",
        avatarColor: "bg-red-900/40 text-red-400",
        game: "God of War: Ragnarök",
        score: 5,
        liked: true,
        complete: true,
        text: "A história me fez chorar três vezes. Kratos e Atreus têm uma das relações mais bem escritas dos jogos.",
        likes: 187,
        timeAgo: "há 5 dias",
    },
    {
        id: 3,
        username: "zelda_nerd",
        initials: "ZN",
        avatarColor: "bg-yellow-900/40 text-yellow-400",
        game: "Hollow Knight: Silksong",
        score: 4,
        liked: false,
        complete: false,
        text: "Esperou demais, mas valeu cada segundo. O combate é refinado e a trilha sonora é obra de arte.",
        likes: 143,
        timeAgo: "há 1 semana",
    },
];

const stats = [
    { label: "Gamers cadastrados", value: 28, suffix: "k", icon: "👾" },
    { label: "Reviews escritas",   value: 140, suffix: "k", icon: "📝" },
    { label: "Jogos catalogados",  value: 12,  suffix: "k", icon: "🎮" },
    { label: "Listas criadas",     value: 34,  suffix: "k", icon: "📋" },
];

export default function Social() {
    const [statsVisible, setStatsVisible] = React.useState(false);

    return (
        <section className="w-full bg-cinza text-white py-20 px-6 flex flex-col items-center">

            {/* Header */}
            <motion.div
                className="flex flex-col items-center text-center mb-16"
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeIn" }}
            >
                <label className="text-roxo font-bold tracking-widest uppercase text-sm mb-2">
                    Comunidade
                </label>
                <h1 className="text-3xl md:text-5xl font-bold mb-4">
                    Descreva sua jornada
                </h1>
                <p className="text-gray-400 text-lg max-w-xl">
                    Compartilhe com outros membros da comunidade como foi sua experiência de gameplay
                </p>
            </motion.div>

            {/* Stats */}
            <motion.div
                className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-4xl mb-16"

                onViewportEnter={() => setStatsVisible(true)}
                onViewportLeave={() => setStatsVisible(false)}
            >
                {stats.map((stat) => (
                    <div
                        key={stat.label}
                        className="bg-dark-card rounded-2xl p-6 flex flex-col items-center border border-transparent hover:border-roxo/50 transition-colors duration-300"
                    >
                        <span className="text-2xl mb-2">{stat.icon}</span>
                        <span className="text-3xl font-bold text-white tabular-nums">
                            <NumberFlow
                                value={statsVisible ? stat.value : 0} 
                                suffix={stat.suffix}
                                trend={1}
                                spinTiming ={{duration: 2000, easing: 'ease-out'}}
                            />
                        </span>
                        <span className="text-gray-400 text-sm text-center mt-1">{stat.label}</span>
                    </div>
                ))}
            </motion.div>

            {/* Review cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-6xl">
                {reviews.map((review, index) => (
                    <motion.div
                        key={review.id}
                        initial={{ opacity: 0, y: 60 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.7, ease: "easeIn", delay: index * 0.15 }}
                        viewport={{ once: true }}
                    >
                        <ReviewCard review={review} />
                    </motion.div>
                ))}
            </div>

            {/* CTA final */}
            <motion.div
                className="mt-20 w-full max-w-4xl bg-dark-card rounded-3xl p-12 flex flex-col items-center text-center border border-transparent hover:border-roxo/30 transition-colors duration-300"
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeIn" }}
                viewport={{ once: true }}
            >
                <h2 className="text-3xl md:text-5xl font-bold mb-4">
                    Não perca mais tempo!
                </h2>
                <p className="text-gray-400 text-lg mb-8 max-w-md">
                    Crie agora sua conta e junte-se à maior rede social exclusiva para gamers do Brasil.
                </p>
                <Link to={"/register"} className="relative overflow-hidden bg-roxo px-10 py-4 rounded-2xl text-white font-bold text-lg after:content-[''] after:absolute after:top-0 after:left-0 after:h-full after:w-0 after:bg-white/10 after:transition-all after:duration-300 hover:after:w-full cursor-pointer transition-all duration-300 hover:scale-105">
                    <span className="relative z-10">Criar conta grátis</span>
                </Link>
                <p className="text-gray-600 text-sm mt-4">
                    Grátis para sempre.
                </p>
            </motion.div>

        </section>
    );
}

function ReviewCard({ review }) {
    return (
        <div className="bg-dark-card rounded-2xl p-6 flex flex-col border border-transparent hover:border-roxo/50 transition-colors duration-300 h-full">

            {/* Header do card */}
            <div className="flex items-center gap-3 mb-4">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm shrink-0 ${review.avatarColor}`}>
                    {review.initials}
                </div>
                <div>
                    <p className="font-bold text-white text-sm">{review.username}</p>
                    <p className="text-gray-500 text-xs">{review.game}</p>
                </div>
            </div>

            {/* Ícones de status */}
            <div className="flex items-center gap-3 mb-3">
                <GameScore score={review.score} />
                <div className="flex gap-2 ml-auto">
                    {review.liked && (
                        <Heart size={14} className="text-red-500 fill-red-500" />
                    )}
                    {review.complete && (
                        <Trophy size={14} className="text-yellow-400 fill-yellow-400" />
                    )}
                </div>
            </div>

            {/* Texto da review */}
            <p className="text-gray-400 text-sm leading-relaxed flex-1">
                {review.text}
            </p>

            {/* Footer */}
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/5">
                <div className="flex items-center gap-1 text-gray-500 text-xs">
                    <Heart size={12} className="text-red-500 fill-red-500" />
                    <span>{review.likes}</span>
                </div>
                <span className="text-gray-600 text-xs">{review.timeAgo}</span>
            </div>
        </div>
    );
}

function GameScore({ score }) {
    return (
        <div className="flex gap-0.5">
            {Array.from({ length: 5 }).map((_, i) => (
                <img key={i} className="w-[10%]" src={notaSvg}></img>
            ))}
        </div>
    );
}