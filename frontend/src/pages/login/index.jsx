import { Link } from "react-router-dom";

export default function Login() {
  return (
    // celular: flex-col (empilhado) e permite rolar se a tela for muito pequena.
    // PC: flex-row (lado a lado), trava a altura e tira a rolagem.
    <div className="flex flex-col md:flex-row min-h-screen md:h-[calc(100vh-80px)] w-full md:overflow-hidden">
      {/* imagem -> celular: largura total e altura fixa (250px). PC: 40% da largura e altura total */}
      <div className="w-full h-[250px] md:h-full md:w-[40%] bg-black flex-shrink-0">
        <img
          src="/gta-vi.jpg"
          alt="GTA VI"
          className="w-full h-full object-cover object-center"
        />
      </div>

      {/* formulário -> celular: ocupa o resto do espaço. PC: 60% da largura */}
      <div className="w-full md:w-[60%] flex-grow bg-white flex flex-col justify-center items-center p-8 py-12 md:py-8">
        <div className="w-full max-w-md">
          <h1 className="text-3xl tracking-[0.2em] text-center text-black mb-6">
            GAMERBOXD
          </h1>

          <h2 className="text-[#8b7df0] text-2xl mb-1">Log In</h2>
          <p className="text-xs text-gray-500 mb-5">
            Não possui uma conta?{" "}
            <Link to="/register" className="text-[#8b7df0] hover:underline">
              Cadastre-se aqui
            </Link>
          </p>

          <form className="flex flex-col gap-5">
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

            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center text-xs mt-1 gap-4 sm:gap-0">
              <a href="#" className="text-[#8b7df0] hover:underline">
                Esqueceu sua senha?
              </a>
              <label className="flex items-center gap-2 text-gray-600 cursor-pointer">
                <input type="checkbox" className="accent-[#8b7df0]" />
                Relembrar usuário?
              </label>
            </div>

            <button
              type="submit"
              className="bg-[#8b7df0] hover:bg-[#7262d9] text-white py-2.5 px-8 rounded-full mt-4 mx-auto w-full sm:w-3/5 transition-colors"
            >
              Login
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
