import { Link } from "react-router-dom";

export default function Login() {
  return (
    <div className="flex flex-col md:flex-row min-h-screen md:h-screen w-full md:overflow-hidden">
      
      {/* Imagem (Some no celular, aparece no PC) */}
      <div className="hidden md:block md:h-full md:w-1/2 bg-black shrink-0 shadow-inner relative">
        <img
          src="/gta-vi.jpg"
          alt="GTA VI"
          className="w-full h-full object-cover object-top block shadow-[inset_0_0_50px_rgba(0,0,0,0.5)]"
        />
        <div className="absolute w-full inset-0 shadow-[0_20px_20px_rgba(0,0,0,0.5)] pointer-events-none"></div>
      </div>

      {/* Formulário */}
      <div className="w-full md:w-1/2 grow bg-cinza flex flex-col justify-center items-center p-8 py-12 md:py-8 overflow-x-hidden">
        <div className="w-full max-w-md">
          {/* text-4xl no celular, text-6xl no PC. Margem menor no mobile */}
          <h1 className="text-4xl md:text-6xl text-start mb-12 md:mb-24 font-sans text-white truncate">
            GAMERBOXD
          </h1>

          <h2 className="text-roxo text-3xl md:text-4xl text-start mb-1">Log In</h2>
          <p className="text-xs sm:text-sm text-white mb-5 mt-2">
            Não possui uma conta?{" "}
            <Link to="/register" className="text-roxo font-medium hover:underline">
              Cadastre-se aqui
            </Link>
          </p>

          <form className="flex flex-col gap-5">
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

            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center text-xs mt-1 gap-4 sm:gap-0">
              <a href="#" className="text-[#8b7df0] font-medium hover:underline">
                Esqueceu sua senha?
              </a>
              <label className="flex items-center gap-2 text-white cursor-pointer">
                <input type="checkbox" className="accent-[#8b7df0]" />
                Relembrar usuário?
              </label>
            </div>

            <button
              type="submit"
              className="bg-roxo hover:bg-white hover:border hover:border-roxo hover:text-roxo hover:cursor-pointer text-white px-1 py-3 rounded-lg mt-4 mx-auto w-full sm:w-3/5 transition-colors"
            >
              Login
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}