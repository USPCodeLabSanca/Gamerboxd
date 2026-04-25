import HeroBg from "../../assets/imgs/hornet_landscape.jpg"


export default function Hero () {
    return (
        <div className="relative h-screen text-black flex flex-col items-center justify-center md:overflow-hidden ">
        
            <div
                className="absolute inset-0 z-0 bg-cover bg-center overflow-hidden"
                style={{
                    backgroundImage: `url(${HeroBg})`,
                    transform: "scale(1.2) translateY(-5%)", // translateY move verticalmente
                }}
            ></div>

            <div className="absolute inset-0 z-0 bg-linear-to-b from-transparent via-black/5 to-black"></div>

            <div className="relative z-10 flex flex-col items-center w-full">
                <MainTitle />
                <div className="flex flex-col-reverse items-center lg:flex-col lg:w-full">
                    <CAT />
                </div>
            </div>
        
        </div>
    )
}

function MainTitle() {
    return (
        <div className="flex flex-col items-center mt-48 w-10/12 text-white">
            <h2 className="font-sans font-semibold text-2xl lg:text-5xl text-center">Avalie os jogos que você jogou</h2>
            <h1 className="font-sans font-bold text-2xl lg:text-6xl lg:mt-4 text-center">COMPARTILHE OS QUE VALEM O 100%</h1>
            <p className="font-sans font-medium mt-5 text-center">A sua rede social para acompanhar e avaliar os seus jogos favoritos</p>
        </div>
    )
}

function CAT() {
    const animatedButton = "relative overflow-hidden bg-white px-8 py-4 rounded-4xl text-black font-semibold mt-10 lg:mt-40 after:content-[''] after:absolute after:top-0 after:left-0 after:h-full after:w-0 after:bg-roxo after:transition-all after:duration-300 hover:after:w-full hover:cursor-pointer transition-colors duration-300 hover:text-white";

    const animatedLink = "relative text-white mt-2 after:content-[''] after:absolute after:left-0 after:-bottom-1 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full hover:text-gray-300 transition-colors";
    return (
        <>
            <button className={animatedButton}>
                <span className="relative z-10 transition-colors duration-300 hover:text-white hover:cursor-pointer">
                    CADASTRE-SE GRATUITAMENTE
                </span>
            </button>
            <a href="" className={animatedLink}>Como funciona?</a>
        </>
    );
}

