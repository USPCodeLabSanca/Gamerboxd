import { Gamepad2, Calendar, TableProperties, Heart, Trophy } from "lucide-react";

const NAV_ITEMS = [
  { id: "jogos", label: "Jogos", icon: Gamepad2, iconClass: "" },
  { id: "diario", label: "Diário", icon: Calendar, iconClass: "" },
  { id: "listas", label: "Listas", icon: TableProperties, iconClass: "" },
  { id: "curtidos", label: "Curtidos", icon: Heart, iconClass: "text-red-500" },
  { id: "100%", label: "100%", icon: Trophy, iconClass: "text-yellow-500" },
];

export default function ProfileNavBar({ activeTab = "jogos", onTabChange }) {
  return (
    <div className="bg-[#2c2c2c] flex justify-center gap-8 py-4 border-b border-white/20">
      {NAV_ITEMS.map(({ id, label, icon: Icon, iconClass }) => {
        const isActive = activeTab === id;
        return (
          <button
            key={id}
            onClick={() => onTabChange?.(id)}
            className={`flex items-center gap-1.5 pb-1 border-b-2 transition-colors ${
              isActive
                ? "text-purple-400 border-purple-500 font-medium"
                : "text-white border-transparent hover:text-purple-400"
            }`}
          >
            <Icon className={`w-4 h-4 ${iconClass}`} />
            <span>{label}</span>
          </button>
        );
      })}
    </div>
  );
}