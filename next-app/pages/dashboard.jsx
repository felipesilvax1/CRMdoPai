import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { supabase } from '../lib/supabaseClient';
import DataTable from '../components/DataTable'; // Reutilizaremos o componente da tabela

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkSessionAndFetchData = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        router.push('/'); // Redireciona para o login se não houver sessão
      } else {
        setUser(session.user);
        // Busca dados da tabela protegida
        const { data: result } = await supabase
          .from('sua_tabela_protegida') // 🚨 Altere para sua tabela
          .select('*')
          .limit(100);
        setData(result || []);
        setLoading(false);
      }
    };
    checkSessionAndFetchData();
  }, [router]);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.push('/');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">Carregando...</div>;
  }

  return (
    <main className="min-h-screen p-4 sm:p-8 bg-gray-900 text-white">
      <div className="w-full max-w-6xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-gray-400">Logado como: {user?.email}</p>
          </div>
          <button
            onClick={handleSignOut}
            className="px-4 py-2 font-semibold text-white bg-red-600 rounded-md hover:bg-red-700"
          >
            Sair
          </button>
        </header>
        <DataTable data={data} loading={!data} />
      </div>
    </main>
  );
}

