import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    password: "",
    rememberMe: false,
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(form.username, form.password);
      navigate("/games");
    } catch (err) {
      setError("Falha no login. Verifique se digitou corretamente o nome ou senha.");
    } finally {
      setLoading(false);
    }
  };


  return (
    // celular: flex-col (empilhado) e permite rolar se a tela for muito pequena.
    // PC: flex-row (lado a lado), trava a altura e tira a rolagem.
    <div className="flex flex-col md:flex-row min-h-screen md:h-screen w-full md:overflow-hidden">
      {/* imagem -> celular: largura total e altura fixa (250px). PC: 50% da largura e altura total */}
      <div className="w-full h-62.5 md:h-full md:w-1/2 bg-black shrink-0 shadow-inner">
        <img
          src="/gta-vi.jpg"
          alt="GTA VI"
          className="w-full h-full object-cover object-top block shadow-[inset_0_0_50px_rgba(0,0,0,0.5)]"
        />
        <div className="absolute w-1/2 inset-0 shadow-[0_20px_20px_rgba(0,0,0,0.5)] pointer-events-none"></div>

      </div>

      {/* formulário -> celular: ocupa o resto do espaço. PC: 60% da largura */}
      <div className="w-full md:w-1/2 grow bg-cinza flex flex-col justify-center items-center p-8 py-12 md:py-8">
        <div className="w-full max-w-md">
          <h1 className="text-6xl text-start mb-24 font-sans text-white">
            GAMERBOXD
          </h1>

          <h2 className="text-roxo text-4xl text-start mb-1">Log In</h2>
          <p className="text-sm text-white mb-5 mt-2">
            Não possui uma conta?{" "}
            <Link to="/register" className="text-roxo font-medium hover:underline">
              Cadastre-se aqui
            </Link>
          </p>


          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
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
                required
                onChange={handleChange}
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
              disabled={loading}
              className="bg-roxo hover:bg-white hover:border hover:border-roxo hover:text-roxo hover:cursor-pointer text-white px-1 py-3 rounded-lg mt-4 mx-auto w-full sm:w-3/5 transition-colors"
            >
              {loading ? "Entrando..." : "Login"}
            </button>
          </form>



        </div>
      </div>
    </div>
  );
}
