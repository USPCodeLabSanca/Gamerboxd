import { User, ShieldOff } from 'lucide-react';
import { useUnblockUser } from '../../../hooks/useUsers';
import { getErrorMessage } from '../../../api/errors';

export function BlockedUserRow({ user }) {

    const unblockMutation = useUnblockUser(user.user_id);

    function handleUnblock() {
        unblockMutation.mutate();
    }

    return (
        <div className="flex flex-col gap-2 border-b border-white/10 py-3">

            <div className="flex items-center justify-between gap-3">

                <div className="flex items-center gap-3 min-w-0">

                    <div className="w-12 h-12 shrink-0 rounded-full bg-black/30 overflow-hidden flex items-center justify-center">

                        {user.pfp ? (
                            <img
                                src={user.pfp}
                                alt={user.username}
                                className="w-full h-full object-cover"
                            />
                        ) : (
                            <User size={24} className="text-gray-400" />
                        )}

                    </div>

                    <span className="font-medium text-sm truncate">
                        @{user.username}
                    </span>

                </div>

                <button
                    type="button"
                    onClick={handleUnblock}
                    disabled={unblockMutation.isPending}
                    className="flex items-center gap-2 text-xs font-semibold
                               border border-roxo text-white rounded-lg
                               px-3 py-2 hover:bg-roxo/20 transition-colors
                               disabled:opacity-50 shrink-0"
                >
                    <ShieldOff size={15} />

                    {unblockMutation.isPending
                        ? 'Desbloqueando...'
                        : 'Desbloquear'}
                </button>

            </div>

            {unblockMutation.isError && (
                <p className="text-xs text-red-400">
                    {getErrorMessage(unblockMutation.error)}
                </p>
            )}

        </div>
    );
}