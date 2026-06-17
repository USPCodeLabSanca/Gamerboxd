import { Link } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const {register} = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    agreeToTerms: false,
  })
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({...form, [e.target.name]: e.target.value})
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (form.password !== form.confirmPassword) {
      setError("As senhas não coincidem.");
      setLoading(false);
      return;
    }

    try {
      await register(form.username, form.email, form.password);
      navigate("/games");
    } catch (err) {
      setError(err.response?.data?.detail || "Erro ao criar conta.");
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="flex flex-col md:flex-row min-h-screen md:h-[calc(100vh-80px)] w-full md:overflow-hidden">
      {/* lado esquerdo (imagem) */}
      <div className="w-full h-62.5 md:h-full md:w-1/2 bg-black shrink-0">
        <img
          src="/eldenring.jpg"
          alt="Elden Ring"
          className="w-full h-full object-cover object-top block"
        />
        <div className="absolute w-1/2 inset-0 shadow-[0_20px_20px_rgba(0,0,0,0.5)] pointer-events-none"></div>
      </div>

      {/* lado lireito (formulario))*/}
      <div className="w-full md:w-1/2 grow bg-cinza flex flex-col justify-center items-center p-8 py-12 md:py-8">
        <div className="w-full max-w-md">
          <h1 className="text-6xl text-start text-white mb-24">
            GAMERBOXD
          </h1>

          <h2 className="text-[#8b7df0] text-4xl mb-1">Criar Conta</h2>
          <p className="text-xs text-white font-light mb-5 mt-2">
            Já possui uma conta? {/* link aponta para o login */}
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
                value={form.email}
                onChange={handleChange}
                required
                className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div>
              <input
                name="username"
                type="text"
                placeholder="Nome de usuário"
                value={form.username}
                onChange={handleChange}
                required
                className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div>
              <input
                name="password"
                type="password"
                placeholder="Senha"
                value={form.password}
                onChange={handleChange}
                required
                className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>

            <div>
              <input
                name="confirmPassword"
                type="password"
                placeholder="Confirmar Senha"
                value={form.confirmPassword}
                onChange={handleChange}
                required
                className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-[#8b7df0] transition-colors"
              />
            </div>
            {error && <div className="text-red-500 text-sm mt-1">{error}</div>}

            <div className="flex items-center text-xs mt-1">
              <label className="flex items-center gap-2 text-white cursor-pointer">
                <input 
                  name="agreeToTerms"
                  type="checkbox"
                  checked={form.agreeToTerms}
                  onChange={(e) => setForm({...form, agreeToTerms: e.target.checked})} 
                  className="accent-[#8b7df0] hover:cursor-pointer"
                  required />
                  Concordo com os Termos de Serviço e Política de Privacidade
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="bg-roxo hover:bg-white hover:border hover:border-roxo hover:text-roxo hover:cursor-pointer text-white py-2.5 px-8 rounded-full mt-4 mx-auto w-full sm:w-3/5 transition-colors"
            >
              {loading ? "Cadastrando..." : "Cadastre-se"}
            </button>
          </form>



        </div>
      </div>
    </div>
  );
}
