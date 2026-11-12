import Review from '../../../components/gameReview';

export default function ReviewItem({ review }) {
    return <Review review={review} gameClassName="w-24" />;
}
