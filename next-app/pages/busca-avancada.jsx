import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useRouter } from 'next/router';
import { supabase } from '../lib/supabaseClient';
import DataTable from '../components/DataTable';

const DEV_MODE = process.env.NEXT_PUBLIC_DEV_MODE === 'true';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Cache simples para evitar chamadas duplicadas
const cache = {
  ufs: null,
  cnaes: null,
  municipios: {},
  bairros: {}
};

export default function BuscaAvancada() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [buscando, setBuscando] = useState(false);
  const router = useRouter();

  // Estados dos filtros
  const [filtros, setFiltros] = useState({
    // Localização
    uf: '',
    municipio: '',
    bairro: '',
    cep: '',
    
    // Empresa
    razaoSocial: '',
    nomeFantasia: '',
    cnpj: '',
    situacao: '02', // Ativa por padrão
    matrizFilial: '', // 1=Matriz, 2=Filial
    
    // Econômico
    cnae: '',
    naturezaJuridica: '',
    porteEmpresa: '',
    capitalSocialMin: '',
    capitalSocialMax: '',
    
    // Temporal
    dataAberturaInicio: '',
    dataAberturaFim: '',
    
    // Outros
    mei: '', // S/N
    ddd: '',
    opcaoSimples: '', // 1=Sim, 2=Não
    
    // Paginação
    limit: 100,
    offset: 0
  });

  // Opções para dropdowns
  const [opcoes, setOpcoes] = useState({
    ufs: [],
    municipios: [],
    bairros: [],
    cnaes: [],
    naturezas: [],
    portes: []
  });

  // Resultados
  const [dados, setDados] = useState([]);
  const [totalEncontrado, setTotalEncontrado] = useState(0);
  const [filtrosAtivos, setFiltrosAtivos] = useState(0);

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

      await carregarOpcoes();
      setLoading(false);
    };

    checkSession();
  }, [router]);

  // Carregar opções para dropdowns (COM CACHE)
  const carregarOpcoes = useCallback(async () => {
    try {
      // UFs (usar cache se disponível)
      if (cache.ufs) {
        console.log('📦 UFs carregadas do cache');
        setOpcoes(prev => ({ ...prev, ufs: cache.ufs }));
      } else {
        const ufsResponse = await fetch(`${API_URL}/filtros/ufs`);
        const ufsData = await ufsResponse.json();
        if (ufsData.ufs && ufsData.ufs.length > 0) {
          cache.ufs = ufsData.ufs; // Salvar no cache
          setOpcoes(prev => ({ ...prev, ufs: ufsData.ufs }));
          console.log('✅ UFs carregadas da API');
        }
      }

      // CNAEs principais (usar cache se disponível)
      if (cache.cnaes) {
        console.log('📦 CNAEs carregadas do cache');
        setOpcoes(prev => ({ ...prev, cnaes: cache.cnaes }));
      } else {
        const cnaesResponse = await fetch(`${API_URL}/filtros/cnaes?limit=100`);
        const cnaesData = await cnaesResponse.json();
        if (cnaesData.cnaes) {
          cache.cnaes = cnaesData.cnaes; // Salvar no cache
          setOpcoes(prev => ({ ...prev, cnaes: cnaesData.cnaes }));
          console.log('✅ CNAEs carregadas da API');
        }
      }

    } catch (error) {
      console.error('Erro ao carregar filtros:', error);
    }
  }, []);

  // Carregar municípios quando UF mudar (COM CACHE + DEBOUNCE)
  const isLoadingMunicipios = useRef(false);
  
  useEffect(() => {
    if (filtros.uf) {
      // Verificar cache primeiro
      const cacheKey = filtros.uf;
      if (cache.municipios[cacheKey]) {
        console.log(`📦 Municípios de ${filtros.uf} carregados do cache`);
        setOpcoes(prev => ({ ...prev, municipios: cache.municipios[cacheKey], bairros: [] }));
        setFiltros(prev => ({ ...prev, municipio: '', bairro: '' }));
        return;
      }

      // Evitar múltiplas chamadas simultâneas
      if (isLoadingMunicipios.current) {
        console.log('⏳ Já está carregando municípios, aguarde...');
        return;
      }

      isLoadingMunicipios.current = true;
      const startTime = performance.now();
      
      fetch(`${API_URL}/filtros/municipios?uf=${filtros.uf}&limit=50`)
        .then(res => res.json())
        .then(data => {
          const elapsed = performance.now() - startTime;
          console.log(`⏱️ Municípios de ${filtros.uf} carregados em ${elapsed.toFixed(0)}ms (${data.municipios?.length || 0} resultados)`);
          
          if (data.municipios) {
            cache.municipios[cacheKey] = data.municipios; // Salvar no cache
            setOpcoes(prev => ({ ...prev, municipios: data.municipios, bairros: [] }));
          }
          
          if (data.tempo_ms) {
            console.log(`📊 Tempo no servidor: ${data.tempo_ms}ms`);
          }
        })
        .catch(console.error)
        .finally(() => {
          isLoadingMunicipios.current = false;
        });
      
      // Limpar município e bairro quando UF mudar
      setFiltros(prev => ({ ...prev, municipio: '', bairro: '' }));
    } else {
      setOpcoes(prev => ({ ...prev, municipios: [], bairros: [] }));
      setFiltros(prev => ({ ...prev, municipio: '', bairro: '' }));
    }
  }, [filtros.uf]);

  // Carregar bairros quando município mudar (COM CACHE)
  const isLoadingBairros = useRef(false);
  
  useEffect(() => {
    if (filtros.municipio && filtros.uf) {
      // Verificar cache primeiro
      const cacheKey = `${filtros.uf}-${filtros.municipio}`;
      if (cache.bairros[cacheKey]) {
        console.log(`📦 Bairros de ${filtros.municipio} carregados do cache`);
        setOpcoes(prev => ({ ...prev, bairros: cache.bairros[cacheKey] }));
        setFiltros(prev => ({ ...prev, bairro: '' }));
        return;
      }

      // Evitar múltiplas chamadas simultâneas
      if (isLoadingBairros.current) {
        console.log('⏳ Já está carregando bairros, aguarde...');
        return;
      }

      isLoadingBairros.current = true;
      const startTime = performance.now();
      
      fetch(`${API_URL}/filtros/bairros?uf=${filtros.uf}&municipio=${filtros.municipio}`)
        .then(res => res.json())
        .then(data => {
          const elapsed = performance.now() - startTime;
          console.log(`⏱️ Bairros carregados em ${elapsed.toFixed(0)}ms (${data.bairros?.length || 0} resultados)`);
          
          if (data.bairros) {
            cache.bairros[cacheKey] = data.bairros; // Salvar no cache
            setOpcoes(prev => ({ ...prev, bairros: data.bairros }));
          }
        })
        .catch(console.error)
        .finally(() => {
          isLoadingBairros.current = false;
        });
      
      // Limpar bairro quando município mudar
      setFiltros(prev => ({ ...prev, bairro: '' }));
    } else {
      setOpcoes(prev => ({ ...prev, bairros: [] }));
      setFiltros(prev => ({ ...prev, bairro: '' }));
    }
  }, [filtros.municipio, filtros.uf]);

  // Atualizar filtro
  const updateFiltro = (campo, valor) => {
    setFiltros(prev => ({ ...prev, [campo]: valor }));
  };

  // Contar filtros ativos
  useEffect(() => {
    const ativos = Object.entries(filtros).filter(([key, value]) => {
      if (key === 'limit' || key === 'offset' || key === 'situacao') return false;
      return value !== '' && value !== null && value !== undefined;
    }).length;
    setFiltrosAtivos(ativos);
  }, [filtros]);

  // Buscar
  const handleBuscar = async () => {
    setBuscando(true);
    setDados([]);

    try {
      // Montar query params
      const params = new URLSearchParams();
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
          params.append(key, value);
        }
      });

      const response = await fetch(`${API_URL}/query/avancada?${params.toString()}`);
      const data = await response.json();
      
      if (data.dados) {
        setDados(data.dados);
        setTotalEncontrado(data.total || data.dados.length);
      }
    } catch (error) {
      console.error('Erro na busca:', error);
      alert('Erro ao realizar busca. Verifique se a API está rodando.');
    } finally {
      setBuscando(false);
    }
  };

  // Limpar filtros
  const limparFiltros = () => {
    setFiltros({
      uf: '',
      municipio: '',
      bairro: '',
      cep: '',
      razaoSocial: '',
      nomeFantasia: '',
      cnpj: '',
      situacao: '02',
      matrizFilial: '',
      cnae: '',
      naturezaJuridica: '',
      porteEmpresa: '',
      capitalSocialMin: '',
      capitalSocialMax: '',
      dataAberturaInicio: '',
      dataAberturaFim: '',
      mei: '',
      ddd: '',
      opcaoSimples: '',
      limit: 100,
      offset: 0
    });
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
        <header className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold">🔍 Busca Avançada</h1>
            <p className="text-gray-400">Filtros abrangentes para buscas precisas</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => router.push('/admin-console')}
              className="px-4 py-2 font-semibold text-white bg-purple-600 rounded-md hover:bg-purple-700"
            >
              🎛️ Admin
            </button>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 font-semibold text-white bg-gray-700 rounded-md hover:bg-gray-600"
            >
              ← Dashboard
            </button>
          </div>
        </header>

        {/* Info Box */}
        <div className="mb-6 p-4 bg-blue-900 border border-blue-700 rounded-md">
          <p className="text-sm text-blue-200">
            💡 <strong>Dica:</strong> Combine múltiplos filtros para buscas precisas. Deixe em branco os que não quiser usar.
            {filtrosAtivos > 0 && <span className="ml-2 font-bold">{filtrosAtivos} filtros ativos</span>}
          </p>
        </div>

        {/* Filtros */}
        <div className="bg-gray-800 rounded-lg p-6 mb-6 border border-gray-700">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            📊 Filtros Avançados
            {filtrosAtivos > 0 && (
              <span className="text-sm bg-blue-600 px-3 py-1 rounded-full">{filtrosAtivos}</span>
            )}
          </h2>
          
          {/* Seção: Localização */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3 text-blue-400">📍 Localização</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Estado (UF)</label>
                <select
                  value={filtros.uf}
                  onChange={(e) => updateFiltro('uf', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                >
                  <option value="">Todos</option>
                  {opcoes.ufs && opcoes.ufs.length > 0 ? (
                    opcoes.ufs.map((uf) => (
                      <option key={uf.uf} value={uf.uf}>
                        {uf.uf} ({uf.total?.toLocaleString() || 0} empresas)
                      </option>
                    ))
                  ) : (
                    <option disabled>🔄 Carregando...</option>
                  )}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Município {opcoes.municipios.length > 0 && <span className="text-xs text-gray-500">({opcoes.municipios.length})</span>}
                </label>
                <select
                  value={filtros.municipio}
                  onChange={(e) => updateFiltro('municipio', e.target.value)}
                  disabled={!filtros.uf}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200 disabled:opacity-50"
                >
                  <option value="">Todos</option>
                  {filtros.uf && opcoes.municipios.length === 0 && (
                    <option disabled>🔄 Carregando...</option>
                  )}
                  {opcoes.municipios.map((m) => (
                    <option key={m.codigo} value={m.codigo}>
                      {m.codigo} ({m.total?.toLocaleString() || 0} empresas)
                    </option>
                  ))}
                </select>
                {!filtros.uf && (
                  <p className="text-xs text-gray-500 mt-1">↑ Selecione um estado primeiro</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Bairro {opcoes.bairros.length > 0 && <span className="text-xs text-gray-500">({opcoes.bairros.length})</span>}
                </label>
                <select
                  value={filtros.bairro}
                  onChange={(e) => updateFiltro('bairro', e.target.value)}
                  disabled={!filtros.municipio}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200 disabled:opacity-50"
                >
                  <option value="">Todos</option>
                  {filtros.municipio && opcoes.bairros.length === 0 && (
                    <option disabled>🔄 Carregando...</option>
                  )}
                  {opcoes.bairros.map((b, idx) => (
                    <option key={idx} value={b.bairro}>
                      {b.bairro} ({b.total?.toLocaleString() || 0} empresas)
                    </option>
                  ))}
                </select>
                {!filtros.municipio && (
                  <p className="text-xs text-gray-500 mt-1">↑ Selecione um município primeiro</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">CEP</label>
                <input
                  type="text"
                  value={filtros.cep}
                  onChange={(e) => updateFiltro('cep', e.target.value)}
                  placeholder="00000000"
                  maxLength="8"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                />
              </div>
            </div>
          </div>

          {/* Seção: Identificação */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3 text-green-400">🏢 Identificação da Empresa</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Razão Social</label>
                <input
                  type="text"
                  value={filtros.razaoSocial}
                  onChange={(e) => updateFiltro('razaoSocial', e.target.value)}
                  placeholder="Nome da empresa"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Nome Fantasia</label>
                <input
                  type="text"
                  value={filtros.nomeFantasia}
                  onChange={(e) => updateFiltro('nomeFantasia', e.target.value)}
                  placeholder="Nome fantasia"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">CNPJ</label>
                <input
                  type="text"
                  value={filtros.cnpj}
                  onChange={(e) => updateFiltro('cnpj', e.target.value)}
                  placeholder="00000000000000"
                  maxLength="14"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Situação Cadastral</label>
                <select
                  value={filtros.situacao}
                  onChange={(e) => updateFiltro('situacao', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                >
                  <option value="">Todas</option>
                  <option value="02">✅ Ativa</option>
                  <option value="01">⚪ Nula</option>
                  <option value="03">⏸️ Suspensa</option>
                  <option value="04">❌ Inapta</option>
                  <option value="08">🔻 Baixada</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Matriz/Filial</label>
                <select
                  value={filtros.matrizFilial}
                  onChange={(e) => updateFiltro('matrizFilial', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                >
                  <option value="">Ambos</option>
                  <option value="1">🏢 Matriz</option>
                  <option value="2">🏪 Filial</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">MEI</label>
                <select
                  value={filtros.mei}
                  onChange={(e) => updateFiltro('mei', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                >
                  <option value="">Todos</option>
                  <option value="S">Sim</option>
                  <option value="N">Não</option>
                </select>
              </div>
            </div>
          </div>

          {/* Seção: Econômico */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3 text-yellow-400">💼 Dados Econômicos</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">CNAE (Atividade)</label>
                <input
                  type="text"
                  value={filtros.cnae}
                  onChange={(e) => updateFiltro('cnae', e.target.value)}
                  placeholder="Código CNAE (ex: 4711)"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Natureza Jurídica</label>
                <input
                  type="text"
                  value={filtros.naturezaJuridica}
                  onChange={(e) => updateFiltro('naturezaJuridica', e.target.value)}
                  placeholder="Código"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Porte</label>
                <select
                  value={filtros.porteEmpresa}
                  onChange={(e) => updateFiltro('porteEmpresa', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                >
                  <option value="">Todos</option>
                  <option value="01">Micro Empresa</option>
                  <option value="03">Pequeno Porte</option>
                  <option value="05">Demais</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Capital Social Mínimo (R$)</label>
                <input
                  type="number"
                  value={filtros.capitalSocialMin}
                  onChange={(e) => updateFiltro('capitalSocialMin', e.target.value)}
                  placeholder="0.00"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Capital Social Máximo (R$)</label>
                <input
                  type="number"
                  value={filtros.capitalSocialMax}
                  onChange={(e) => updateFiltro('capitalSocialMax', e.target.value)}
                  placeholder="999999999.99"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Simples Nacional</label>
                <select
                  value={filtros.opcaoSimples}
                  onChange={(e) => updateFiltro('opcaoSimples', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                >
                  <option value="">Todos</option>
                  <option value="1">Sim</option>
                  <option value="2">Não</option>
                </select>
              </div>
            </div>
          </div>

          {/* Seção: Temporal */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3 text-purple-400">📅 Período</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Data Abertura (Início)</label>
                <input
                  type="date"
                  value={filtros.dataAberturaInicio}
                  onChange={(e) => updateFiltro('dataAberturaInicio', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Data Abertura (Fim)</label>
                <input
                  type="date"
                  value={filtros.dataAberturaFim}
                  onChange={(e) => updateFiltro('dataAberturaFim', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">DDD</label>
                <input
                  type="text"
                  value={filtros.ddd}
                  onChange={(e) => updateFiltro('ddd', e.target.value)}
                  placeholder="11"
                  maxLength="3"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                />
              </div>
            </div>
          </div>

          {/* Seção: Resultados */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3 text-red-400">⚙️ Configurações de Busca</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Limite de Resultados</label>
                <select
                  value={filtros.limit}
                  onChange={(e) => updateFiltro('limit', parseInt(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-200"
                >
                  <option value="10">10 resultados</option>
                  <option value="50">50 resultados</option>
                  <option value="100">100 resultados</option>
                  <option value="500">500 resultados</option>
                  <option value="1000">1000 resultados</option>
                  <option value="5000">5000 resultados</option>
                </select>
              </div>
            </div>
          </div>

          {/* Botões */}
          <div className="flex gap-3 mt-6">
            <button
              onClick={handleBuscar}
              disabled={buscando}
              className="flex-1 px-6 py-3 font-bold text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:bg-gray-500 disabled:cursor-not-allowed transition-colors"
            >
              {buscando ? '🔍 Buscando...' : `🔍 Buscar${filtrosAtivos > 0 ? ` (${filtrosAtivos} filtros)` : ''}`}
            </button>
            <button
              onClick={limparFiltros}
              className="px-6 py-3 font-semibold text-white bg-gray-700 rounded-md hover:bg-gray-600 transition-colors"
            >
              🔄 Limpar Tudo
            </button>
            <button
              onClick={() => router.push('/chat-llm')}
              className="px-6 py-3 font-semibold text-white bg-purple-600 rounded-md hover:bg-purple-700 transition-colors"
            >
              🤖 Usar IA
            </button>
          </div>
        </div>

        {/* Resumo da Busca */}
        {totalEncontrado > 0 && (
          <div className="mb-4 p-4 bg-green-900 border border-green-700 rounded-md">
            <p className="text-green-200">
              ✅ Encontrados <strong>{totalEncontrado.toLocaleString()}</strong> estabelecimentos. 
              Mostrando <strong>{dados.length}</strong> resultados.
              {filtrosAtivos > 0 && (
                <span className="ml-2">
                  ({filtrosAtivos} filtros aplicados)
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
              Use a IA (Chat LLM) apenas para queries complexas que exijam linguagem natural!
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
