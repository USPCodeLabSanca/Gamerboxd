import React from 'react';
import { User, Gamepad2, Calendar, List, Heart, Trophy } from 'lucide-react';

export default function ProfileHeader() {
  // Dados simulados para os status
  const stats = [
    { label: 'Listas', value: '1k' },
    { label: 'Seguidores', value: '100' },
    { label: 'Seguindo', value: '300' },
  ];

  // Dados do menu de navegação do perfil
  const navItems = [
    { name: 'Jogos', icon: Gamepad2, iconColor: 'text-[#8b5cf6]', active: true }, // Roxo (Ativo)
    { name: 'Diário', icon: Calendar, iconColor: 'text-gray-300', active: false },
    { name: 'Listas', icon: List, iconColor: 'text-gray-300', active: false },
    { name: 'Curtidos', icon: Heart, iconColor: 'text-red-500', active: false },
    { name: '100%', icon: Trophy, iconColor: 'text-yellow-500', active: false },
  ];

  return (
    <div className="w-full flex flex-col">
      
      {/* 1. Área do Banner e Informações Principais */}
      <div className="relative w-full h-56 rounded-t-lg overflow-hidden">
        
        {/* Imagem de Fundo (Placeholder) */}
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: "url('https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&q=80')" }} 
        />
        
        {/* Gradiente escuro para mesclar a imagem com o fundo da página */}
        {/* <div className="absolute inset-0 bg-gradient-to-t from-[#2c2c2c] via-[#2c2c2c]/60 to-transparent" /> */}

        {/* Contêiner de Informações (Nome, Avatar e Stats) */}
        <div className="absolute bottom-0 w-full px-8 pb-4 flex items-end justify-between">
          
          {/* Lado Esquerdo: Avatar, Nome e Botão */}
          <div className="flex items-center gap-5">
            {/* Avatar Circular */}
            <div className="w-24 h-24 rounded-full bg-[#4a4d5a] border-4 border-[#2c2c2c] flex items-center justify-center overflow-hidden z-10">
              <User size={48} className="text-gray-300" />
            </div>
            
            {/* Username e Botão de Editar */}
            <div className="flex flex-col items-start gap-1 pb-1">
              <h1 className="text-2xl font-bold text-white tracking-wide">@username</h1>
              <button className="bg-[#8b5cf6] hover:bg-[#7c3aed] text-white text-xs font-semibold px-4 py-1 rounded-full transition-colors">
                editar perfil
              </button>
            </div>
          </div>

          {/* Lado Direito: Estatísticas (Listas, Seguidores, Seguindo) */}
          <div className="flex items-center gap-6 pb-2">
            {stats.map((stat, index) => (
              <React.Fragment key={stat.label}>
                <div className="flex flex-col items-center">
                  <span className="font-bold text-white text-base leading-tight">{stat.value}</span>
                  <span className="text-gray-400 text-xs">{stat.label}</span>
                </div>
                {/* Linha vertical separadora (exceto no último item) */}
                {index < stats.length - 1 && (
                  <div className="w-px h-8 bg-gray-500/50" />
                )}
              </React.Fragment>
            ))}
          </div>

        </div>
      </div>



    </div>
  );
}

// import React from "react";
// import { User } from "lucide-react";

// export default function ProfileHeader() {
//     return (
//         <div className=" bg-gray-300 flex justify-between items-center">
//             <div className="flex items-center gap-4">
//                 <div><User className="w-16 h-16 text-gray-400 mx-auto mt-4" /></div>
//                 <div className="text-xl font-bold"><h1>John Doe</h1></div>
//             </div>
//             {/* Submenu: Favoritos, Completados, Avaliações */}
//             <div>
//                 <ul className="flex gap-8 justify-center mt-4 text-gray-400">
//                     <li className="hover:text-white cursor-pointer">1k<br></br>Listas</li>
//                     <li className="hover:text-white cursor-pointer">100<br></br>Seguidores</li>
//                     <li className="hover:text-white cursor-pointer">300<br></br>Seguido</li>
//                 </ul>
//             </div>
//         </div>
//     )
// }