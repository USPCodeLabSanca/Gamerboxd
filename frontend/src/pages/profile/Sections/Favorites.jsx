export default function Favorites() {
    return (
        <div>
            <div className=" text-[#939191] text-[20px] flex justify-between items-center mb-2">
                <div>Jogos Favoritos</div>
                <div>Ver todos</div>
            </div>
            {/* Div com os jogos favoritos */}
            <div className="flex gap-4 items-center">
                {/* Cada jogo seria um card, aqui só tem um exemplo */}
                <div className="w-48 h-64 bg-gray-700 rounded-lg flex-shrink-0"></div>
                <div className="w-48 h-64 bg-gray-700 rounded-lg flex-shrink-0"></div>
                <div className="w-48 h-64 bg-gray-700 rounded-lg flex-shrink-0"></div>
                <div className="w-48 h-64 bg-gray-700 rounded-lg flex-shrink-0"></div>
            </div>
        </div>
    )
}