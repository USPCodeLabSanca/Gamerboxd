import React from 'react';
import ReviewItem from '../Components/ReviewItem';

export default function RecentReviews() {
    const totalReviews = 4; 
    return (
        <div className='flex flex-col gap-3 items-start'>
            <div className="text-[#939191] text-[20px]">Últimas Avaliações</div>
            <div className='flex flex-col gap-3'>
                {Array.from({ length : totalReviews }).map((_, index) => (
                    <ReviewItem key={index} />))}
            </div>
        </div>
    )
}