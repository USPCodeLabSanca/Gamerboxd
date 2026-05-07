import React from "react";
import { motion } from "framer-motion";

const links = {
    Plataforma: ["Reviews", "Catálogo", "Listas", "Membros", "Diário"],
    Conta: ["Criar conta", "Entrar", "Perfil", "Configurações"],
    Empresa: ["Sobre nós", "Blog", "Carreiras", "Contato"],
    Legal: ["Termos de uso", "Privacidade", "Cookies"],
};

// Redes sociais apenas como texto estilizado
const socials = [
    { name: "TW", href: "#", label: "Twitter" },
    { name: "IG", href: "#", label: "Instagram" },
    { name: "GH", href: "#", label: "Github" },
];

export default function Footer() {
    return (
        <footer className="w-full bg-black text-white border-t border-white/10">
            {/* Grid principal */}
            <motion.div
                className="max-w-7xl mx-auto px-6 py-16 grid grid-cols-2 md:grid-cols-6 gap-10"
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
                viewport={{ once: true }}
            >
                {/* Seção Logo + Bio */}
                <div className="col-span-2 flex flex-col gap-6">
                    <Logo />
                    <p className="text-gray-400 text-sm leading-relaxed max-w-xs">
                        A rede social dos gamers. Organize sua coleção, escreva reviews e descubra sua próxima obsessão.
                    </p>

                    {/* Redes Sociais em Texto (Substituindo os ícones) */}
                    <div className="flex gap-4">
                        {socials.map((social) => (
                            <a
                                key={social.name}
                                href={social.href}
                                className="text-xs font-bold tracking-widest text-gray-500 hover:text-roxo transition-colors border border-white/10 px-2 py-1 rounded"
                                aria-label={social.label}
                            >
                                {social.name}
                            </a>
                        ))}
                    </div>
                </div>

                {/* Colunas de links dinâmicas */}
                {Object.entries(links).map(([category, items]) => (
                    <div key={category} className="flex flex-col gap-4">
                        <h4 className="text-white font-bold text-xs uppercase tracking-[0.2em]">
                            {category}
                        </h4>
                        <ul className="flex flex-col gap-2">
                            {items.map((item) => (
                                <li key={item}>
                                    <a
                                        href="#"
                                        className="text-gray-500 text-sm hover:text-white transition-all duration-200 inline-block hover:translate-x-1"
                                    >
                                        {item}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
            </motion.div>

            {/* Barra inferior de Copyright */}
            <div className="border-t border-white/5 bg-zinc-950/50 px-6 py-8">
                <div className="max-w-7xl mx-auto flex flex-col md:row items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <span className="h-px w-8 bg-roxo hidden md:block"></span>
                        <p className="text-gray-600 text-[10px] uppercase tracking-widest">
                            © {new Date().getFullYear()} GAMERBOXD — DESIGNED FOR PLAYERS
                        </p>
                    </div>
                    
                    <p className="text-gray-500 text-[10px] uppercase tracking-tighter">
                        BRASIL <span className="text-white/20 mx-2">|</span> GLOBAL
                    </p>
                </div>
            </div>
        </footer>
    );
}

function Logo() {
    return (
        <span className="font-sans font-bold text-2xl lg:text-4xl">
            GAMERBOXD
        </span>
    );
}