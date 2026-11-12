import { motion as Motion, useTransform, useScroll } from "framer-motion";
import { useRef } from "react";
import Card from "../../components/gameCard";
import { useGames } from "../../hooks/useGames";


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
    const { data } = useGames();
    const cards = (data?.games ?? []).map((game) => ({id: game.game_id, title: game.title, url: game.picture}));
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
                <Motion.h1
                    style={{ x: xTextoCima }}
                    className="absolute top-32 left-10 md:left-40 md:top-16 text-white font-bold text-3xl md:text-5xl z-20"
                >
                    Um catálogo com os jogos mais amados pela comunidade
                </Motion.h1>

                {/* CARROSSEL */}
                <Motion.div style={{ x: xCards }} className="flex gap-8 h-6/12 relative z-10 pl-10 md:pl-40">
                    {cards.map((card) => {
                        return <Card game={card} status={false} key={card.id} className="w-48 md:w-64 shrink-0" />;
                    })} 
                </Motion.div>

                {/* TEXTO 2 (Inferior) */}
                <Motion.h1
                    style={{ x: xTextoBaixo }}
                    className="absolute bottom-32 left-10 md:left-40 text-white font-bold text-3xl md:text-5xl z-20"
                >
                    Para você interagir e compartilhar
                </Motion.h1>

            </div>
        </section>
    );
};
