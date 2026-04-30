import React, { act, useState } from "react";
import { motion } from "framer-motion";
import Card from "../../components/gameCard";
import jogouSvg from "../../assets/icons/jogou.svg";
import notaSvg from "../../assets/icons/nota.svg";
import likedSvg from "../../assets/icons/liked.svg";
import completeSvg from "../../assets/icons/complete.svg";
import reviewSvg from "../../assets/icons/review.svg"
import listaSvg from "../../assets/icons/lista.svg"
import diarioSvg from "../../assets/icons/diario.svg"
import reviewImg from "../../assets/imgs/Review.png";
import gtaImg from "../../assets/imgs/gta.png";
import gowImg from "../../assets/imgs/ragnarok.png";

export default function Features() {
    return (
        <div className="bg-cinza h-screen font-sans flex flex-col items-center">
            <motion.div className="flex flex-col items-center justify-center"
                initial={{opacity: 0, y: 50}}
                whileInView={{opacity: 100, y: 0}}
                transition={{duration: 0.8, ease: "easeIn"}}
            >
                <label className="text-roxo font-bold tracking-widest uppercase text-sm mb-2">Funcionalidades</label>
                <h1 className="text-3xl text-white md:text-5xl font-bold mb-4">O que você pode fazer?</h1>
                <p className="text-gray-400 mb-16 text-lg">Escolha a sua forma preferida de compartilhar sua experiência</p>
            </motion.div>
            <SideTabs />
        </div>
    )
}

function SideTabs() {

    const [activeTab, setActiveTab] = useState("tab1")

    const tabs = [
        {id: "tab1", label: "Jogados"},
        {id: "tab2", label: "Notas"},
        {id: "tab3", label: "Avaliações"},
        {id: "tab4", label: "Completados"},
        {id: "tab5", label: "Favoritos"},
        {id: "tab6", label: "Diario"},
        {id: "tab7", label: "Listas"},
    ]

    const tabContent = {
        tab1: (
            <div 
            className="w-full h-full flex flex-col items-center justify-evenly text-white font-sans">

                <div className=" w-full flex flex-col items-center">
                    <img src={jogouSvg} alt="botões do controle" />
                    <h4 className="font-bold text-4xl mt-4">Jogados</h4>
                    <p className="w-[70%] text-center">Mostre para comunidade quais jogos você já jogou</p>
                </div>
            </div>
        ),
        tab2: (
            <div
            className="w-full h-full flex flex-col items-center justify-evenly text-white font-sans">
                <div className=" w-full flex flex-col items-center">
                    <img className="w-[15%]" 
                    src={notaSvg} alt="ícone de controle" />
                    <h4 className="font-bold text-4xl mt-2">Notas</h4>
                    <p className="w-[70%] text-center">De uma nota para seus jogos</p>
                    <div className="w-10/12 h-7/12 mt-2 flex flex-row gap-2 items-center justify-center text-2xl">
                        {cards.map((card) => {
                            return (
                                <div className="flex flex-col items-center justify-center h-full">
                                    <Card card={card} key={card.id} />
                                    <div className="mt-2 ml-2 flex flex-row gap-2 h-3">
                                        <img key={card.id} src={card.played ? jogouSvg : null}></img>
                                        <img key={card.id} src={card.liked ? likedSvg : null}></img>
                                        <img key={card.id} src={card.complete ? completeSvg : null}></img>
                                        <div className="flex flex-row gap-1 items-center text-xs text-roxo">
                                            {card.score} 
                                            <img className="h-3" key={card.id} src={notaSvg}></img>
                                        </div>
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            </div>
        ),
        tab3: (
            <div 
            className="w-full h-full flex flex-col items-center justify-evenly text-white font-sans">
                <div className=" w-full flex flex-col items-center">
                    <img src={reviewSvg} alt="ícone de escrita" />
                    <h4 className="font-bold text-4xl mt-4">Avaliações</h4>
                    <p className="w-[70%] text-center">Descreva como foi sua experiência com os jogos que jogou</p>
                </div>
            </div>
        ),
        tab4: (
        <div className="w-full h-full flex flex-col items-center justify-evenly text-white font-sans">
            <div className="w-full flex flex-col items-center">
                {/* Usando o completeSvg que você já tem importado */}
                <img src={completeSvg} alt="ícone de troféu ou check" />
                <h4 className="font-bold text-4xl mt-4">Completados</h4>
                <p className="w-[70%] text-center">Mostre quais desafios você já superou e os jogos que conseguiu completar 100%</p>
            </div>
        </div>
        ),
        tab5: (
            <div className="w-full h-full flex flex-col items-center justify-evenly text-white font-sans">
                <div className="w-full flex flex-col items-center">
                    {/* Usando o likedSvg que você já tem importado */}
                    <img src={likedSvg} alt="ícone de coração" />
                    <h4 className="font-bold text-4xl mt-4">Favoritos</h4>
                    <p className="w-[70%] text-center">Destaque aqueles jogos inesquecíveis que moram no seu coração</p>
                </div>
            </div>
        ),
        tab6: (
            <div className="w-full h-full flex flex-col items-center justify-evenly text-white font-sans">
                <div className="w-full flex flex-col items-center">
                    {/* Necessário importar esse SVG no topo */}
                    <img src={diarioSvg} alt="ícone de diário ou calendário" />
                    <h4 className="font-bold text-4xl mt-4">Diário</h4>
                    <p className="w-[70%] text-center">Registre sua jornada diária, conquistas e os momentos mais épicos das suas gameplays</p>
                </div>
            </div>
        ),
        tab7: (
            <div className="w-full h-full flex flex-col items-center justify-evenly text-white font-sans">
                <div className="w-full flex flex-col items-center">
                    {/* Necessário importar esse SVG no topo */}
                    <img src={listaSvg} alt="ícone de lista" />
                    <h4 className="font-bold text-4xl mt-4">Listas</h4>
                    <p className="w-[70%] text-center">Crie listas personalizadas para organizar seu backlog, jogos da franquia ou recomendações</p>
                </div>
            </div>
        )
    }


    

    return (
        <div className="w-6/12 h-6/12 border rounded-2xl bg-dark-card flex flex-row shadow-2xl shadow-black">
            <div className="
            w-6/12 h-full py-4 flex flex-col items-start justify-between
            font-bold text-2xl text-white font-sans

            ">
                {tabs.map((tab) => (
                    <button key={tab.id} className={`
                        text-start
                        ml-4 w-11/12 px-4 py-2
                        border border-cinza rounded-2xl
                        ${activeTab === tab.id ? "border-roxo text-roxo" : "text-white hover:border-roxo"}
                        hover: cursor-pointer
                    `}
                    onClick={() => setActiveTab(tab.id)}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>
            <motion.div
            key={activeTab} 
            initial={{opacity: 0, y: 10}}
            animate={{opacity: 100, y: 0}}
            transition={{duration: 0.5, ease:"easeInOut"}} 
            className="w-7/12 p-4 flex flex-col items-center">
                {tabContent[activeTab]}
            </motion.div>
        </div>
    )
}

const cards = [
    {
        url: gtaImg,
        title: "Title 1",
        score: 5,
        played: false,
        liked: true,
        complete: false,
        id: 1,
    },
    {
        url: gowImg,
        title: "Title 2",
        score: 5,
        played: true,
        liked: true,
        complete: true,
        id: 2,
    },
];