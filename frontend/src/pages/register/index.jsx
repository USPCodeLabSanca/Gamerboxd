import { Link } from "react-router-dom";

export default function Register() {
  return (
    <div className="flex flex-col md:flex-row min-h-[calc(100vh-80px)] md:h-[calc(100vh-80px)] w-full md:overflow-hidden">
      {/* lado esquerdo (imagem) */}
      <div className="w-full h-[250px] md:h-full md:w-[40%] bg-black flex-shrink-0">
        <img
          src="/eldenring.jpg"
          alt="Elden Ring"
          className="w-full h-full object-cover object-top block"
        />
      </div>

      {/* lado lireito (formulario))*/}
      <div className="w-full md:w-[60%] flex-grow bg-white flex flex-col justify-center items-center p-8 py-12 md:py-8">
        <div className="w-full max-w-md">
          <h1 className="text-3xl tracking-[0.2em] text-center text-black mb-6">
            GAMERBOXD
          </h1>

          <h2 className="text-[#8b7df0] text-2xl mb-1">Criar Conta</h2>
          <p className="text-xs text-gray-500 mb-5">
            Já possui uma conta? {/* link aponta para o login */}
            <Link to="/login" className="text-[#8b7df0] hover:underline">
              Faça login aqui
            </Link>
          </p>

          <form className="flex flex-col gap-4">
            <div>
              <input
                type="email"
                placeholder="E-mail"
                className="w-full border-b border-gray-300 py-2 outline-none text-gray-800 placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div>
              <input
                type="text"
                placeholder="Nome de usuário"
                className="w-full border-b border-gray-300 py-2 outline-none text-gray-800 placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div>
              <input
                type="password"
                placeholder="Senha"
                className="w-full border-b border-gray-300 py-2 outline-none text-gray-800 placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div>
              <input
                type="password"
                placeholder="Confirmar Senha"
                className="w-full border-b border-gray-300 py-2 outline-none text-gray-800 placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div className="flex items-center text-xs mt-1">
              <label className="flex items-center gap-2 text-gray-600 cursor-pointer">
                <input type="checkbox" className="accent-[#8b7df0]" required />
                Concordo com os Termos de Serviço e Política de Privacidade
              </label>
            </div>

            <button
              type="submit"
              className="bg-[#8b7df0] hover:bg-[#7262d9] text-white py-2.5 px-8 rounded-full mt-4 mx-auto w-full sm:w-3/5 transition-colors"
            >
              Cadastrar
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
