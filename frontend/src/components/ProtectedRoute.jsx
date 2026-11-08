import { Outlet, Navigate } from "react-router-dom";
import { useMe } from "../hooks/useAuth";

export default function ProtectedRoute() {

    const {data: user, isLoading, isError} = useMe();

    if (isLoading) {
        return <div>Carregando...</div>;
    }

    if (isError) {
        return (
            <div className = "min-h-screen flex items-center justify-center bg-linear-to-b from-cinza to-black text-white font-semibold">
                <div className = "bg-red-500 p-6 rounded-lg shadow-lg text-center">
                    <p>Erro ao carregar informações do usuário</p>
                    <p>Tente novamente daqui a pouco</p>
                </div>
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    return <Outlet />;

}