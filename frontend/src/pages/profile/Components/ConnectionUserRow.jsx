import { User } from "lucide-react";
import { Link } from "react-router-dom";

import {
    useGetUser,
    useFollowUser,
    useUnfollowUser
} from "../../../hooks/useUsers";

import { getErrorMessage } from "../../../api/errors";

export default function ConnectionUserRow({ user, onClose }) {

    const {
        data: userDetails,
        isLoading,
        isFetching,
        isError
    } = useGetUser(user.user_id);

    const followMutation = useFollowUser(user.user_id);
    const unfollowMutation = useUnfollowUser(user.user_id);

    const dono = userDetails?.rel === 40;

    const segue =
        userDetails?.rel === 10 ||
        userDetails?.rel === 30;

    const isPending =
        followMutation.isPending ||
        unfollowMutation.isPending;

    const mutationError =
        followMutation.error || unfollowMutation.error;

    function handleFollowToggle() {

        if (segue) {
            unfollowMutation.mutate();
        } else {
            followMutation.mutate();
        }

    }

    return (
        <div className="flex flex-col gap-2 border-b border-white/10 py-3">

            <div className="flex items-center justify-between gap-3">

                {/* Avatar e username */}
                <Link 
                    to={`/profile/${user.user_id}`}
                    onClick={onClose}
                    className=" group flex items-center gap-3 min-w-0 cursor-pointer">

                    <div className="w-12 h-12 shrink-0 rounded-full
                                    bg-black/30 overflow-hidden
                                    flex items-center justify-center">

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

                    <div className="flex flex-col min-w-0">

                        <span className="text-sm font-semibold truncate">
                            @{user.username}
                        </span>

                        {dono && (
                            <span className="text-xs text-gray-400">
                                Você
                            </span>
                        )}

                    </div>

                </Link>

                {/* Botão de seguir */}
                {isLoading ? (

                    <div className="w-24 h-8 rounded-full
                                    bg-white/10 animate-pulse" />

                ) : isError || !userDetails ? (

                    <span className="text-xs text-gray-400">
                        Indisponível
                    </span>

                ) : !dono && (

                    <button
                        type="button"
                        onClick={handleFollowToggle}
                        disabled={isPending || isFetching}
                        className={`text-xs font-semibold px-4 py-2
                                    rounded-full transition-colors
                                    shrink-0 disabled:opacity-50
                                    disabled:cursor-not-allowed ${
                            segue
                                ? "border border-gray-500 hover:bg-white/10"
                                : "bg-roxo hover:bg-roxo/80"
                        }`}
                    >

                        {isPending
                            ? "Carregando..."
                            : segue
                                ? "Deixar de seguir"
                                : "Seguir"}

                    </button>

                )}

            </div>

            {mutationError && (
                <p className="text-red-400 text-xs">
                    {getErrorMessage(mutationError)}
                </p>
            )}

        </div>
    );
}