import { Link } from "react-router-dom";
import { Search, Menu, X } from "lucide-react";
import { useState } from "react";
import { motion, useMotionValueEvent, useScroll } from "framer-motion";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
    const { scrollY } = useScroll();
    const [menuOpen, setMenuOpen] = useState(false);
    const [isHidden, setHidden] = useState(false);
    const { user, logout } = useAuth();

    useMotionValueEvent(scrollY, "change", (current) => {
        const previous = scrollY.getPrevious() ?? 0;
        if (current > previous && current > 10) {
            setHidden(true);
        } else {
            setHidden(false);
        }
    });

    const animatedLink = "relative after:content-[''] after:absolute after:left-0 after:-bottom-1 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full hover:text-gray-300 transition-colors";

    const links = [
        { to: "/", label: "Home" },
        { to: "/games", label: "Games" },
        { to: "/lists", label: "Lists" },
        { to: "/members", label: "Members" },
    ];

    return (
        <motion.nav
            animate={{ y: isHidden ? "-100%" : "0%" }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="w-full bg-transparent lg:opacity-50 lg:hover:opacity-100 transition-opacity duration-500 text-white py-4 px-4 lg:px-20 flex items-center justify-between fixed top-0 z-50"
        >
            {/* Logo */}
            <h4
                onClick={() => window.location.href = "/"}
                className="font-sans font-bold text-2xl lg:text-4xl hover:cursor-pointer"
            >
                GAMERBOXD
            </h4>

            {/* Links — desktop */}
            <div className="hidden lg:flex gap-6 items-center">
                {links.map(({ to, label }) => (
                    <Link key={to} to={to} className={animatedLink}>{label}</Link>
                ))}

                {user ? (
                    <>
                        <Link to={`/profile/${user.username}`} className={animatedLink}>
                            {user.username}
                        </Link>
                        <button
                            onClick={logout}
                            className="text-white/50 hover:text-white text-sm transition-colors cursor-pointer"
                        >
                            Sair
                        </button>
                    </>
                ) : (
                    <>
                        <Link to="/login" className={animatedLink}>Sign in</Link>
                        <Link to="/register" className={animatedLink}>Create Account</Link>
                    </>
                )}
            </div>

            {/* Search — desktop */}
            <div className="hidden lg:flex items-center bg-gray-400 rounded-4xl py-2 px-3 w-40">
                <Search size={18} />
                <input
                    type="text"
                    className="w-full border-none outline-0 bg-transparent text-white placeholder-white ml-2 hover:ring-amber-50"
                    placeholder="Search"
                />
            </div>

            {/* Botão hamburguer — mobile */}
            <button
                className="lg:hidden text-white"
                onClick={() => setMenuOpen(!menuOpen)}
            >
                {menuOpen ? <X size={28} /> : <Menu size={28} />}
            </button>

            {/* Menu mobile */}
            {menuOpen && (
                <div className="absolute top-full left-0 w-full bg-black/90 flex flex-col items-start gap-5 px-6 py-6 lg:hidden">
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

                    {user ? (
                        <>
                            <Link
                                to={`/profile/${user.username}`}
                                className="text-white text-lg font-medium hover:text-gray-300 transition-colors"
                                onClick={() => setMenuOpen(false)}
                            >
                                {user.username}
                            </Link>
                            <button
                                onClick={() => { logout(); setMenuOpen(false); }}
                                className="text-white/50 hover:text-white text-lg font-medium transition-colors cursor-pointer"
                            >
                                Sair
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="text-white text-lg font-medium hover:text-gray-300 transition-colors" onClick={() => setMenuOpen(false)}>
                                Sign in
                            </Link>
                            <Link to="/register" className="text-white text-lg font-medium hover:text-gray-300 transition-colors" onClick={() => setMenuOpen(false)}>
                                Create Account
                            </Link>
                        </>
                    )}
                </div>
            )}
        </motion.nav>
    );
}