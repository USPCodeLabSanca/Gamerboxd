import React from 'react';

// Componentes já criados
import Navbar from '../../components/Navbar'; // Ajuste o caminho conforme sua estrutura
import ProfileHeader from './Sections/ProfileHeader'; // Ajuste o caminho conforme sua estrutura
import ProfileNavBar from './Sections/ProfileNavBar';
import Favorites from './Sections/Favorites';
import Completed from './Sections/Completed';
import RecentReviews from './Sections/RecentReviews';

export default function ProfilePage() {
  return (
    // Container Mestre: Ocupa no mínimo a tela toda, fundo escuro, flex em coluna
    <div className="min-h-screen bg-[#2c2c2c] text-white flex flex-col font-sans">
      <Navbar />
      {/* 2. Área Principal de Conteúdo */}
      {/* O flex-1 faz o main ocupar o restante da tela caso falte conteúdo */}
      {/* pt-20 compensa a altura da Navbar caso ela seja "fixed" no topo */}
      <main className="flex-1 flex flex-col items-center w-full pt-20 pb-16">
        
        {/* Container interno para limitar a largura do conteúdo (igual ao mockup) */}
        <div className="w-full max-w-4xl flex flex-col gap-10 px-6">
        
            <section><ProfileHeader /></section>

            <section><ProfileNavBar /></section>

            {/* Jogos Favoritos */}
            <section><Favorites /></section>

            {/* Jogos Completados */}
            <section><Completed /></section>

            {/* Últimas Avaliações */}
            <section><RecentReviews /></section>
        </div>
      </main>
    </div>
  );
}