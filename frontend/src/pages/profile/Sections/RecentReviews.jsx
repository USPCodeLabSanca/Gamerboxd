import ReviewItem from '../Components/ReviewItem';
import { useUserReviews } from '../../../hooks/useReviews';
import { getErrorMessage } from '../../../api/errors';

export default function RecentReviews({ user }) {
    const { data, isLoading, error, hasNextPage, fetchNextPage, isFetchingNextPage } = useUserReviews(user.user_id);
    const reviews = data?.pages.flatMap((page) => page.content) ?? [];
    return (
        <div className="flex flex-col gap-4 items-start w-full">
            <h2 className="text-[#939191] text-[20px]">Últimas Avaliações</h2>
            {isLoading && <p>Carregando reviews...</p>}
            {error && <p role="alert">{getErrorMessage(error)}</p>}
            {!isLoading && !error && reviews.length === 0 && <p>Nenhuma review disponível.</p>}
            {reviews.map((review) => <ReviewItem key={review.review_id} review={review} />)}
            {hasNextPage && <button disabled={isFetchingNextPage} onClick={() => fetchNextPage()}>{isFetchingNextPage ? "Carregando..." : "Mostrar mais"}</button>}
        </div>
    );
}
