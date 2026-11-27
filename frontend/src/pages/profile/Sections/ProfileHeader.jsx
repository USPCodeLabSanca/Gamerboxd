import React, {useState} from 'react';
import EditProfileModal from '../Sections/EditProfileModal';
import { User} from 'lucide-react';
import { useFollowUser, useUnfollowUser } from '../../../hooks/useUsers';

export default function ProfileHeader({user}) {
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const stats = [
    { label: 'Seguidores', value: user.follower_count },
    { label: 'Seguindo', value: user.following_count },
  ];

  const dono = user.rel === 40;
  const segue = user.rel === 10 || user.rel === 30;

  const followMutation = useFollowUser(user.user_id);
  const unfollowMutation = useUnfollowUser(user.user_id);
  const isPending = followMutation.isPending || unfollowMutation.isPending;

  function handleFollowToggle() {
    if (segue) {
      unfollowMutation.mutate();
    } else {
      followMutation.mutate();
    }
  }

  return (
    <div className="w-6xl flex flex-col items-center justify-center shadow-lg">
      
      {/* 1. Área do Banner e Informações Principais */}
      <div className="relative w-full h-96 rounded-lg overflow-hidden">
        
        {/* Imagem de Fundo (Placeholder) */}
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={user.banner ? { backgroundImage: `url(${user.banner})`} : {backgroundImage: "url('https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&q=80')" }} 
        />

        {/* Contêiner de Informações (Nome, Avatar e Stats) */}
        <div className="absolute bottom-0 w-full px-8 pb-4 flex items-end justify-between">
          
          {/* Lado Esquerdo: Avatar, Nome e Botão */}
          <div className="flex items-center gap-5">
            {/* Avatar Circular */}
            <div className="w-24 h-24 rounded-full bg-[#4a4d5a] border-4 border-[#2c2c2c] flex items-center justify-center overflow-hidden z-10">
              {user.pfp ? (
                <img src={user.pfp} alt="Avatar" className="w-full h-full object-cover" />
              ) : (
                <User className="w-12 h-12 text-gray-400" />
              )}
            </div>
            
            {/* Username e Botão de Editar */}
            <div className="flex flex-col items-start gap-1 pb-1">
              <h1 className="text-2xl font-bold text-white tracking-wide">@{user.username}</h1>
              {dono && (
                <button onClick={() => setIsEditModalOpen(true)} className="bg-roxo hover:bg-roxo/80 text-white text-xs font-semibold px-4 py-1 rounded-full transition-colors hover:cursor-pointer">
                  editar perfil
                </button>
              )}
              {!dono && (
                <button onClick={handleFollowToggle} className={"bg-roxo hover:bg-roxo/80 text-white text-xs font-semibold px-4 py-1 rounded-full transition-colors"}>
                  {segue ? 'Deixar de seguir' : 'Seguir'}
                </button>
              )}
            </div>
          </div>

          {/* Lado Direito: Estatísticas (Listas, Seguidores, Seguindo) */}
          <div className="flex items-center gap-6 pb-2 pr-10 bg-cinza/30 rounded-full px-6 py-2">
            {stats.map((stat, index) => (
              <React.Fragment key={stat.label}>
                <div className="flex flex-col items-center">
                  <span className="font-bold text-white text-base leading-tight">{stat.value}</span>
                  <span className="text-gray-200 text-lg">{stat.label}</span>
                </div>
                {/* Linha vertical separadora (exceto no último item) */}
                {index < stats.length - 1 && (
                  <div className="w-px h-8 bg-gray-500" />
                )}
              </React.Fragment>
            ))}
          </div>

        </div>
      </div>

      {isEditModalOpen && (
        <EditProfileModal user={user} onClose={() => setIsEditModalOpen(false)} />
      )}

    </div>
  );
}