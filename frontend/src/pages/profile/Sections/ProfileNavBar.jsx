import { Home, Calendar, TableProperties, Heart, Trophy } from "lucide-react";

const NAV_ITEMS = [
  { id: "home", label: "Home", icon: Home, iconClass: "" },
  { id: "diario", label: "Diário", icon: Calendar, iconClass: "" },
  { id: "listas", label: "Listas", icon: TableProperties, iconClass: "" },
  { id: "curtidos", label: "Curtidos", icon: Heart, iconClass: "text-red-500" },
  { id: "100%", label: "100%", icon: Trophy, iconClass: "text-yellow-500" },
];

export default function ProfileNavBar({ activeTab = "jogos", onTabChange }) {
  return (
    <div className="min-w-4xl flex justify-around pt-8 mb-8 border-b border-white/20">
      {NAV_ITEMS.map(({ id, label, icon: Icon, iconClass }) => {
        const isActive = activeTab === id;
        return (
          <button
            key={id}
            onClick={() => onTabChange?.(id)}
            className={`flex items-center gap-1.5 pb-1 border-b-2 transition-colors ${
              isActive
                ? "text-purple-400 border-purple-500 font-medium"
                : "text-white font-medium border-transparent hover:text-purple-400 hover:cursor-pointer"
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