import { Link } from "react-router-dom";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useRegister } from "../../hooks/useAuth";
import { getErrorMessage } from "../../api/errors";

export default function Register() {
  
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [agreeToTerms, setAgreeToTerms] = useState(false);

  const register = useRegister();
  const navigate = useNavigate();

  function handleSubmit(e) {
    e.preventDefault();

    if (password !== confirmPassword) {
      alert("As senhas não coincidem!");
      return;
    }

    register.mutate({ username, email, password }, {
      onSuccess: () => {
        navigate("/games");
      }
    });
  }


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


          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <input
                name="email"
                type="email"
                placeholder="E-mail"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div>
              <input
                name="username"
                type="text"
                placeholder="Nome de usuário"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div>
              <input
                name="password"
                type="password"
                placeholder="Senha"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div>
              <input
                name="confirmPassword"
                type="password"
                placeholder="Confirmar Senha"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div className="flex items-center text-xs mt-1">
              <label className="flex items-center gap-2 text-white cursor-pointer">
                <input 
                  name="agreeToTerms"
                  type="checkbox"
                  checked={agreeToTerms}
                  onChange={(e) => setAgreeToTerms(e.target.checked)} 
                  className="accent-[#8b7df0] hover:cursor-pointer"
                  required />
                  Concordo com os Termos de Serviço e Política de Privacidade
              </label>
            </div>

            <button
              type="submit"
              disabled={register.isPending}
              className="bg-roxo hover:bg-white hover:border hover:border-roxo hover:text-roxo hover:cursor-pointer text-white py-2.5 px-8 rounded-full mt-4 mx-auto w-full sm:w-3/5 transition-colors"
            >
              {register.isPending ? "Cadastrando..." : "Cadastre-se"}
            </button>
          </form>

          {register.isError && errorCardMessage(getErrorMessage(register.error))}

        </div>
      </div>
    </div>
  );
}

function errorCardMessage(error) {

  return (
    <div className="bg-red-100/50 border border-red-300 text-white px-4 py-3 rounded relative mb-4 mt-30" role="alert">
      <strong className="font-bold">Ops!</strong>
      <span className="block sm:inline"> {error}</span>
    </div>
  );
}