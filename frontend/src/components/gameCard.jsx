const Card = ({ card }) => {
    return (
        <div
            key={card.id}
            className="group relative h-full w-auto aspect-4/5 overflow-hidden bg-neutral-200 rounded-2xl"
        >
            <img src={card.url} alt={card.title} className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-110" />
            <div>{}</div>
        </div>
    );
};

export default Card;
