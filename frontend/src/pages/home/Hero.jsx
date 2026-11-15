import HeroBg from "../../assets/imgs/hornet_landscape.jpg"
import { ParallaxBanner } from "react-scroll-parallax";
import { Link } from "react-router-dom";

export default function HeroParallax() {
    const background = {
        image: HeroBg,
        translateY: [0, 50],
        opacity: [1, 0.3],
        scale: [1.05, 1, 'easeOutCubic'],
        shouldAlwaysCompleteAnimation: true,
    };

    const headline = {
        translateY: [0, 30],
        scale: [1, 1.05, 'easeOutCubic'],
        shouldAlwaysCompleteAnimation: true,
        expanded: false,
        children: (
            <div className="absolute inset-0 flex flex-col items-center pt-32 z-10">
                <MainTitle />
                <CAT />
            </div>
        ),
    };

    const gradientOverlay = {
        opacity: [0, 0.9],
        shouldAlwaysCompleteAnimation: true,
        expanded: false,
        // Gradiente agora vai para "from-cinza" em vez de "from-gray-900"
        children: (
            <div className="absolute inset-0 bg-linear-to-t from-cinza to-transparent pointer-events-none" />
        ),
    };

    return (
        <>
            {/* mobile sem imagem */}
            <div id="hero-mobile" className="md:hidden h-screen bg-cinza flex flex-col items-center justify-center pt-10">
                <MainTitle />
                <CAT />
            </div>

            {/* desktop com imagem */}
            <div className="hidden md:block">
                <ParallaxBanner
                    id="#hero"
                    layers={[background, gradientOverlay, headline]}
                    className="h-screen bg-cinza"
                />
            </div>
        </>
    );
}

function MainTitle() {
    return (
        <div className="flex flex-col items-center mt-10 md:mt-32 w-11/12 md:w-10/12 text-white">
            <h2 className="font-sans font-semibold text-xl md:text-2xl lg:text-5xl text-center">Avalie os jogos que você jogou</h2>
            <h1 className="font-sans font-bold text-3xl md:text-5xl lg:text-6xl mt-2 lg:mt-4 text-center">COMPARTILHE OS QUE VALEM O 100%</h1>
            <p className="font-sans font-medium mt-3 md:mt-5 text-center text-sm md:text-base text-gray-300">A sua rede social para acompanhar e avaliar os seus jogos favoritos</p>
        </div>
    )
}

function CAT() {
    const animatedButton = "relative overflow-hidden bg-roxo px-6 md:px-8 py-3 md:py-4 rounded-4xl text-white font-semibold text-sm md:text-base mt-10 lg:mt-40 after:content-[''] after:absolute after:top-0 after:left-0 after:h-full after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full cursor-pointer transition-colors duration-300 hover:text-black";

    const animatedLink = "relative text-white mt-6 after:content-[''] after:absolute after:left-0 after:-bottom-1 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full hover:text-gray-300 transition-colors cursor-pointer";

    return (
        <div className="flex flex-col items-center">
            <Link to={"/register"} className={animatedButton}>
                <span className="relative z-10 transition-colors duration-300 hover:text-black hover:bg-white cursor-pointer">
                    CADASTRE-SE GRATUITAMENTE
                </span>
            </Link>
            <a href="#about" className={animatedLink}>Como funciona?</a>
        </div>
    );
}