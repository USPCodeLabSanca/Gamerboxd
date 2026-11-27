import React, { useState } from "react";
import EditProfileModal from "../Sections/EditProfileModal";
import ConnectionsModal from "./ConnectionsModal";
import { User, Ellipsis, Ban } from "lucide-react";
import { getErrorMessage } from "../../../api/errors";
import {
  useFollowUser,
  useUnfollowUser,
  useBlockUser,
} from "../../../hooks/useUsers";

export default function ProfileHeader({ user }) {
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [blockMenuIsOpen, setBlockMenuIsOpen] = useState(false);
  const [connectionsModal, setConnectionsModal] = useState(null);

  const stats = [
    { label: "Seguidores", value: user.follower_count, type: "followers" },
    { label: "Seguindo", value: user.following_count, type: "followings" },
  ];

  const dono = user.rel === 40;
  const segue = user.rel === 10 || user.rel === 30;

  const followMutation = useFollowUser(user.user_id);
  const unfollowMutation = useUnfollowUser(user.user_id);
  const blockMutation = useBlockUser(user.user_id);
  const isPending = followMutation.isPending || unfollowMutation.isPending;

  function handleFollowToggle() {
    if (segue) {
      unfollowMutation.mutate();
    } else {
      followMutation.mutate();
    }
  }

  function handleBlock() {
    const confirmed = window.confirm(
      `Tem certeza de que deseja bloquear o usuário ${user.username}?`,
    );

    if (!confirmed) return;

    blockMutation.mutate(undefined, {
      onSuccess: () => {
        setBlockMenuIsOpen(false);
      },
    });
  }

  return (
    <div className="w-6xl flex flex-col items-center justify-center shadow-lg">
      {/* 1. Área do Banner e Informações Principais */}
      <div className="relative w-full h-96 rounded-lg overflow-hidden">
        {/* Imagem de Fundo (Placeholder) */}
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={
            user.banner
              ? { backgroundImage: `url(${user.banner})` }
              : {
                  backgroundImage:
                    "url('https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&q=80')",
                }
          }
        />

        {/* Contêiner de Informações (Nome, Avatar e Stats) */}
        <div className="absolute bottom-0 w-full px-8 pb-4 flex items-end justify-between">
          {/* Lado Esquerdo: Avatar, Nome e Botão */}
          <div className="flex items-center gap-5 bg-cinza/30 rounded-full px-6 py-2">
            {/* Avatar Circular */}
            <div className="w-24 h-24 rounded-full bg-[#4a4d5a] border-4 border-[#2c2c2c] flex items-center justify-center overflow-hidden z-10">
              {user.pfp ? (
                <img
                  src={user.pfp}
                  alt="Avatar"
                  className="w-full h-full object-cover"
                />
              ) : (
                <User className="w-12 h-12 text-gray-400" />
              )}
            </div>

            {/* Username e Botão de Editar */}
            <div className="flex flex-col items-start gap-1 pb-1">
              <h1 className="text-2xl font-bold text-white tracking-wide">
                @{user.username}
              </h1>
              {dono && (
                <button
                  onClick={() => setIsEditModalOpen(true)}
                  className="bg-roxo hover:bg-roxo/80 text-white text-xs font-semibold px-4 py-1 rounded-full transition-colors hover:cursor-pointer"
                >
                  editar perfil
                </button>
              )}
              {!dono && (
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleFollowToggle}
                    disabled={
                      isPending ||
                      blockMutation.isPending ||
                      blockMutation.isSuccess
                    }
                    className="bg-roxo hover:bg-roxo/80 text-white text-xs
                 font-semibold px-4 py-1 rounded-full
                 transition-colors disabled:opacity-50"
                  >
                    {isPending
                      ? "Carregando..."
                      : segue
                        ? "Deixar de seguir"
                        : "Seguir"}
                  </button>

                  {/* Menu de opções */}
                  <div className="relative">
                    <button
                      type="button"
                      aria-label="Opções do perfil"
                      aria-expanded={blockMenuIsOpen}
                      disabled={
                        blockMutation.isPending || blockMutation.isSuccess
                      }
                      onClick={() => setBlockMenuIsOpen((prev) => !prev)}
                      className="p-1 rounded-full bg-black/40 hover:bg-black/60"
                    >
                      <Ellipsis size={20} />
                    </button>

                    {blockMenuIsOpen && (
                      <div
                        className="absolute left-0 bottom-full mb-2
                        w-48 bg-cinza rounded-lg shadow-xl
                        border border-gray-700 z-30 p-1"
                      >
                        <button
                          type="button"
                          onClick={handleBlock}
                          disabled={blockMutation.isPending}
                          className="flex items-center gap-2 w-full px-3 py-2
                       text-sm text-red-400 hover:bg-white/10
                       rounded-lg transition-colors"
                        >
                          <Ban size={16} />

                          {blockMutation.isPending
                            ? "Bloqueando..."
                            : "Bloquear usuário"}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {blockMutation.isError && (
                <p className="text-red-400 text-xs">
                  {getErrorMessage(blockMutation.error)}
                </p>
              )}

              {blockMutation.isSuccess && (
                <p className="text-green-400 text-xs">Usuário bloqueado.</p>
              )}
            </div>
          </div>

          {/* Lado Direito: Estatísticas (Listas, Seguidores, Seguindo) */}
          <div
            className="flex items-center gap-6 pb-2 pr-10
                bg-cinza/30 rounded-full px-6 py-2"
          >
            {stats.map((stat, index) => (
              <React.Fragment key={stat.label}>
                <button
                  type="button"
                  onClick={() => setConnectionsModal(stat.type)}
                  className="group flex flex-col items-center
                           cursor-pointer hover:bg-cinza/20 px-4 py-2 rounded-lg transition-colors"
                >
                  <span
                    className="font-bold text-white text-base
                                 leading-tight group-hover:text-roxo
                                 transition-colors"
                  >
                    {stat.value}
                  </span>

                  <span
                    className="text-gray-200 text-lg
                                 group-hover:text-white
                                 transition-colors"
                  >
                    {stat.label}
                  </span>
                </button>

                {index < stats.length - 1 && (
                  <div className="w-px h-8 bg-gray-500" />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>
      {(user.bio || dono) && (
        <div className="w-full mt-4 px-6 py-4 bg-cinza/30 rounded-lg">
          <h2 className="text-sm font-semibold text-gray-400 mb-2">
            Sobre mim
          </h2>

          <p className="text-white text-sm leading-relaxed whitespace-pre-wrap break-words">
            {user.bio || "Você ainda não adicionou uma biografia."}
          </p>
        </div>
      )}

      {isEditModalOpen && (
        <EditProfileModal
          user={user}
          onClose={() => setIsEditModalOpen(false)}
        />
      )}

      {connectionsModal && (
        <ConnectionsModal
          key={`${user.user_id}-${connectionsModal}`}
          userId={user.user_id}
          username={user.username}
          initialTab={connectionsModal}
          onClose={() => setConnectionsModal(null)}
        />
      )}
    </div>
  );
}
