import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [credential, setCredential] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();       // evita recarregar a página
    setError("");
    setLoading(true);
    try {
      await login(credential, password);
      navigate("/");        // redireciona pro home após login
    } catch (err) {
      setError(err.detail ?? "Usuário ou senha inválidos.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col md:flex-row min-h-screen w-full">
      <div className="w-full h-62.5 md:h-full md:w-1/2 bg-black shrink-0">
        <img src="/gta-vi.jpg" alt="GTA VI" className="w-full h-full object-cover object-top" />
      </div>

      <div className="w-full md:w-1/2 bg-cinza flex flex-col justify-center items-center p-8">
        <div className="w-full max-w-md">
          <h1 className="text-6xl text-white mb-24 font-bold">GAMERBOXD</h1>
          <h2 className="text-roxo text-4xl mb-1">Log In</h2>
          <p className="text-sm text-white mb-5 mt-2">
            Não possui uma conta?{" "}
            <Link to="/register" className="text-roxo font-medium hover:underline">
              Cadastre-se aqui
            </Link>
          </p>

          {/* Mensagem de erro */}
          {error && (
            <p className="text-red-400 text-sm mb-4 bg-red-400/10 px-4 py-2 rounded-lg">
              {error}
            </p>
          )}

          <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Nome de usuário ou e-mail"
              value={credential}
              onChange={(e) => setCredential(e.target.value)}
              className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-roxo transition-colors"
            />
            <input
              type="password"
              placeholder="Senha"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-roxo transition-colors"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-roxo hover:bg-roxo/80 disabled:opacity-50 text-white px-1 py-3 rounded-lg mt-4 mx-auto w-full sm:w-3/5 transition-colors cursor-pointer"
            >
              {loading ? "Entrando..." : "Login"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}