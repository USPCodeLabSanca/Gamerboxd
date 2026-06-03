import {Gamepad2, Calendar, TableProperties, Heart, Trophy} from "lucide-react"

export default function ProfileNavBar() {
    return (
        <div className="bg-[#2c2c2c] flex justify-center gap-8 py-4 border-b-1">
            <div className="flex gap-1.5">
                <div>
                    <Gamepad2 />
                </div>
                <div>
                    <button className="text-white hover:text-purple-600 transition-colors">Jogos</button>
                </div>
            </div>
            <div className="flex gap-1.5">
                <div>
                    <Calendar />
                </div>
                <div>
                    <button className="text-white hover:text-purple-600 transition-colors">Diário</button>
                </div>
            </div>
            <div className="flex gap-1.5">
                <div>
                    <TableProperties />
                </div>
                <div>
                    <button className="text-white hover:text-purple-600 transition-colors">Listas</button>
                </div>
            </div>
            <div className="flex gap-1.5">
                <div>
                    <Heart className="text-red-500" />
                </div>
                <div>
                    <button className="text-white hover:text-purple-600 transition-colors">Curtidos</button>
                </div>
            </div>
            <div className="flex gap-1.5">
                <div>
                    <Trophy className="text-yellow-500" />
                </div>
                <div>
                    <button className="text-white hover:text-purple-600 transition-colors">100%</button>
                </div>
            </div>
        </div>
    )
}   