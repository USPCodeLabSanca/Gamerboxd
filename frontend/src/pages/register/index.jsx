import { Link } from "react-router-dom";

export default function Register() {
  return (
    <div className="flex flex-col md:flex-row min-h-screen md:h-[calc(100vh-80px)] w-full md:overflow-hidden">
      
      {/* imagem -> sem no mobile, visível no desktop */}
      <div className="hidden md:block md:h-full md:w-1/2 bg-black shrink-0 relative">
        <img
          src="/eldenring.jpg"
          alt="Elden Ring"
          className="w-full h-full object-cover object-top block"
        />
        {/* sombra com w-full */}
        <div className="absolute w-full inset-0 shadow-[0_20px_20px_rgba(0,0,0,0.5)] pointer-events-none"></div>
      </div>

      {/* formulario -> Ocupa 100% no mobile e 50% no desktop */}
      <div className="w-full md:w-1/2 grow bg-cinza flex flex-col justify-center items-center p-8 py-12 md:py-8 overflow-x-hidden">
        <div className="w-full max-w-md">
          {/* Título e margem reduzidos no celular */}
          <h1 className="text-4xl md:text-6xl text-start mb-12 md:mb-24 font-sans text-white truncate">
            GAMERBOXD
          </h1>

          <h2 className="text-[#8b7df0] text-3xl md:text-4xl mb-1">Criar Conta</h2>
          <p className="text-xs text-white font-light mb-5 mt-2">
            Já possui uma conta? {/* link para o login */}
            <Link to="/login" className="text-[#8b7df0] font-medium hover:underline">
              Faça login aqui
            </Link>
          </p>

          <form className="flex flex-col gap-4">
            <div>
              <input
                type="email"
                placeholder="E-mail"
                className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div>
              <input
                type="text"
                placeholder="Nome de usuário"
                className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div>
              <input
                type="password"
                placeholder="Senha"
                className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div>
              <input
                type="password"
                placeholder="Confirmar Senha"
                className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div className="flex items-center text-xs mt-1">
              <label className="flex items-center gap-2 text-white cursor-pointer">
                <input type="checkbox" className="accent-[#8b7df0] hover:cursor-pointer" required />
                Concordo com os Termos de Serviço e Política de Privacidade
              </label>
            </div>

            <button
              type="submit"
              className="bg-roxo hover:bg-white hover:border hover:border-roxo hover:text-roxo hover:cursor-pointer text-white py-2.5 px-8 rounded-full mt-4 mx-auto w-full sm:w-3/5 transition-colors"
            >
              Cadastrar
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}