import { UserPlus, Gamepad2, Users } from "lucide-react";
import registerPage from "../../assets/imgs/Register.png";
import gamePage from "../../assets/imgs/Game.png";
import reviewPage from "../../assets/imgs/Review.png";
import { motion } from "framer-motion";


const steps = [
    {
        id: 1,
        title: "1. Crie sua conta",
        text: "Ao clicar em criar sua conta, insira um email de sua escolha e defina uma senha. Após isso, escolha um nome de usuário e seu perfil já estará pronto.",
        icon: UserPlus,
        img: registerPage,
    },
    {
        id: 2,
        title: "2. Avalie seus jogos",
        text: "Procure pelos jogos que você já jogou, dê uma nota, marque aqueles que completou 100% ou crie uma lista dos que ainda deseja jogar.",
        icon: Gamepad2,
        img: gamePage,
    },
    {
        id: 3,
        title: "3. Interaja com a comunidade",
        text: "Descreva sua experiência com os jogos que jogou, crie listas temáticas e siga outros/as jogadores/as com os mesmos gostos que o seu.",
        icon: Users,
        img: reviewPage,
    }
];

export default function About() {
    return (
       
        <section id="about" className="w-full min-h-screen h-auto bg-cinza text-white py-20 px-6 flex flex-col items-center text-center">
            
            <h2 className="text-roxo font-bold tracking-widest uppercase text-sm mb-2">Como funciona?</h2>
            <h1 className="text-3xl md:text-5xl font-bold mb-4">Apenas 3 passos para começar</h1>
            <p className="text-gray-400 mb-16 text-lg">Criar seu perfil é rápido e totalmente gratuito</p>

           
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl w-full">
                {steps.map((step) => {
                    return (
                        <motion.div key = {step.id}

                            initial={{opacity: 0, y: 100}}
                            whileInView={{opacity: 100, y: 0}}
                            transition={{duration: 1.5, ease: "easeIn"}}>

                            <Card data={step} />
                            <ImgCard data={step} />
                        </motion.div>
                    )
                })}
            </div>

        </section>
    );
}

// 2. O componente Card recebe a prop "data"
function Card({ data }) {
    // Extraímos o ícone que veio no objeto para poder renderizá-lo como um componente
    const Icon = data.icon;

    return (
        <div className="bg-dark-card h-6/12 rounded-2xl p-8 flex flex-col items-center border border-transparent hover:border-roxo/50 transition-colors duration-300">

            {/* Círculo com o ícone */}
            <div className="w-16 h-16 bg-roxo/10 text-roxo rounded-full flex items-center justify-center mb-6">
                <Icon size={32} />
            </div>

            {/* Textos */}
            <h3 className="text-xl font-bold mb-4 text-white">{data.title}</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
                {data.text}
            </p>

        </div>
    );
}

function ImgCard ({data}) {
    return (
        <img src={data.img} alt={data.title} className="bg-cover mt-5 rounded-2xl border border-transparent hover:border-roxo transition-colors duration-300"></img>
    )
}