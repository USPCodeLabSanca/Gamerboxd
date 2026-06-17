import { Link, useNavigate } from "react-router-dom";
import { Search, Menu, X } from "lucide-react";
import { useState } from "react";
import { motion, useMotionValueEvent, useScroll } from "framer-motion";
import { useAuth } from "../hooks/useAuth";

export default function Navbar() {
    const { scrollY } = useScroll();
    const { user } = useAuth();
    const navigate = useNavigate();
    
    const [menuOpen, setMenuOpen] = useState(false);
    const [isHidden, setHidden] = useState(false);

    // O status de logado é derivado diretamente do user
    const isLogged = !!user;

    const handleLogout = () => {
        logout();
        navigate("/home");
        setMenuOpen(false);
    }

    useMotionValueEvent(scrollY, "change", (current) => {
        const previous = scrollY.getPrevious() ?? 0;
        setHidden(current > previous && current > 10);
    });

    const animatedLink = "hover:cursor-pointer  relative after:content-[''] after:absolute after:left-0 after:-bottom-1 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full hover:text-gray-300 transition-colors";

    // Configuração dinâmica dos links baseada na autenticação
    const links = [
        { to: "/", label: "Home" },
        { to: "/games", label: "Jogos" },
        { to: "/lists", label: "Listas" },
        { to: "/members", label: "Membros" },
        isLogged 
            ? { to: `/profile/${user?.username}`, label: "Perfil" } 
            : { to: "/login", label: "Login" },
        !isLogged && { to: "/register", label: "Cadastre-se" },
    ].filter(Boolean); // Remove itens nulos ou falsos

    return (
        <motion.nav
            animate={{ y: isHidden ? "-100%" : "0%" }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="w-full bg-black/50 backdrop-blur-md lg:bg-transparent lg:opacity-50 lg:hover:opacity-100 transition-opacity duration-500 text-white py-4 px-4 lg:px-20 flex items-center justify-between fixed top-0 z-50"
        >
            {/* Logo */}
            <h4 
                onClick={() => navigate("/")} 
                className="font-sans font-bold text-2xl lg:text-4xl hover:cursor-pointer"
            >
                GAMERBOXD
            </h4>

            {/* Links — desktop */}
            <div className="hidden lg:flex gap-6 items-center">
                {links.map(({ to, label }) => (
                    <Link key={to} to={to} className={animatedLink}>{label}</Link>
                ))}
                {isLogged && (
                    <button onClick={handleLogout} className={animatedLink}>Sair</button>
                )}
            </div>

            {/* Search — desktop */}
            <div className="hidden lg:flex items-center bg-gray-400 rounded-full py-2 px-3 w-40">
                <Search size={18} />
                <input
                    type="text"
                    className="w-full border-none outline-0 bg-transparent text-white placeholder-white ml-2"
                    placeholder="Search"
                />
            </div>

            {/* Botão mobile */}
            <button
                className="lg:hidden text-white"
                onClick={() => setMenuOpen(!menuOpen)}
            >
                {menuOpen ? <X size={28} /> : <Menu size={28} />}
            </button>

            {/* Menu mobile — dropdown */}
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
                </div>
            )}
        </motion.nav>
    );
}