import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { supabase } from '../lib/supabaseClient';
import AuthForm from '../components/AuthForm';

const DEV_MODE = process.env.NEXT_PUBLIC_DEV_MODE === 'true';

export default function LoginPage() {
  const router = useRouter();

  useEffect(() => {
    // MODO DESENVOLVIMENTO: Bypass autenticação
    if (DEV_MODE) {
      const devUser = localStorage.getItem('dev_user');
      if (devUser) {
        router.push('/dashboard');
      }
      return; // Não configura listeners do Supabase em dev mode
    }

    // Redireciona se o usuário já estiver logado
    const checkUser = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        router.push('/dashboard');
      }
    };
    checkUser();

    // Escuta por mudanças no estado de autenticação (ex: login bem-sucedido)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        router.push('/dashboard');
      }
    });

    // Limpa a inscrição quando o componente é desmontado
    return () => subscription.unsubscribe();
  }, [router]);

  // MODO DESENVOLVIMENTO: Formulário simplificado
  if (DEV_MODE) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg shadow-md">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-white">🚀 Modo Desenvolvimento</h1>
            <p className="mt-2 text-sm text-yellow-400">
              Autenticação desabilitada para testes
            </p>
          </div>
          
          <div className="p-4 bg-blue-900 border border-blue-700 rounded-md">
            <p className="text-sm text-blue-200">
              ℹ️ Você está no modo de desenvolvimento. A autenticação do Supabase está desabilitada.
            </p>
          </div>

          <button
            onClick={() => {
              localStorage.setItem('dev_user', JSON.stringify({
                email: 'dev@teste.com',
                id: 'dev-user-id'
              }));
              router.push('/dashboard');
            }}
            className="w-full px-4 py-3 font-bold text-white bg-indigo-600 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 focus:ring-offset-gray-900"
          >
            Entrar no Dashboard (Sem Login)
          </button>

          <div className="pt-4 border-t border-gray-700">
            <p className="text-xs text-gray-400 text-center">
              Para habilitar autenticação real, configure o Supabase e altere<br/>
              <code className="bg-gray-700 px-2 py-1 rounded">NEXT_PUBLIC_DEV_MODE=false</code><br/>
              no arquivo <code className="bg-gray-700 px-2 py-1 rounded">.env.local</code>
            </p>
          </div>
        </div>
      </div>
    );
  }

  // MODO PRODUÇÃO: Formulário normal
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900">
      <AuthForm />
    </div>
  );
}

