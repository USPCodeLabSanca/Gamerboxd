export default function Favorites() {

    const animatedLink ="hover:text-white hover:cursor-pointer relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-4 py-1 rounded-2xl"

    return (
        <div className = "min-w-4xl flex flex-col items-center">
            <div className="w-full text-white/50 text-[20px] flex items-center justify-between py-2 mb-2">
                <div>Jogos Favoritos</div>
                <div className={animatedLink}>Ver todos</div>
            </div>
            {/* Div com os jogos favoritos */}
            <div className="flex gap-4 items-center">
                {/* Cada jogo seria um card, aqui só tem um exemplo */}
                <div className="w-48 h-64 bg-gray-700 rounded-lg flex-shrink-0"></div>
                <div className="w-48 h-64 bg-gray-700 rounded-lg flex-shrink-0"></div>
                <div className="w-48 h-64 bg-gray-700 rounded-lg flex-shrink-0"></div>
                <div className="w-48 h-64 bg-gray-700 rounded-lg flex-shrink-0"></div>
                <div className="w-48 h-64 bg-gray-700 rounded-lg flex-shrink-0"></div>
                <div className="w-48 h-64 bg-gray-700 rounded-lg flex-shrink-0"></div>
            </div>
        </div>
    )
}