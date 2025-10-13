import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { supabase } from '../lib/supabaseClient';
import DataTable from '../components/DataTable';

const DEV_MODE = process.env.NEXT_PUBLIC_DEV_MODE === 'true';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export default function BuscaAvancada() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Opções de filtros
  const [ufs, setUfs] = useState([]);
  const [municipios, setMunicipios] = useState([]);
  const [municipiosBusca, setMunicipiosBusca] = useState('');

  // Filtros selecionados
  const [ufSelecionada, setUfSelecionada] = useState('');
  const [municipioSelecionado, setMunicipioSelecionado] = useState('');
  const [situacaoSelecionada, setSituacaoSelecionada] = useState('02'); // Padrão: Ativas
  const [limiteSelecionado, setLimiteSelecionado] = useState(50);

  // Resultados
  const [dados, setDados] = useState([]);
  const [totalEncontrado, setTotalEncontrado] = useState(0);
  const [buscando, setBuscando] = useState(false);

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

      // Carregar UFs
      carregarUFs();
      setLoading(false);
    };

    checkSession();
  }, [router]);

  const carregarUFs = async () => {
    try {
      console.log('Carregando UFs de:', `${API_URL}/filtros/ufs`);
      const response = await fetch(`${API_URL}/filtros/ufs`);
      const data = await response.json();
      console.log('UFs recebidas:', data.ufs?.length || 0);
      if (data.ufs && Array.isArray(data.ufs)) {
        setUfs(data.ufs);
        console.log('UFs setadas no estado:', data.ufs.length);
      } else {
        console.error('Formato inválido de UFs:', data);
      }
    } catch (error) {
      console.error('Erro ao carregar UFs:', error);
      // Fallback para teste - carregar UFs fixas
      const ufsFixas = [
        {uf: 'SP', total: 22873914}, {uf: 'MG', total: 8622911}, 
        {uf: 'RJ', total: 6729190}, {uf: 'RS', total: 5470547},
        {uf: 'PR', total: 5379569}, {uf: 'BA', total: 3948780},
        {uf: 'SC', total: 3797700}, {uf: 'GO', total: 2832955},
        {uf: 'PE', total: 2374609}, {uf: 'CE', total: 2244514}
      ];
      setUfs(ufsFixas);
      console.log('Usando UFs fixas:', ufsFixas.length);
    }
  };

  const carregarMunicipios = async (uf) => {
    try {
      const url = uf 
        ? `${API_URL}/filtros/municipios?uf=${uf}`
        : `${API_URL}/filtros/municipios`;
      const response = await fetch(url);
      const data = await response.json();
      setMunicipios(data.municipios || []);
    } catch (error) {
      console.error('Erro ao carregar municípios:', error);
    }
  };

  const buscarMunicipioPorNome = async (busca) => {
    if (busca.length < 3) {
      setMunicipios([]);
      return;
    }
    try {
      const response = await fetch(`${API_URL}/filtros/municipios?busca=${encodeURIComponent(busca)}`);
      const data = await response.json();
      setMunicipios(data.municipios || []);
    } catch (error) {
      console.error('Erro ao buscar municípios:', error);
    }
  };

  const handleUfChange = (uf) => {
    setUfSelecionada(uf);
    setMunicipioSelecionado('');
    if (uf) {
      carregarMunicipios(uf);
    } else {
      setMunicipios([]);
    }
  };

  const handleBuscar = async () => {
    setBuscando(true);
    setDados([]);

    try {
      const response = await fetch(`${API_URL}/query/filtrado`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          uf: ufSelecionada || null,
          municipio: municipioSelecionado || null,
          situacao: situacaoSelecionada || null,
          limit: limiteSelecionado
        })
      });

      const data = await response.json();
      
      if (data.dados) {
        setDados(data.dados);
        setTotalEncontrado(data.total_encontrado);
      }
    } catch (error) {
      console.error('Erro na busca:', error);
    } finally {
      setBuscando(false);
    }
  };

  const limparFiltros = () => {
    setUfSelecionada('');
    setMunicipioSelecionado('');
    setSituacaoSelecionada('02');
    setLimiteSelecionado(50);
    setMunicipios([]);
    setDados([]);
    setTotalEncontrado(0);
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">Carregando...</div>;
  }

  return (
    <main className="min-h-screen p-4 sm:p-8 bg-gray-900 text-white">
      <div className="w-full max-w-7xl mx-auto">
        {/* Header */}
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">🔍 Busca Avançada (Filtros)</h1>
            <p className="text-gray-400">Busque sem usar IA - Rápido e gratuito!</p>
          </div>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 font-semibold text-white bg-gray-700 rounded-md hover:bg-gray-600"
          >
            ← Dashboard
          </button>
        </header>

        {/* Informação */}
        <div className="mb-6 p-4 bg-blue-900 border border-blue-700 rounded-md">
          <p className="text-sm text-blue-200">
            💡 <strong>Dica:</strong> Use os filtros abaixo para buscar diretamente no banco (79M registros). 
            Queries simples são instantâneas e não gastam créditos de IA!
          </p>
        </div>

        {/* Filtros */}
        <div className="bg-gray-800 rounded-lg p-6 mb-6 border border-gray-700">
          <h2 className="text-xl font-bold mb-4">📊 Filtros</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* UF */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Estado (UF) {ufs.length > 0 && <span className="text-xs text-green-400">({ufs.length} estados)</span>}
              </label>
              <select
                value={ufSelecionada}
                onChange={(e) => handleUfChange(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Todos os estados</option>
                {ufs.length === 0 && <option disabled>Carregando estados...</option>}
                {ufs.map((uf) => (
                  <option key={uf.uf} value={uf.uf}>
                    {uf.uf} ({uf.total.toLocaleString()} empresas)
                  </option>
                ))}
              </select>
              {ufs.length === 0 && (
                <button
                  onClick={carregarUFs}
                  className="mt-2 text-xs text-indigo-400 hover:text-indigo-300 underline"
                >
                  🔄 Recarregar estados
                </button>
              )}
            </div>

            {/* Município */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Município (Código IBGE) {ufSelecionada && <span className="text-xs text-gray-500">- {ufSelecionada}</span>}
              </label>
              <select
                value={municipioSelecionado}
                onChange={(e) => setMunicipioSelecionado(e.target.value)}
                disabled={!ufSelecionada}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="">
                  {ufSelecionada ? 'Todos os municípios' : 'Selecione um estado primeiro'}
                </option>
                {municipios.map((m) => (
                  <option key={m.codigo} value={m.codigo}>
                    {m.codigo} - {m.total.toLocaleString()} empresas
                  </option>
                ))}
              </select>
              {ufSelecionada && municipios.length > 0 && (
                <p className="text-xs text-gray-400 mt-1">
                  📊 Top {municipios.length} municípios de {ufSelecionada} (ordenados por quantidade)
                </p>
              )}
              {!ufSelecionada && (
                <p className="text-xs text-gray-400 mt-1">
                  ℹ️ Selecione um estado para ver os municípios
                </p>
              )}
            </div>

            {/* Situação */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Situação Cadastral
              </label>
              <select
                value={situacaoSelecionada}
                onChange={(e) => setSituacaoSelecionada(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Todas</option>
                <option value="02">✅ Ativa (02)</option>
                <option value="01">⚪ Nula (01)</option>
                <option value="03">⏸️ Suspensa (03)</option>
                <option value="04">❌ Inapta (04)</option>
                <option value="08">🔻 Baixada (08)</option>
              </select>
            </div>

            {/* Limite */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Resultados
              </label>
              <select
                value={limiteSelecionado}
                onChange={(e) => setLimiteSelecionado(parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="10">10 resultados</option>
                <option value="50">50 resultados</option>
                <option value="100">100 resultados</option>
                <option value="500">500 resultados</option>
                <option value="1000">1000 resultados (máx)</option>
              </select>
            </div>
          </div>

          {/* Botões */}
          <div className="flex gap-3 mt-6">
            <button
              onClick={handleBuscar}
              disabled={buscando}
              className="flex-1 px-6 py-3 font-bold text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:bg-gray-500 disabled:cursor-not-allowed"
            >
              {buscando ? '🔍 Buscando...' : '🔍 Buscar'}
            </button>
            <button
              onClick={limparFiltros}
              className="px-6 py-3 font-semibold text-white bg-gray-700 rounded-md hover:bg-gray-600"
            >
              🔄 Limpar
            </button>
            <button
              onClick={() => router.push('/chat-llm')}
              className="px-6 py-3 font-semibold text-white bg-purple-600 rounded-md hover:bg-purple-700"
            >
              🤖 Usar IA (LLM)
            </button>
          </div>
        </div>

        {/* Resumo da Busca */}
        {totalEncontrado > 0 && (
          <div className="mb-4 p-4 bg-green-900 border border-green-700 rounded-md">
            <p className="text-green-200">
              ✅ Encontrados <strong>{totalEncontrado.toLocaleString()}</strong> estabelecimentos. 
              Mostrando os primeiros <strong>{dados.length}</strong>.
              {totalEncontrado > dados.length && (
                <span className="ml-2 text-sm">
                  (Aumente o limite para ver mais)
                </span>
              )}
            </p>
          </div>
        )}

        {/* Tabela de Resultados */}
        <DataTable data={dados} loading={buscando} />

        {/* Dica de Economia */}
        {dados.length > 0 && (
          <div className="mt-6 p-4 bg-yellow-900 border border-yellow-700 rounded-md">
            <p className="text-sm text-yellow-200">
              💰 <strong>Economia:</strong> Esta busca foi executada diretamente no banco (grátis). 
              O Chat LLM é útil para queries complexas, mas os filtros são mais rápidos e econômicos para buscas simples!
            </p>
          </div>
        )}
      </div>
    </main>
  );
}

