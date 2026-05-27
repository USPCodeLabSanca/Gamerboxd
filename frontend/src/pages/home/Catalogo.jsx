import { motion, useTransform, useScroll } from "framer-motion";
import { useRef } from "react";
import Card from "../../components/gameCard";
import gtaImg from "../../assets/imgs/gta.png"
import gowImg from "../../assets/imgs/ragnarok.png"
import silksongImg from "../../assets/imgs/silksong.png"
import rdr2Img from "../../assets/imgs/rdr2.jpg"
import cyberpunkImg from "../../assets/imgs/cyberpunk2077.png"
import clairImg from "../../assets/imgs/clair-obscure.png"


export default function Catalogo() {
    return (
        <>
            <div className="hidden lg:block">
                <HorizontalScrollCarousel />
            </div>
            <div className="md:hidden">

            </div>
        </>
    )
}



const HorizontalScrollCarousel = () => {
    const targetRef = useRef(null);
    const { scrollYProgress } = useScroll({
        target: targetRef,
        offset: ["start start", "end end"]
    });

    // 1. Animação do Carrossel (Move constantemente de 1% a -95%)
    const xCards = useTransform(scrollYProgress, [0, 1], ["1%", "-100%"]);

    // 2. Animação do Texto Superior (Fica parado até 75% do scroll, depois sai pela esquerda)
    const xTextoCima = useTransform(scrollYProgress, [0, 0.5, 1], ["0vw", "0vw", "-100vw"]);

    // 3. Animação do Texto Inferior (Escondido na direita até 75%, depois entra na tela)
    const xTextoBaixo = useTransform(scrollYProgress, [0, 0.5, 1], ["100vw", "0vw", "0vw"]);

    return (
        <section ref={targetRef} className="relative h-[300vh] bg-linear-to-b from-black to-cinza">
            {/* O container sticky segura TUDO na tela (textos e carrossel) */}
            <div className="sticky top-0 flex h-screen flex-col items-start justify-center overflow-hidden">

                {/* TEXTO 1 (Superior) */}
                <motion.h1
                    style={{ x: xTextoCima }}
                    className="absolute top-32 left-10 md:left-40 md:top-16 text-white font-bold text-3xl md:text-5xl z-20"
                >
                    Um catálogo com os jogos mais amados pela comunidade
                </motion.h1>

                {/* CARROSSEL */}
                <motion.div style={{ x: xCards }} className="flex gap-8 h-6/12 relative z-10 pl-10 md:pl-40">
                    {cards.map((card) => {
                        return <Card game={card} status={false} key={card.id} />;
                    })} 
                </motion.div>

                {/* TEXTO 2 (Inferior) */}
                <motion.h1
                    style={{ x: xTextoBaixo }}
                    className="absolute bottom-32 left-10 md:left-40 text-white font-bold text-3xl md:text-5xl z-20"
                >
                    Para você interagir e compartilhar
                </motion.h1>

            </div>
        </section>
    );
};


const cards = [
    {
        url: gtaImg,
        title: "Title 1",
        id: 1,
    },
    {
        url: gowImg,
        title: "Title 2",
        id: 2,
    },
    {
        url: rdr2Img,
        title: "Title 3",
        id: 3,
    },
    {
        url: silksongImg,
        title: "Title 4",
        id: 4,
    },
    {
        url: cyberpunkImg,
        title: "Title 5",
        id: 5,
    },
    {
        url: clairImg,
        title: "Title 6",
        id: 6,
    },
];