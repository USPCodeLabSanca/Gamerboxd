import { useState } from 'react';
import { useEditProfile } from '../../../hooks/useUsers';
import { getErrorMessage } from '../../../api/errors';

export default function EditProfileModal({ user, onClose }) {

  const editMutation = useEditProfile();

  const [form, setForm] = useState({
    username: user.username ?? '',
    email: user.email ?? '',
    bio: user.bio ?? '',
    pfp: user.pfp ?? '',
    banner: user.banner ?? '',
  });

  function handleChange(event) {
    const { name, value } = event.target;

    setForm(prev => ({
      ...prev,
      [name]: value,
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

      <div className="w-full max-w-lg max-h-[90vh] overflow-y-auto bg-cinza rounded-2xl shadow-xl p-6 text-white">

        {/* Cabeçalho */}
        <div className="flex items-center justify-between mb-6">

          <h2 className="text-2xl font-bold">
            Editar perfil
          </h2>

          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            &times;
          </button>

        </div>

        {/* Formulário */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">

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
              className="w-full bg-black/30 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-roxo resize-none"
              placeholder="Conte um pouco sobre você..."
            />
          </div>

          {/* Foto de perfil */}
          <div className="flex flex-col gap-1">
            <label htmlFor="pfp" className="text-sm font-medium">
              URL da foto de perfil
            </label>

            <input
              id="pfp"
              name="pfp"
              type="url"
              value={form.pfp}
              onChange={handleChange}
              className="w-full bg-black/30 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-roxo"
              placeholder="https://..."
            />
          </div>

          {/* Banner */}
          <div className="flex flex-col gap-1">
            <label htmlFor="banner" className="text-sm font-medium">
              URL do banner
            </label>

            <input
              id="banner"
              name="banner"
              type="url"
              value={form.banner}
              onChange={handleChange}
              className="w-full bg-black/30 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-roxo"
              placeholder="https://..."
            />
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
              {editMutation.isPending
                ? 'Salvando...'
                : 'Salvar alterações'}
            </button>

          </div>

        </form>

      </div>

    </div>
  );
}