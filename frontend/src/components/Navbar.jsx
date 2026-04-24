import { Link } from "react-router-dom";
import { Search, Menu } from "lucide-react";

export default function Navbar() {
    const animatedLink = "relative after:content-[''] after:absolute after:left-0 after:-bottom-1 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full hover:text-gray-300 transition-colors";

    return (
        <nav className="w-full bg-black text-white py-4 px-4 md:px-20 flex items-center justify-between sticky top-0 z-20">
            <h4 className="font-sans font-bold text-4xl">GAMERBOXD</h4>

            <div className="flex justify-between w-2xl">
                <Link to="/reviews" className={animatedLink}>Reviews</Link>
                <Link to="/games" className={animatedLink}>Games</Link>
                <Link to="/lists" className={animatedLink}>Lists</Link>
                <Link to="/members" className={animatedLink}>Members</Link>
                <Link to="/login" className={animatedLink}>Sign in</Link>
                <Link to="/register" className={animatedLink}>Create Account</Link>
            </div>

            <div className="flex items-center justify-between bg-gray-400 opacity-60 rounded-4xl py-2 px-2 w-40">
                <Search />
                <input type="text" className="w-10/12 border-none outline-0 bg-transparent text-white placeholder-white" placeholder="Search" />
            </div>
        </nav>
    );
}