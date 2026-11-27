const MENSAGEM_GENERICA_ERRO = "Vish algo deu errado. Tente novamente daqui a pouquinho";
const STATUS_LEGIVEIS = [400, 401, 404, 409];

export function getErrorMessage(error) {
    const res = error.response;

    if (!res) return "Não foi possível conectar ao servidor, tente novamente daqui a pouco";

    if (STATUS_LEGIVEIS.includes(res.status) && res.data?.message) {
        return res.data.message;
    }

    return MENSAGEM_GENERICA_ERRO;
}