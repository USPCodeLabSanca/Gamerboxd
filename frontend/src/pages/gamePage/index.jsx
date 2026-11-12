import React, { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import Card from "../../components/gameCard";
import Review from "../../components/gameReview";
import List from "../../components/List";
import ReviewModal from "../../components/ReviewModal";
import { useMe } from "../../hooks/useAuth";
import { useCreatedReviews, useReview } from "../../hooks/useReviews";
import { getErrorMessage } from "../../api/errors";
import { useGame, useGames } from "../../hooks/useGames";


import list from "../../assets/icons/lista.svg";

// Adicione no topo do GamePage
export default function GamePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const gameQuery = useGame(id);
  const game = gameQuery.data ? {
    id: gameQuery.data.game_id,
    title: gameQuery.data.title,
    url: gameQuery.data.picture,
    year: gameQuery.data.year,
  } : null;
  const session = useMe();
  const me = session.data;
  const reviews = useCreatedReviews(me?.user_id);
  const existingReview = reviews.data?.pages.flatMap((page) => page.content).find((review) => review.game.game_id === Number(id));
  const savedReview = useReview(existingReview?.review_id);
  const lastPage = reviews.data?.pages.at(-1);
  const searchComplete = reviews.isSuccess && !reviews.hasNextPage && !lastPage?.next_url;
  const canReview = !!me && !reviews.isFetching && (existingReview ? savedReview.isSuccess : searchComplete);
  const reviewLoading = session.isPending || (!!me && reviews.isPending) || reviews.isFetching || (!!existingReview && savedReview.isPending);
  const [modal, setModal] = useState(null);
  const [reviewMessage, setReviewMessage] = useState(null);
  const [wishlist, setWishlist] = useState(false);         // <- novo
  const [completo, setCompleto] = useState(false);         // <- novo

  function handleReview() {
    if (session.isPending) {
      setReviewMessage({gameId: Number(id), text: "Aguarde enquanto verificamos sua sessão."});
    } else if (session.isError) {
      setReviewMessage({gameId: Number(id), text: getErrorMessage(session.error)});
      session.refetch();
    } else if (!me) {
      navigate("/login");
    } else if (reviews.isError || savedReview.isError) {
      setReviewMessage({gameId: Number(id), text: "Não foi possível verificar sua avaliação no servidor. Tente novamente em instantes."});
      if (reviews.isError) reviews.refetch();
      else savedReview.refetch();
    } else if (!canReview) {
      let text = "Não foi possível concluir a consulta das suas avaliações. Acesse seu perfil para conferir.";
      if (reviews.hasNextPage) text = "Consulte as próximas avaliações abaixo antes de criar uma nova.";
      else if (reviewLoading) text = "Aguarde enquanto consultamos sua avaliação.";
      setReviewMessage({gameId: Number(id), text: text});
    } else {
      setReviewMessage(null);
      setModal({gameId: Number(id), review: savedReview.data});
    }
  }

  if (gameQuery.isPending) return (
    <div className="bg-linear-to-b from-cinza to-black min-h-screen flex items-center justify-center">
      <p className="text-white text-4xl">Carregando...</p>
    </div>
  );

  if (gameQuery.isError || !game) return (
    <div className="bg-linear-to-b from-cinza to-black min-h-screen flex flex-col items-center justify-center gap-4 text-white">
      <p>Jogo não encontrado.</p>
      <Link to="/games" className="text-roxo">Voltar ao catálogo</Link>
    </div>
  );

  return (
    <>
      {modal?.gameId === Number(id) && me && <ReviewModal
        game={game}
        isOpen={true}
        review={modal.review}
        onClose={() => setModal(null)}
      />}
      <div className="min-h-screen bg-linear-to-b from-cinza to-black pt-28 pl-20 pr-20 pb-5 grid grid-cols-6 grid-rows-2 gap-x-20">
        <GameHero
          game={game}
          onAvaliar={handleReview}
          reviewLoading={reviewLoading}
          reviewMessage={reviewMessage?.gameId === Number(id) ? reviewMessage.text : null}
          wishlist={wishlist}
          onWishlist={() => setWishlist(w => !w)}
          completo={completo}
          onCompleto={() => setCompleto(c => !c)}
        />
        <Details game={game} />
        <div className="col-span-4">
          {me && reviews.isPending && <p className="text-white mt-10">Consultando suas avaliações...</p>}
          {reviews.isError && <div className="mt-10 text-red-300">
            <p role="alert">Não foi possível verificar sua avaliação. {getErrorMessage(reviews.error)}</p>
            <button disabled={reviews.isFetching} onClick={() => reviews.refetch()}>Tentar novamente</button>
          </div>}
          {me && !existingReview && reviews.hasNextPage && <div className="mt-10 text-white">
            <p>Para conferir se você já avaliou este jogo, consulte as próximas avaliações.</p>
            <button disabled={reviews.isFetching} onClick={() => reviews.fetchNextPage()} className="text-roxo">
              {reviews.isFetchingNextPage ? "Carregando..." : "Consultar próximas avaliações"}
            </button>
          </div>}
          {me && !existingReview && reviews.isSuccess && !reviews.hasNextPage && lastPage?.next_url && <p role="alert" className="text-red-300 mt-10">
            Não foi possível concluir a consulta das suas avaliações. <Link to={`/profile/${me.user_id}`} className="underline">Ver perfil</Link>
          </p>}
          {savedReview.isError && <p role="alert" className="text-red-300">{getErrorMessage(savedReview.error)}</p>}
          {existingReview && <div className="mt-10"><Review review={existingReview} gameClassName="w-28" /></div>}
          <PopularReviews game={game} />
        </div>
        <GameLists />
      </div>
    </>
  );
}

function GameHero({ reviewLoading, reviewMessage, game, onAvaliar, wishlist, onWishlist, completo, onCompleto }) {
  return (
    <div className="flex flex-row items-center self-center gap-4 h-[50%] relative col-span-4 row-span-1">
      <div className="w-[30%]">
        <Card game={game} status={true} />
      </div>
      <div className="flex flex-col gap-4">
        <h1 className="text-white text-5xl font-bold">{game.title}</h1>
        <div className="flex flex-row gap-4 text-white">
          <p>{game.year}</p>
        </div>
        <p className="text-white">Sinopse</p>
        <div className="flex flex-row items-center justify-center gap-4 text-white font-semibold absolute bottom-0">

          <button
            onClick={onAvaliar}
            aria-busy={reviewLoading}
            aria-describedby={reviewMessage ? "review-feedback" : undefined}
            className="w-40 h-10 py-2 bg-roxo/80 hover:bg-roxo rounded-sm shadow-md cursor-pointer transition-colors"
          >
            AVALIE
          </button>

          {reviewMessage && <p id="review-feedback" role="alert" className="absolute top-full left-0 mt-2 text-sm text-red-300 font-normal">{reviewMessage}</p>}

          <button
            onClick={onWishlist}
            className={`w-40 h-10 py-2 rounded-sm shadow-md cursor-pointer transition-colors ${wishlist ? "bg-turquesa text-white font-bold" : "bg-turquesa/80 hover:bg-turquesa"
              }`}
          >
            {wishlist ? "✓ NA WISHLIST" : "QUERO JOGAR"}
          </button>

          <button
            onClick={onCompleto}
            className={`w-40 h-10 flex items-center justify-center group relative overflow-hidden rounded-sm shadow-md cursor-pointer transition-colors ${completo ? "bg-amarelo text-white font-bold" : "bg-amarelo/90"
              }`}
          >
            {!completo && (
              <span className="absolute inset-0 block w-full h-full bg-linear-to-r from-transparent via-white/80 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out -skew-x-12" />
            )}
            <span className="relative z-10">{completo ? "✓ COMPLETEI" : "COMPLETEI"}</span>
          </button>

          <button className="h-9 aspect-square bg-verde/90 rounded-sm shadow-md hover:cursor-pointer flex items-center justify-center">
            <img src={list} alt="list icon" />
          </button>

        </div>
      </div>
    </div>
  );
}

function PopularReviews({ game }) {
  const animatedLink =
    "text-white text-sm hover:cursor-pointer relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-4 py-1 rounded-2xl";

  const reviews = [
    {
      id: 1,
      complete: false,
      content:
        "Esse jogo é incrível! A história é envolvente e os gráficos são de tirar o fôlego. Recomendo para todos os fãs de jogos de ação.",
      author: {
        username: "Gamer123",
        avatar: "https://i.pravatar.cc/150?img=1",
      },
    },
    {
      id: 2,
      complete: false,
      content:
        "Não gostei muito desse jogo. Achei a jogabilidade confusa e a história fraca. Não recomendo.",
      author: {
        username: "Player456",
        avatar: "https://i.pravatar.cc/150?img=2",
      },
    },
    {
      id: 3,
      complete: true,
      content:
        "Esse jogo é mediano. Tem seus momentos bons, mas também tem muitos problemas técnicos. Vale a pena jogar se você for fã do gênero.",
      author: {
        username: "GameLover789",
        avatar: "https://i.pravatar.cc/150?img=3",
      },
    },
  ];

  return (
    <div className="mb-10 col-span-4">
      <div className="mt-20 w-full border-b border-white flex flex-row items-center justify-between py-2">
        <p className="text-white text-sm">Avaliações populares da semana</p>
        <a className={animatedLink}>Mostrar mais</a>
      </div>
      <div className="flex flex-col gap-6 mt-4">
        {reviews.map((review) => {
          return (
            <Review key={review.id} review={review} game={game} gameClassName="w-28" />
          );
        })}
      </div>
    </div>
  );
}

function Details({game}) {
  const [isSelected, setIsSelected] = useState(["Detalhes", "Plataformas", "Studio"].map((item) => item === "Detalhes"));

  return (
    <div className = "col-span-2 row-span-1 self-center">
      <div className="flex flex-row gap-4 mb-4">
        {["Detalhes", "Plataformas", "Studio"].map((item, index) => (
          <button
            key={index}
            className={`text-sm font-semibold px-4 py-2 rounded-tl-lg rounded-tr-lg ${
              isSelected[index] ? "bg-roxo text-white" : "bg-neutral-700 text-gray-400"
            }`}
            onClick={() => {
              const newSelection = [false, false, false];
              newSelection[index] = true;
              setIsSelected(newSelection);
            }}
          >
            {item}
          </button>
        ))}
      </div>
      <div className="bg-neutral-700 p-4 rounded-b-lg text-white">
        {isSelected[0] && (
          <div>
            <p><strong>Gênero:</strong> Não informado</p>
            <p><strong>Ano de lançamento:</strong> {game.year}</p>
          </div>
        )}
        {isSelected[1] && (
          <div>
            <p>Plataformas: não informadas</p>
          </div>
        )}
        {isSelected[2] && (
          <div>
            <p>Studio: não informado</p>
          </div>
        )}
      </div>  
    </div>
  )
}

function GameLists() {
  const { data } = useGames();
  if (!data) return null;
  const games = data.games.map((game) => ({id: game.game_id, title: game.title, url: game.picture}));
  const mockLists = [
    {
      id: 1,
      name: "Melhores jogos de 2025",
      author: "gamer123",
      games: [games[0], games[1], games[4]],
    },
    {
      id: 2,
      name: "Jogos que me fizeram chorar",
      author: "player456",
      games: [games[1], games[3], games[2]],
    },
    {
      id: 3,
      name: "Open worlds imperdíveis",
      author: "gamelover789",
      games: [games[0], games[5], games[2]],
    },
  ];


  const animatedLink =
    "text-white text-sm hover:cursor-pointer relative inline-block z-10 overflow-hidden before:absolute before:inset-0 before:bg-roxo before:-z-10 before:scale-x-0 before:origin-left before:transition-transform before:duration-300 hover:before:scale-x-100 px-4 py-1 rounded-2xl";

  return (
    <div className="col-span-2 row-span-1 self-start">
      <div className="mt-20 w-full border-b border-white flex flex-row items-center justify-between py-2">
        <p className="text-white text-sm">Suas listas com esse jogo</p>
        <a className={animatedLink}>Mostrar mais</a>
      </div>
      <div className="mt-4">
        <List lists={mockLists} />
      </div>
    </div>
  );
}

