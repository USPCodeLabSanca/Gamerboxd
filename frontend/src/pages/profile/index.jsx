import React, { useState } from "react";

// Componentes já criados
import ProfileHeader from "./Sections/ProfileHeader"; // Ajuste o caminho conforme sua estrutura
import ProfileNavBar from "./Sections/ProfileNavBar";
import Favorites from "./Sections/Favorites";
import Completed from "./Sections/Completed";
import RecentReviews from "./Sections/RecentReviews";
import UserLists from "./Sections/UserLists";
import { useGetUser } from "../../hooks/useUsers";
import { useParams } from "react-router-dom";
import { getErrorMessage } from "../../api/errors";

function renderActiveTab(activeTab, user) {
  switch (activeTab) {
    case "home":
      return (
        <div className="w-full flex flex-col gap-10">
          <Favorites user={user} />
          <Completed user={user} />
          <RecentReviews user={user} />
        </div>
      );
    case "diario":
      return <div>Diário</div>;
    case "listas":
      return <UserLists user={user} />;
    case "curtidos":
      return <div>Curtidos</div>;
    case "100%":
      return <div>100%</div>;
    default:
      return null;
  }
}

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState("home");
  const { user_id } = useParams();
  const { data: user, isLoading, isError, error } = useGetUser(user_id);

  if (isLoading) {
    return (
            <div className = "min-h-screen flex items-center justify-center bg-linear-to-b from-cinza to-black text-white font-semibold">
                <div className = "bg-roxo p-6 rounded-lg shadow-lg text-center">
                   <p>Carregando...</p>
                </div>
            </div>
        );
  }
  
  if (isError) {
    return (
            <div className = "min-h-screen flex items-center justify-center bg-linear-to-b from-cinza to-black text-white font-semibold">
                <div className = "bg-red-500 p-6 rounded-lg shadow-lg text-center">
                    <p>{getErrorMessage(error)}</p>
                </div>
            </div>
        );
  }

  return (
    // Container Mestre: Ocupa no mínimo a tela toda, fundo escuro, flex em coluna
    <div className="min-h-screen bg-linear-to-b from-cinza to-black text-white flex flex-col font-sans">
      {/* 2. Área Principal de Conteúdo */}
      {/* O flex-1 faz o main ocupar o restante da tela caso falte conteúdo */}
      {/* pt-20 compensa a altura da Navbar caso ela seja "fixed" no topo */}
      <main className="flex-1 flex flex-col items-center w-full pt-20 pb-16">
        <section>
          <ProfileHeader key={user_id} user={user} />
        </section>
        <section>
          <ProfileNavBar activeTab={activeTab} onTabChange={setActiveTab} />
        </section>

        <div className="w-full max-w-6xl flex flex-col gap-10 px-6 items-center">
          {renderActiveTab(activeTab, user)}
        </div>
      </main>
    </div>
  );
}
