import { Link } from "react-router-dom";
import { Search, Menu, X } from "lucide-react";
import { useState } from "react";
import { motion,  useMotionValueEvent, useScroll } from "framer-motion";

export default function Navbar() {
    const { scrollY } = useScroll();
    const [menuOpen, setMenuOpen] = useState(false);
    const [isHidden, setHidden] = useState(false);

    useMotionValueEvent(scrollY, "change", (current) => {
        const previous = scrollY.getPrevious() ?? 0
        if (current > previous && current > 10) {
            setHidden(true)
        } else {
            setHidden(false)
        }
    })

    const animatedLink = "relative after:content-[''] after:absolute after:left-0 after:-bottom-1 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full hover:text-gray-300 transition-colors";

    const links = [
        {to: "/", label: "Home"},
        { to: "/reviews", label: "Reviews" },
        { to: "/games", label: "Games" },
        { to: "/lists", label: "Lists" },
        { to: "/members", label: "Members" },
        { to: "/login", label: "Sign in" },
        { to: "/register", label: "Create Account" },
    ];

    return (
        <motion.nav 
            animate={{ y: isHidden ? "-100%" : "0%" }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="w-full bg-transparent lg:opacity-50 lg:hover:opacity-100 transition-opacity duration-500 text-white py-4 px-4 lg:px-20 flex items-center justify-between fixed top-0 z-50">

            {/* Logo */}
            <h4 onClick={() => window.location.href = "/"} className="font-sans font-bold text-2xl lg:text-4xl hover:cursor-pointer">GAMERBOXD</h4>

            {/* Links — visível só em desktop */}
            <div className="hidden lg:flex gap-6 items-center">
                {links.map(({ to, label }) => (
                    <Link key={to} to={to} className={animatedLink}>{label}</Link>
                ))}
            </div>

            {/* Search — visível só em desktop */}
            <div className="hidden lg:flex items-center bg-gray-400 rounded-4xl py-2 px-3 w-40">
                <Search size={18} />
                <input
                    type="text"
                    className="w-full border-none outline-0 bg-transparent text-white placeholder-white ml-2 hover:ring-amber-50"
                    placeholder="Search"
                />
            </div>

            {/* Botão hamburguer — visível só em mobile */}
            <button
                className="lg:hidden text-white"
                onClick={() => setMenuOpen(!menuOpen)}
            >
                {menuOpen ? <X size={28} /> : <Menu size={28} />}
            </button>

            {/* Menu mobile — dropdown */}
            {menuOpen && (
                <div className="absolute top-full left-0 w-full bg-black/90 flex flex-col items-start gap-5 px-6 py-6 lg:hidden">

                    {/* Search mobile */}
                    <div className="flex items-center bg-gray-500 rounded-full py-2 px-3 w-full">
                        <Search size={18} />
                        <input
                            type="text"
                            className="w-full border-none outline-0 bg-transparent text-white placeholder-white ml-2"
                            placeholder="Search"
                        />
                    </div>

                    {links.map(({ to, label }) => (
                        <Link
                            key={to}
                            to={to}
                            className="text-white text-lg font-medium hover:text-gray-300 transition-colors"
                            onClick={() => setMenuOpen(false)}
                        >
                            {label}
                        </Link>
                    ))}
                </div>
            )}
        </motion.nav>
    );
}
