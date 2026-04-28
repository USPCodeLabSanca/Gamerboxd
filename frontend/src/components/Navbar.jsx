import { Link } from "react-router-dom";
import { Search, Menu } from "lucide-react";

export default function Navbar() {
  const animatedLink =
    "relative after:content-[''] after:absolute after:left-0 after:-bottom-1 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full hover:text-gray-300 transition-colors";

  return (
    <nav className="w-full bg-black text-white py-4 px-4 md:px-20 flex items-center justify-between sticky top-0 z-20">
      {/* Logo */}
      <h4 className="font-sans font-bold text-4xl">GAMERBOXD</h4>

      {/* Links - Escondidos no celular (hidden), visíveis no PC (md:flex) */}
      <div className="hidden md:flex items-center justify-between gap-6">
        <Link to="/reviews" className={animatedLink}>
          Reviews
        </Link>
        <Link to="/games" className={animatedLink}>
          Games
        </Link>
        <Link to="/lists" className={animatedLink}>
          Lists
        </Link>
        <Link to="/members" className={animatedLink}>
          Members
        </Link>
        <Link to="/login" className={animatedLink}>
          Sign in
        </Link>
        <Link to="/register" className={animatedLink}>
          Create Account
        </Link>
      </div>

      {/* Barra de Pesquisa - Escondida no celular (hidden), visível no PC (md:flex) */}
      <div className="hidden md:flex items-center justify-between bg-gray-400 opacity-60 rounded-full py-2 px-3 w-48">
        <Search size={18} />
        <input
          type="text"
          className="w-10/12 border-none outline-none bg-transparent text-white placeholder-white ml-2"
          placeholder="Search"
        />
      </div>

      {/* Menu Mobile (Hambúrguer) - Visível APENAS no celular (md:hidden) */}
      <div className="md:hidden flex items-center cursor-pointer">
        <Menu size={32} />
      </div>
    </nav>
  );
}
