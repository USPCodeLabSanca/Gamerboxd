import React from "react";
import { motion } from "framer-motion";

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
    return (
        <div className="w-6/12 h-6/12 border rounded-2xl bg-dark-card">
            <div>

            </div>
            <div>

            </div>
        </div>
    )
}