import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { supabase } from '../lib/supabaseClient';
import { getEmpresas, checkApiHealth } from '../lib/apiClient';
import DataTable from '../components/DataTable'; // Reutilizaremos o componente da tabela

const DEV_MODE = process.env.NEXT_PUBLIC_DEV_MODE === 'true';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiStatus, setApiStatus] = useState(null);
  const router = useRouter();

  useEffect(() => {
    const checkSessionAndFetchData = async () => {
      // MODO DESENVOLVIMENTO: Bypass autenticação
      if (DEV_MODE) {
        const devUser = localStorage.getItem('dev_user');
        if (!devUser) {
          router.push('/'); // Redireciona para o login se não houver sessão dev
          return;
        }
        setUser(JSON.parse(devUser));
      } else {
        // MODO PRODUÇÃO: Verifica autenticação Supabase
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) {
          router.push('/'); // Redireciona para o login se não houver sessão
          return;
        }
        setUser(session.user);
      }
      
      // Verifica status da API (funciona em ambos os modos)
      const healthCheck = await checkApiHealth();
      setApiStatus(healthCheck);
      
      if (healthCheck.success) {
        // Busca dados da API local (PostgreSQL)
        const response = await getEmpresas(50);
        if (response.success && response.data.dados_completos) {
          setData(response.data.dados_completos);
        }
      }
      
      setLoading(false);
    };
    checkSessionAndFetchData();
  }, [router]);

  const handleSignOut = async () => {
    if (DEV_MODE) {
      localStorage.removeItem('dev_user');
      router.push('/');
    } else {
      await supabase.auth.signOut();
      router.push('/');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">Carregando...</div>;
  }

  return (
    <main className="min-h-screen p-4 sm:p-8 bg-gray-900 text-white">
      <div className="w-full max-w-6xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">
              Dashboard CRM
              {DEV_MODE && <span className="ml-2 text-sm text-yellow-400">(Modo Dev)</span>}
            </h1>
            <p className="text-gray-400">Logado como: {user?.email}</p>
            {apiStatus && (
              <div className="mt-2 flex items-center gap-2">
                <span className={`inline-block w-2 h-2 rounded-full ${apiStatus.success ? 'bg-green-500' : 'bg-red-500'}`}></span>
                <span className="text-xs text-gray-500">
                  {apiStatus.success 
                    ? `API: ${apiStatus.data.database} (${apiStatus.data.host})`
                    : 'API: Desconectada'
                  }
                </span>
              </div>
            )}
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => router.push('/busca-avancada')}
              className="px-4 py-2 font-semibold text-white bg-green-600 rounded-md hover:bg-green-700"
            >
              🔍 Busca
            </button>
            <button
              onClick={() => router.push('/chat-llm')}
              className="px-4 py-2 font-semibold text-white bg-purple-600 rounded-md hover:bg-purple-700"
            >
              🤖 Chat LLM
            </button>
            <button
              onClick={() => router.push('/configuracoes')}
              className="px-4 py-2 font-semibold text-white bg-gray-700 rounded-md hover:bg-gray-600"
            >
              ⚙️ Config
            </button>
            <button
              onClick={handleSignOut}
              className="px-4 py-2 font-semibold text-white bg-red-600 rounded-md hover:bg-red-700"
            >
              Sair
            </button>
          </div>
        </header>

        {!apiStatus?.success && !loading && (
          <div className="mb-4 p-4 bg-yellow-900 border border-yellow-700 rounded-md">
            <p className="text-yellow-200">
              ⚠️ Não foi possível conectar à API. Verifique se o container está rodando: 
              <code className="ml-2 bg-gray-800 px-2 py-1 rounded">docker-compose up -d api</code>
            </p>
          </div>
        )}

        <DataTable data={data} loading={loading} />
      </div>
    </main>
  );
}

