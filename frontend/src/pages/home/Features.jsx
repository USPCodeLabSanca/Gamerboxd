import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Card from "../../components/gameCard";
import jogouSvg from "../../assets/icons/jogou.svg";
import notaSvg from "../../assets/icons/nota.svg";
import likedSvg from "../../assets/icons/liked.svg";
import completeSvg from "../../assets/icons/complete.svg";
import reviewSvg from "../../assets/icons/review.svg";
import listaSvg from "../../assets/icons/lista.svg";
import diarioSvg from "../../assets/icons/diario.svg";
import gtaImg from "../../assets/imgs/gta.png";
import gowImg from "../../assets/imgs/ragnarok.png";

export default function Features() {
    return (
        <div className="relative bg-cinza font-sans flex flex-col items-center py-24 overflow-hidden">

            {/* Glow de fundo sutil atrás do conteúdo */}
            <div
                className="pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-150 h-150 rounded-full"
                style={{
                    background: "radial-gradient(circle, rgba(127,119,221,0.07) 0%, transparent 70%)",
                }}
            />

            <motion.div
                className="flex flex-col items-center justify-center mb-16 z-10"
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                
            >
                <span className="text-roxo font-bold tracking-widest uppercase text-sm mb-3">
                    Funcionalidades
                </span>
                <h1 className="text-3xl text-white md:text-5xl font-bold mb-4 text-center">
                    O que você pode fazer?
                </h1>
                <p className="text-gray-400 text-lg text-center max-w-md">
                    Escolha a sua forma preferida de compartilhar sua experiência
                </p>
            </motion.div>

            <motion.div
                className="z-10 w-full flex justify-center"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
            >
                <SideTabs />
            </motion.div>
        </div>
    );
}

function SideTabs() {
    const [activeTab, setActiveTab] = useState("tab1");

    const tabs = [
        { id: "tab1", label: "Jogados",     icon: jogouSvg,   emoji: "🎮" },
        { id: "tab2", label: "Notas",       icon: notaSvg,    emoji: "⭐" },
        { id: "tab3", label: "Avaliações",  icon: reviewSvg,  emoji: "📝" },
        { id: "tab4", label: "Completados", icon: completeSvg,emoji: "🏆" },
        { id: "tab5", label: "Favoritos",   icon: likedSvg,   emoji: "❤️" },
        { id: "tab6", label: "Diário",      icon: diarioSvg,  emoji: "📖" },
        { id: "tab7", label: "Listas",      icon: listaSvg,   emoji: "📋" },
    ];

    const tabContent = {
        tab1: (
            <TabPanel
                icon={jogouSvg}
                title="Jogados"
                description="Mostre para a comunidade quais jogos você já jogou e construa seu histórico."
                badge="Biblioteca"
            >
                {/* Preview: grid de capas de jogos */}
                <div className="mt-4 flex flex-row gap-2 items-end justify-center">
                    {[gowImg, gtaImg, gowImg, gtaImg].map((img, i) => (
                        <div
                            key={i}
                            className="rounded-lg overflow-hidden border border-white/10"
                            
                        >
                            <img src={img} alt="" className="w-full h-full object-cover" />
                        </div>
                    ))}
                    <span className="text-xs text-gray-500 pb-1 ml-1">+143</span>
                </div>
            </TabPanel>
        ),

        tab2: (
            <TabPanel
                icon={notaSvg}
                title="Notas"
                description="Dê uma nota para seus jogos e veja como sua coleção se compara."
                badge="Avaliação"
            >
                {/* Preview: cards com score */}
                <div className="mt-4 flex flex-row gap-3 items-center justify-center">
                    {cards.map((card) => (
                        <div key={card.id} className="flex flex-col items-center gap-1">
                            <Card game={card} status={true} />
                        </div>
                    ))}
                </div>
            </TabPanel>
        ),

        tab3: (
            <TabPanel
                icon={reviewSvg}
                title="Avaliações"
                description="Descreva como foi sua experiência com os jogos que você jogou."
                badge="Reviews"
            >
                {/* Preview: review card mockup */}
                <div className="mt-4 w-full rounded-xl border border-white/10 bg-white/5 p-3 text-left">
                    <div className="flex items-center gap-2 mb-2">
                        <div className="w-6 h-6 rounded-full bg-roxo/40 flex items-center justify-center text-xs text-white font-bold">V</div>
                        <span className="text-xs text-gray-300 font-medium">Você</span>
                        <div className="flex gap-0.5 ml-auto">
                            {[1,2,3,4,5].map(s => (
                                <span key={s} className="text-roxo text-xs">★</span>
                            ))}
                        </div>
                    </div>
                    <p className="text-xs text-gray-400 leading-relaxed line-clamp-3">
                        "Uma das experiências mais épicas que já tive. A narrativa te prende do início ao fim e os gráficos são simplesmente..."
                    </p>
                </div>
            </TabPanel>
        ),

        tab4: (
            <TabPanel
                icon={completeSvg}
                title="Completados"
                description="Mostre quais desafios você superou e os jogos que conseguiu completar 100%."
                badge="Conquistas"
            >
                {/* Preview: barra de progresso */}
                <div className="mt-4 w-full space-y-2">
                    {[
                        { name: "God of War", pct: 100 },
                        { name: "GTA V",      pct: 78  },
                        { name: "Hades",      pct: 45  },
                    ].map(({ name, pct }) => (
                        <div key={name}>
                            <div className="flex justify-between text-xs text-gray-400 mb-1">
                                <span>{name}</span>
                                <span className={pct === 100 ? "text-roxo font-bold" : ""}>{pct}%</span>
                            </div>
                            <div className="h-1.5 rounded-full bg-white/10 overflow-hidden">
                                <div
                                    className="h-full rounded-full bg-roxo"
                                    style={{ width: `${pct}%`, opacity: pct === 100 ? 1 : 0.5 }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </TabPanel>
        ),

        tab5: (
            <TabPanel
                icon={likedSvg}
                title="Favoritos"
                description="Destaque aqueles jogos inesquecíveis que moram no seu coração."
                badge="Top picks"
            >
                {/* Preview: grid de favoritos com coração */}
                <div className="mt-4 flex flex-row gap-2 items-center justify-center">
                    {[gowImg, gtaImg, gowImg].map((img, i) => (
                        <div key={i} className="relative rounded-lg overflow-hidden border border-white/10 aspect-[4:5]">
                            <img src={img} alt="" className="w-full h-full object-cover" />
                            <div className="absolute inset-0 bg-linear-to-t from-black/60 to-transparent" />
                            <span className="absolute bottom-1 right-1 text-xs">❤️</span>
                        </div>
                    ))}
                </div>
            </TabPanel>
        ),

        tab6: (
            <TabPanel
                icon={diarioSvg}
                title="Diário"
                description="Registre sua jornada diária, conquistas e os momentos mais épicos das suas gameplays."
                badge="Registro"
            >
                {/* Preview: entradas do diário */}
                <div className="mt-4 w-full space-y-2">
                    {[
                        { date: "Hoje",      text: "Finalmente derrotei o Kratos no modo difícil 🔥" },
                        { date: "Ontem",     text: "Comecei o NG+ de Elden Ring..." },
                    ].map(({ date, text }) => (
                        <div key={date} className="flex gap-2 items-start text-xs text-gray-400">
                            <span className="text-roxo font-medium min-w-9">{date}</span>
                            <span className="leading-relaxed">{text}</span>
                        </div>
                    ))}
                </div>
            </TabPanel>
        ),

        tab7: (
            <TabPanel
                icon={listaSvg}
                title="Listas"
                description="Crie listas personalizadas para organizar seu backlog, franquias ou recomendações."
                badge="Curadoria"
            >
                {/* Preview: listas */}
                <div className="mt-4 w-full space-y-2">
                    {[
                        { name: "🎯 Backlog 2025",           count: 12 },
                        { name: "🏆 Melhores de todos os tempos", count: 8  },
                        { name: "👫 Para jogar com amigos",  count: 5  },
                    ].map(({ name, count }) => (
                        <div key={name} className="flex justify-between items-center text-xs text-gray-400 border-b border-white/5 pb-1.5">
                            <span>{name}</span>
                            <span className="text-roxo font-medium">{count} jogos</span>
                        </div>
                    ))}
                </div>
            </TabPanel>
        ),
    };

    return (
        <div className="w-11/12 max-w-4xl border border-white/10 rounded-2xl bg-dark-card flex flex-row shadow-2xl shadow-black/60 overflow-hidden">

            {/* Coluna de tabs */}
            <div className="w-5/12 md:w-4/12 py-5 px-3 flex flex-col gap-1 border-r border-white/5">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`
                            group flex items-center gap-3
                            w-full px-3 py-2.5 rounded-xl text-left
                            transition-all duration-200 cursor-pointer
                            ${activeTab === tab.id
                                ? "bg-roxo/10 border-l-2 border-roxo text-roxo"
                                : "border-l-2 border-transparent text-gray-400 hover:text-white hover:bg-white/5"
                            }
                        `}
                    >
                        {/* Ícone inline na tab */}
                        <div className={`
                            w-7 h-7 rounded-lg flex items-center justify-center shrink-0
                            transition-colors duration-200 text-sm
                            ${activeTab === tab.id ? "bg-roxo/20" : "bg-white/5 group-hover:bg-white/10"}
                        `}>
                            <img src={tab.icon} alt="" className="w-4 h-4 opacity-80" />
                        </div>
                        <span className="font-semibold text-sm">{tab.label}</span>
                    </button>
                ))}
            </div>

            {/* Painel de conteúdo */}
            <div className="flex-1 relative overflow-hidden">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, x: 12 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -12 }}
                        transition={{ duration: 0.25, ease: "easeInOut" }}
                        className="w-full h-full p-6 flex flex-col"
                    >
                        {tabContent[activeTab]}
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>
    );
}

/* Componente reutilizável para cada painel */
function TabPanel({ icon, title, description, badge, children }) {
    return (
        <div className="flex flex-col h-full text-white">
            {/* Badge */}
            <span className="self-start text-xs font-semibold tracking-widest uppercase text-roxo border border-roxo/30 bg-roxo/10 rounded-full px-3 py-0.5 mb-4">
                {badge}
            </span>

            {/* Ícone + título */}
            <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-xl bg-roxo/15 border border-roxo/20 flex items-center justify-center shrink-0">
                    <img src={icon} alt="" className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-2xl">{title}</h4>
            </div>

            {/* Descrição */}
            <p className="text-gray-400 text-sm leading-relaxed">{description}</p>

            {/* Slot para preview contextual */}
            {children}
        </div>
    );
}

const cards = [
    {
        url: gtaImg,
        title: "GTA V",
        nota: 5,
        played: false,
        liked: false,
        complete: false,
        id: 1,
    },
    {
        url: gowImg,
        title: "God of War",
        nota: 4.5,
        played: true,
        liked: false,
        complete: false,
        id: 2,
    },
];