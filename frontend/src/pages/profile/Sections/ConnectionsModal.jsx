import { useState, useEffect } from "react";
import { createPortal } from "react-dom";

import {
    X,
    Search,
    Users,
    ArrowDownUp,
    ChevronDown
} from "lucide-react";

import {
    useGetFollowers,
    useGetFollowings
} from "../../../hooks/useUsers";

import { useDebounce } from "../../../hooks/useDebounce";
import { getErrorMessage } from "../../../api/errors";

import ConnectionUserRow from "../Components/ConnectionUserRow";

export default function ConnectionsModal({
    userId,
    username,
    initialTab = "followers",
    onClose
}) {

    const [activeTab, setActiveTab] = useState(initialTab);
    const [search, setSearch] = useState("");
    const [order, setOrder] = useState("");

    const debouncedSearch = useDebounce(search);

    const isFollowers = activeTab === "followers";

    const filters = {
        pageSize: 10,
        search: debouncedSearch.trim() || null,
        order: order || null
    };

    // Habilita apenas a consulta da aba selecionada.
    const followersQuery = useGetFollowers(
        isFollowers ? userId : undefined,
        filters
    );

    const followingsQuery = useGetFollowings(
        !isFollowers ? userId : undefined,
        filters
    );

    const {
        data,
        isLoading,
        isError,
        error,
        fetchNextPage,
        hasNextPage,
        isFetchingNextPage
    } = isFollowers ? followersQuery : followingsQuery;

    const users = data?.pages.flatMap(
        page => page.content
    ) ?? [];

    const total = data?.pages[0]?.total ?? 0;

    // Impede a rolagem da página atrás do modal.
    useEffect(() => {

        const previousOverflow = document.body.style.overflow;

        document.body.style.overflow = "hidden";

        return () => {
            document.body.style.overflow = previousOverflow;
        };

    }, []);

    // Fecha o modal ao pressionar ESC.
    useEffect(() => {

        function handleKeyDown(event) {
            if (event.key === "Escape") {
                onClose();
            }
        }

        document.addEventListener("keydown", handleKeyDown);

        return () => {
            document.removeEventListener("keydown", handleKeyDown);
        };

    }, [onClose]);

    return createPortal(

        <div
            onClick={onClose}
            className="fixed inset-0 z-50 bg-black/70
                       backdrop-blur-sm flex items-center
                       justify-center p-4"
        >

            <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="connections-title"
                onClick={event => event.stopPropagation()}
                className="w-full max-w-lg h-[75vh] max-h-175
                           flex flex-col bg-cinza rounded-2xl
                           shadow-xl text-white overflow-hidden"
            >

                {/* Cabeçalho */}
                <div className="flex items-center justify-between
                                p-5 border-b border-white/10">

                    <div>

                        <h2
                            id="connections-title"
                            className="text-xl font-bold"
                        >
                            Conexões
                        </h2>

                        <p className="text-sm text-gray-400">
                            @{username}
                        </p>

                    </div>

                    <button
                        type="button"
                        onClick={onClose}
                        aria-label="Fechar modal"
                        className="p-2 rounded-full hover:bg-white/10
                                   text-gray-400 hover:text-white
                                   transition-colors"
                    >
                        <X size={22} />
                    </button>

                </div>

                {/* Abas */}
                <div className="flex border-b border-white/10">

                    <button
                        type="button"
                        onClick={() => setActiveTab("followers")}
                        aria-pressed={isFollowers}
                        className={`flex-1 py-4 text-sm font-semibold
                                    border-b-2 transition-colors ${
                            isFollowers
                                ? "border-roxo text-roxo"
                                : "border-transparent text-gray-400 hover:text-white"
                        }`}
                    >
                        Seguidores
                    </button>

                    <button
                        type="button"
                        onClick={() => setActiveTab("followings")}
                        aria-pressed={!isFollowers}
                        className={`flex-1 py-4 text-sm font-semibold
                                    border-b-2 transition-colors ${
                            !isFollowers
                                ? "border-roxo text-roxo"
                                : "border-transparent text-gray-400 hover:text-white"
                        }`}
                    >
                        Seguindo
                    </button>

                </div>

                {/* Pesquisa e ordenação */}
                <div className="p-5 flex flex-col gap-3">

                    <div className="flex items-center gap-2
                                    bg-black/30 border border-gray-600
                                    rounded-lg px-3 py-2
                                    focus-within:border-roxo">

                        <Search size={18} className="text-gray-400" />

                        <input
                            type="text"
                            autoFocus
                            value={search}
                            onChange={event =>
                                setSearch(event.target.value)
                            }
                            placeholder="Buscar por username..."
                            className="w-full bg-transparent
                                       outline-none text-sm"
                        />

                        {search && (
                            <button
                                type="button"
                                aria-label="Limpar pesquisa"
                                onClick={() => setSearch("")}
                            >
                                <X size={16} className="text-gray-400" />
                            </button>
                        )}

                    </div>

                    <div className="flex items-center justify-between">

                        <span className="text-xs text-gray-400">
                            {data ? `${total} usuários` : ""}
                        </span>

                        <div className="flex items-center gap-2">

                            <ArrowDownUp
                                size={16}
                                className="text-gray-400"
                            />

                            <select
                                value={order}
                                onChange={event =>
                                    setOrder(event.target.value)
                                }
                                aria-label="Ordenar usuários"
                                className="bg-cinza border border-gray-600
                                           rounded-lg px-2 py-2 text-xs
                                           outline-none focus:border-roxo"
                            >

                                <option value="">
                                    Ordenação padrão
                                </option>

                                <option value="username">
                                    Nome (A - Z)
                                </option>

                                <option value="!username">
                                    Nome (Z - A)
                                </option>

                            </select>

                        </div>

                    </div>

                </div>

                {/* Lista com scroll personalizado */}
                <div className="flex-1 min-h-0 overflow-y-auto
                                custom-scrollbar px-5 pb-5">

                    {isLoading ? (

                        <div className="flex flex-col gap-4 py-3">

                            {Array.from({ length: 5 }, (_, index) => (

                                <div
                                    key={index}
                                    className="flex items-center gap-3
                                               animate-pulse"
                                >

                                    <div className="w-12 h-12 rounded-full bg-white/10" />

                                    <div className="h-4 w-32 rounded bg-white/10" />

                                    <div className="ml-auto h-8 w-20 rounded-full bg-white/10" />

                                </div>

                            ))}

                        </div>

                    ) : isError && !data ? (

                        <p className="text-sm text-red-400
                                      text-center py-10">
                            {getErrorMessage(error)}
                        </p>

                    ) : users.length === 0 ? (

                        <div className="flex flex-col items-center
                                        justify-center gap-3 py-12
                                        text-gray-400">

                            <Users size={44} />

                            <p className="text-sm text-center">

                                {debouncedSearch
                                    ? "Nenhum usuário encontrado."
                                    : isFollowers
                                        ? "Nenhum seguidor ainda."
                                        : "Não está seguindo ninguém."}

                            </p>

                        </div>

                    ) : (

                        users.map(user => (

                            <ConnectionUserRow
                                key={user.user_id}
                                user={user}
                                onClose={onClose}
                            />

                        ))

                    )}

                    {isError && data && (
                        <p className="text-red-400 text-sm text-center mt-4">
                            {getErrorMessage(error)}
                        </p>
                    )}

                    {/* Paginação */}
                    {hasNextPage && (

                        <div className="flex justify-center mt-5">

                            <button
                                type="button"
                                onClick={() => fetchNextPage()}
                                disabled={isFetchingNextPage}
                                className="flex items-center gap-2
                                           bg-roxo hover:bg-roxo/80
                                           px-5 py-2 rounded-lg text-sm
                                           disabled:opacity-50"
                            >

                                {isFetchingNextPage
                                    ? "Carregando..."
                                    : "Carregar mais"}

                                <ChevronDown size={16} />

                            </button>

                        </div>

                    )}

                </div>

            </div>

        </div>,

        document.body

    );
}