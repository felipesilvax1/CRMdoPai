import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { supabase } from '../lib/supabaseClient';

const DEV_MODE = process.env.NEXT_PUBLIC_DEV_MODE === 'true';

export default function Configuracoes() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const router = useRouter();

  // Configurações
  const [supabaseUrl, setSupabaseUrl] = useState('');
  const [supabaseKey, setSupabaseKey] = useState('');
  const [apiUrl, setApiUrl] = useState('');
  const [llmUrl, setLlmUrl] = useState('');
  const [devMode, setDevMode] = useState(DEV_MODE);

  useEffect(() => {
    const checkSession = async () => {
      if (DEV_MODE) {
        const devUser = localStorage.getItem('dev_user');
        if (!devUser) {
          router.push('/');
          return;
        }
        setUser(JSON.parse(devUser));
      } else {
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) {
          router.push('/');
          return;
        }
        setUser(session.user);
      }

      // Carregar configurações do localStorage
      setSupabaseUrl(localStorage.getItem('SUPABASE_URL') || process.env.NEXT_PUBLIC_SUPABASE_URL || '');
      setSupabaseKey(localStorage.getItem('SUPABASE_KEY') || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '');
      setApiUrl(localStorage.getItem('API_URL') || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000');
      setLlmUrl(localStorage.getItem('LLM_URL') || process.env.NEXT_PUBLIC_LLM_URL || 'http://localhost:8000');
      
      setLoading(false);
    };

    checkSession();
  }, [router]);

  const handleSave = () => {
    setSaving(true);
    setMessage('');

    try {
      // Salvar no localStorage
      localStorage.setItem('SUPABASE_URL', supabaseUrl);
      localStorage.setItem('SUPABASE_KEY', supabaseKey);
      localStorage.setItem('API_URL', apiUrl);
      localStorage.setItem('LLM_URL', llmUrl);

      setMessage('✅ Configurações salvas! Recarregue a página para aplicar.');
      setSaving(false);
    } catch (error) {
      setMessage('❌ Erro ao salvar: ' + error.message);
      setSaving(false);
    }
  };

  const handleReset = () => {
    setSupabaseUrl(process.env.NEXT_PUBLIC_SUPABASE_URL || '');
    setSupabaseKey(process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '');
    setApiUrl(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000');
    setLlmUrl(process.env.NEXT_PUBLIC_LLM_URL || 'http://localhost:8000');
    
    localStorage.removeItem('SUPABASE_URL');
    localStorage.removeItem('SUPABASE_KEY');
    localStorage.removeItem('API_URL');
    localStorage.removeItem('LLM_URL');
    
    setMessage('🔄 Configurações restauradas para os valores padrão!');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">Carregando...</div>;
  }

  return (
    <main className="min-h-screen p-4 sm:p-8 bg-gray-900 text-white">
      <div className="w-full max-w-4xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">⚙️ Configurações</h1>
            <p className="text-gray-400">Gerencie as configurações do sistema</p>
          </div>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 font-semibold text-white bg-gray-700 rounded-md hover:bg-gray-600"
          >
            Voltar ao Dashboard
          </button>
        </header>

        {message && (
          <div className={`mb-6 p-4 rounded-md ${
            message.includes('✅') ? 'bg-green-900 border border-green-700 text-green-200' :
            message.includes('🔄') ? 'bg-blue-900 border border-blue-700 text-blue-200' :
            'bg-red-900 border border-red-700 text-red-200'
          }`}>
            {message}
          </div>
        )}

        <div className="space-y-6">
          {/* Modo de Desenvolvimento */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-bold mb-4">🚀 Modo de Desenvolvimento</h2>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300">Status atual</p>
                <p className="text-sm text-gray-500">
                  {devMode ? 'Autenticação desabilitada (bypass)' : 'Autenticação Supabase ativa'}
                </p>
              </div>
              <div className={`px-4 py-2 rounded-md font-semibold ${
                devMode ? 'bg-yellow-900 text-yellow-200' : 'bg-green-900 text-green-200'
              }`}>
                {devMode ? '🟡 DEV MODE' : '🟢 PRODUÇÃO'}
              </div>
            </div>
            <p className="mt-4 text-sm text-gray-400">
              💡 Para alterar, edite a variável <code className="bg-gray-700 px-2 py-1 rounded">NEXT_PUBLIC_DEV_MODE</code> no arquivo <code className="bg-gray-700 px-2 py-1 rounded">.env.local</code>
            </p>
          </div>

          {/* Supabase */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-bold mb-4">🔐 Supabase (Autenticação)</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Project URL
                </label>
                <input
                  type="text"
                  value={supabaseUrl}
                  onChange={(e) => setSupabaseUrl(e.target.value)}
                  placeholder="https://seu-projeto.supabase.co"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Anon/Public Key
                </label>
                <input
                  type="password"
                  value={supabaseKey}
                  onChange={(e) => setSupabaseKey(e.target.value)}
                  placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div className="text-sm text-gray-400 bg-gray-900 p-3 rounded-md">
                📖 <strong>Como obter:</strong> Supabase Dashboard → Settings → API
              </div>
            </div>
          </div>

          {/* API URLs */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-bold mb-4">🔌 URLs dos Serviços</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  API de Dados (PostgreSQL)
                </label>
                <input
                  type="text"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  placeholder="http://localhost:5000"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  LLM Service (LangChain + Gemma)
                </label>
                <input
                  type="text"
                  value={llmUrl}
                  onChange={(e) => setLlmUrl(e.target.value)}
                  placeholder="http://localhost:8000"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* Ações */}
          <div className="flex gap-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 px-6 py-3 font-bold text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:bg-gray-500 disabled:cursor-not-allowed"
            >
              {saving ? 'Salvando...' : '💾 Salvar Configurações'}
            </button>
            <button
              onClick={handleReset}
              className="px-6 py-3 font-semibold text-white bg-gray-700 rounded-md hover:bg-gray-600"
            >
              🔄 Restaurar Padrões
            </button>
          </div>

          {/* Informações */}
          <div className="bg-blue-900 border border-blue-700 rounded-lg p-4">
            <p className="text-sm text-blue-200">
              ℹ️ <strong>Nota:</strong> As configurações são salvas localmente no navegador. Para aplicar mudanças no Supabase, você precisa recarregar a página.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

