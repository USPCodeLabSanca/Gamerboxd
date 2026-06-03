import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createUser } from "../../services/api";
import { useAuth } from "../../context/AuthContext";

export default function Register() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", username: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.confirm) return setError("As senhas não coincidem.");
    setLoading(true);
    try {
      await createUser(form.username, form.email, form.password);
      await login(form.username, form.password); // loga automaticamente após cadastro
      navigate("/");
    } catch (err) {
      setError(err.detail ?? "Erro ao criar conta.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col md:flex-row min-h-screen w-full">
      <div className="w-full h-62.5 md:h-full md:w-1/2 bg-black shrink-0">
        <img src="/eldenring.jpg" alt="Elden Ring" className="w-full h-full object-cover object-top" />
      </div>

      <div className="w-full md:w-1/2 bg-cinza flex flex-col justify-center items-center p-8">
        <div className="w-full max-w-md">
          <h1 className="text-6xl text-white mb-24 font-bold">GAMERBOXD</h1>
          <h2 className="text-roxo text-4xl mb-1">Criar Conta</h2>
          <p className="text-xs text-white mb-5 mt-2">
            Já possui uma conta?{" "}
            <Link to="/login" className="text-roxo font-medium hover:underline">
              Faça login aqui
            </Link>
          </p>

          {error && (
            <p className="text-red-400 text-sm mb-4 bg-red-400/10 px-4 py-2 rounded-lg">
              {error}
            </p>
          )}

          <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
            <input type="email" placeholder="E-mail" value={form.email} onChange={set("email")}
              className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-roxo transition-colors" />
            <input type="text" placeholder="Nome de usuário" value={form.username} onChange={set("username")}
              className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-roxo transition-colors" />
            <input type="password" placeholder="Senha" value={form.password} onChange={set("password")}
              className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-roxo transition-colors" />
            <input type="password" placeholder="Confirmar senha" value={form.confirm} onChange={set("confirm")}
              className="w-full border-b border-gray-300 py-2 outline-none text-white placeholder-gray-400 bg-transparent focus:border-roxo transition-colors" />
            <label className="flex items-center gap-2 text-white text-xs cursor-pointer">
              <input type="checkbox" className="accent-roxo" required />
              Concordo com os Termos de Serviço e Política de Privacidade
            </label>
            <button type="submit" disabled={loading}
              className="bg-roxo hover:bg-roxo/80 disabled:opacity-50 text-white py-2.5 rounded-full mt-4 mx-auto w-full sm:w-3/5 transition-colors cursor-pointer">
              {loading ? "Criando conta..." : "Cadastrar"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}