import { useState } from "react";
import { getErrorMessage } from "../../../api/errors";
import { useEditProfile, useGetBlocks } from "../../../hooks/useUsers";
import { useMe } from "../../../hooks/useAuth";
import { useDebounce } from "../../../hooks/useDebounce";
import { avatarOptions, bannerOptions } from "../../../data/profilePresets";
import { BlockedUserRow } from "../Components/BlockedUserRow";
import { ChevronDown, ShieldBan, Search } from "lucide-react";

export default function EditProfileModal({ user, onClose }) {
  const editMutation = useEditProfile();
  const {data: me} = useMe();
  const [form, setForm] = useState({
    username: user.username ?? "",
    email: me?.email ?? "",
    bio: user.bio ?? "",
    pfp: user.pfp ?? "",
    banner: user.banner ?? "",
  });


  const [showBlockedUsers, setShowBlockedUsers] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  function handleSelectAvatar(url) {
    setForm((prev) => ({
      ...prev,
      pfp: url,
    }));
  }

  function handleSelectBanner(url) {
    setForm((prev) => ({
      ...prev,
      banner: url,
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();

    editMutation.mutate(form, {
      onSuccess: () => {
        onClose();
      },
    });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
      <div className="w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-cinza rounded-2xl shadow-xl p-6 text-white custom-scrollbar">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Editar perfil</h2>

          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            &times;
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          {/* Preview do banner */}
          <div className="relative w-full h-48 rounded-xl overflow-hidden bg-black/30">
            {form.banner ? (
              <img
                src={form.banner}
                alt="Preview do banner"
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                Nenhum banner selecionado
              </div>
            )}

            <div className="absolute bottom-4 left-4 w-20 h-20 rounded-full overflow-hidden border-4 border-[#2c2c2c] bg-[#4a4d5a]">
              {form.pfp ? (
                <img
                  src={form.pfp}
                  alt="Preview do avatar"
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-300 text-sm">
                  Avatar
                </div>
              )}
            </div>
          </div>

          {/* Username */}
          <div className="flex flex-col gap-1">
            <label htmlFor="username" className="text-sm font-medium">
              Username
            </label>
            <input
              id="username"
              name="username"
              value={form.username}
              onChange={handleChange}
              required
              maxLength={25}
              className="w-full bg-black/30 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-roxo"
            />
          </div>

          {/* Email */}
          <div className="flex flex-col gap-1">
            <label htmlFor="email" className="text-sm font-medium">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              required
              className="w-full bg-black/30 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-roxo"
            />
          </div>

          {/* Bio */}
          <div className="flex flex-col gap-1">
            <label htmlFor="bio" className="text-sm font-medium">
              Biografia
            </label>
            <textarea
              id="bio"
              name="bio"
              value={form.bio}
              onChange={handleChange}
              rows={4}
              maxLength={290}
              className="w-full bg-black/30 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-roxo resize-none"
              placeholder="Conte um pouco sobre você..."
            />
            <p className="text-xs text-gray-400 text-right">
              {form.bio.length}/290
            </p>
          </div>

          {/* Escolha de avatar */}
          <div className="flex flex-col gap-3">
            <h3 className="text-lg font-semibold">Escolha um avatar</h3>

            <div className="flex gap-4 overflow-x-auto pb-2 custom-scrollbar">
              {avatarOptions.map((avatar) => {
                const selected = form.pfp === avatar.url;

                return (
                  <button
                    key={avatar.id}
                    type="button"
                    onClick={() => handleSelectAvatar(avatar.url)}
                    className={`shrink-0 w-24 h-24 rounded-full overflow-hidden border-4 transition-all ${
                      selected
                        ? "border-roxo scale-105"
                        : "border-transparent hover:border-gray-400"
                    }`}
                  >
                    <img
                      src={avatar.url}
                      alt={avatar.name}
                      className="w-full h-full object-cover"
                    />
                  </button>
                );
              })}
            </div>
          </div>

          {/* Escolha de banner */}
          <div className="flex flex-col gap-3">
            <h3 className="text-lg font-semibold">Escolha um banner</h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {bannerOptions.map((banner) => {
                const selected = form.banner === banner.url;

                return (
                  <button
                    key={banner.id}
                    type="button"
                    onClick={() => handleSelectBanner(banner.url)}
                    className={`rounded-xl overflow-hidden border-4 transition-all ${
                      selected
                        ? "border-roxo scale-[1.02]"
                        : "border-transparent hover:border-gray-400"
                    }`}
                  >
                    <img
                      src={banner.url}
                      alt={banner.name}
                      className="w-full h-32 object-cover"
                    />
                  </button>
                );
              })}
            </div>
          </div>

          {/* Erro */}
          {editMutation.isError && (
            <p className="text-red-400 text-sm">
              {getErrorMessage(editMutation.error)}
            </p>
          )}

          {/* Botões */}
          <div className="flex justify-end gap-3 mt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={editMutation.isPending}
              className="px-4 py-2 rounded-lg bg-gray-600 hover:bg-gray-500 transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>

            <button
              type="submit"
              disabled={editMutation.isPending}
              className="px-4 py-2 rounded-lg bg-roxo hover:bg-roxo/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {editMutation.isPending ? "Salvando..." : "Salvar alterações"}
            </button>
          </div>
        </form>

        <div className="border-t border-white/10 mt-6 pt-6">
          <button
            type="button"
            onClick={() => setShowBlockedUsers((prev) => !prev)}
            aria-expanded={showBlockedUsers}
            className="w-full flex items-center justify-between
                   bg-black/20 rounded-lg p-4 hover:bg-black/30
                   transition-colors"
          >
            <div className="flex items-center gap-3">
              <ShieldBan size={20} className="text-gray-400" />

              <span className="font-semibold">
                Gerenciar usuários bloqueados
              </span>
            </div>

            <ChevronDown
              size={20}
              className={`transition-transform duration-300 ${
                showBlockedUsers ? "rotate-180" : ""
              }`}
            />
          </button>

          {showBlockedUsers && (
            <div className="mt-5">
              <BlockedUsers />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function BlockedUsers() {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search);

  const {
    data,
    isLoading,
    isError,
    error,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
  } = useGetBlocks({
    pageSize: 10,
    search: debouncedSearch.trim() || null,
  });

  const users = data?.pages.flatMap((page) => page.content) ?? [];

  const total = data?.pages[0]?.total ?? 0;

  return (
    <section className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldBan size={22} className="text-red-400" />

          <h3 className="text-lg font-semibold">Usuários bloqueados</h3>
        </div>

        {data && <span className="text-sm text-gray-400">{total}</span>}
      </div>

      <p className="text-sm text-gray-400">
        Gerencie os usuários que você bloqueou.
      </p>

      {/* Pesquisa */}
      <div
        className="flex items-center gap-2 bg-black/30
                            border border-gray-600 rounded-lg px-3 py-2
                            focus-within:border-roxo"
      >
        <Search size={18} className="text-gray-400" />

        <input
          type="text"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Buscar usuário bloqueado..."
          className="w-full bg-transparent outline-none text-sm"
        />
      </div>

      {/* Lista */}
      <div className="max-h-64 overflow-y-auto custom-scrollbar pr-2">
        {isLoading ? (
          <p className="py-8 text-center text-sm text-gray-400">
            Carregando usuários...
          </p>
        ) : isError && !data ? (
          <p className="py-8 text-center text-red-400 text-sm">
            {getErrorMessage(error)}
          </p>
        ) : users.length === 0 ? (
          <div
            className="flex flex-col items-center gap-3
                                    py-8 text-gray-400"
          >
            <ShieldBan size={36} />

            <p className="text-sm text-center">
              {debouncedSearch
                ? "Nenhum usuário encontrado."
                : "Você não possui usuários bloqueados."}
            </p>
          </div>
        ) : (
          users.map((user) => <BlockedUserRow key={user.user_id} user={user} />)
        )}
      </div>

      {isError && data && (
        <p className="text-red-400 text-sm">{getErrorMessage(error)}</p>
      )}

      {hasNextPage && (
        <button
          type="button"
          onClick={() => fetchNextPage()}
          disabled={isFetchingNextPage}
          className="flex items-center justify-center gap-2
                               text-sm text-gray-300 hover:text-white
                               disabled:opacity-50"
        >
          {isFetchingNextPage ? "Carregando..." : "Carregar mais"}

          <ChevronDown size={16} />
        </button>
      )}
    </section>
  );
}
