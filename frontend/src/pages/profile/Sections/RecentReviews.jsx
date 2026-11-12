import { useParams } from 'react-router-dom';
import ReviewItem from '../Components/ReviewItem';
import { useCreatedReviews } from '../../../hooks/useReviews';
import { getErrorMessage } from '../../../api/errors';

export default function RecentReviews() {
    const { user_id } = useParams();
    const reviews = useCreatedReviews(user_id);
    return (
        <div className='flex flex-col gap-3 items-start'>
            <div className="text-[#939191] text-[20px]">Últimas Avaliações</div>
            {reviews.isPending && <p>Carregando avaliações...</p>}
            {reviews.isError && <p role="alert">{getErrorMessage(reviews.error)}</p>}
            {reviews.data?.pages[0].total === 0 && <p>Nenhuma avaliação para mostrar.</p>}
            <div className="flex flex-col gap-6 w-full">
                {reviews.data?.pages.flatMap((page) => page.content).map((review) => (
                    <ReviewItem key={review.review_id} review={review} />
                ))}
            </div>
            {reviews.hasNextPage && (
                <button disabled={reviews.isFetchingNextPage} onClick={() => reviews.fetchNextPage()} className="text-roxo">
                    {reviews.isFetchingNextPage ? 'Carregando...' : 'Mostrar mais'}
                </button>
            )}
        </div>
    )
}
