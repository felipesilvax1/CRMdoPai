import { useState, useEffect } from 'react';
import Head from 'next/head';

export default function AdminConsole() {
  const [systemStatus, setSystemStatus] = useState({});
  const [currentView, setCurrentView] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [baseUrl, setBaseUrl] = useState('localhost'); // Estado para o hostname

  // Detectar hostname apenas no cliente (evita erro de hydration)
  useEffect(() => {
    setBaseUrl(window.location.hostname);
  }, []);

  // Serviços disponíveis (usar baseUrl do estado)
  const services = [
    {
      id: 'grafana',
      name: 'Grafana',
      description: 'Dashboards e Visualização',
      port: 3002,
      icon: '📊',
      color: 'orange',
      category: 'observability'
    },
    {
      id: 'prometheus',
      name: 'Prometheus',
      description: 'Métricas e Alertas',
      port: 9090,
      icon: '📈',
      color: 'red',
      category: 'observability'
    },
    {
      id: 'loki',
      name: 'Loki',
      description: 'Logs Centralizados',
      port: 3100,
      icon: '📝',
      color: 'yellow',
      category: 'observability'
    },
    {
      id: 'cadvisor',
      name: 'cAdvisor',
      description: 'Métricas de Containers',
      port: 8080,
      icon: '📦',
      color: 'blue',
      category: 'observability'
    },
    {
      id: 'localstack',
      name: 'LocalStack',
      description: 'AWS Simulada',
      port: 4566,
      icon: '☁️',
      color: 'yellow',
      category: 'cloud'
    },
    {
      id: 'api',
      name: 'CRM API',
      description: 'API de Dados',
      port: 5000,
      icon: '🔌',
      color: 'green',
      category: 'backend'
    },
    {
      id: 'llm',
      name: 'LLM Service',
      description: 'Serviço de IA',
      port: 8000,
      icon: '🤖',
      color: 'purple',
      category: 'backend'
    },
    {
      id: 'frontend',
      name: 'Frontend CRM',
      description: 'Aplicação Principal',
      port: 3000,
      icon: '🌐',
      color: 'indigo',
      category: 'frontend'
    }
  ];

  // Verificar status dos serviços
  useEffect(() => {
    // Só verificar status após ter o baseUrl correto
    if (baseUrl === 'localhost' && typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
      return; // Aguardar o baseUrl ser atualizado
    }

    const checkServices = async () => {
      const status = {};
      
      for (const service of services) {
        const serviceUrl = `http://${baseUrl}:${service.port}`;
        try {
          // Tentar /health primeiro
          const response = await fetch(`${serviceUrl}/health`, { 
            method: 'GET',
            signal: AbortSignal.timeout(3000)
          });
          status[service.id] = response.ok ? 'online' : 'offline';
        } catch (error) {
          // Alguns serviços não têm /health, marcar como disponível por padrão
          status[service.id] = 'available';
        }
      }
      
      setSystemStatus(status);
      setLoading(false);
    };

    checkServices();
    const interval = setInterval(checkServices, 30000); // Atualizar a cada 30s
    
    return () => clearInterval(interval);
  }, [baseUrl]);

  // Categorias
  const categories = {
    observability: { name: 'Observabilidade', icon: '👁️', color: 'blue' },
    backend: { name: 'Backend', icon: '⚙️', color: 'green' },
    cloud: { name: 'Cloud', icon: '☁️', color: 'yellow' },
    frontend: { name: 'Frontend', icon: '🎨', color: 'purple' }
  };

  const getStatusColor = (status) => {
    if (status === 'online') return 'green';
    if (status === 'offline') return 'red';
    if (status === 'available') return 'blue';
    return 'gray';
  };

  const getStatusText = (status) => {
    if (status === 'online') return '🟢 Online';
    if (status === 'offline') return '🔴 Offline';
    if (status === 'available') return '🔵 Disponível';
    return '⚪ Verificando...';
  };

  return (
    <>
      <Head>
        <title>Admin Console - CRM</title>
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
        {/* Header */}
        <header className="bg-gray-800 border-b border-gray-700 shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="text-3xl">🎛️</div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                    Admin Console
                  </h1>
                  <p className="text-sm text-gray-400">Central de Controle do CRM</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-400">
                  Acessando de: <span className="text-blue-400 font-mono">{baseUrl}</span>
                </div>
                <div className="px-3 py-1 bg-green-900 border border-green-700 rounded-full text-sm">
                  {Object.values(systemStatus).filter(s => s === 'online').length}/{services.length} Online
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Quick Actions */}
          <div className="mb-8 grid grid-cols-1 md:grid-cols-4 gap-4">
            <button
              onClick={() => {
                if (typeof window !== 'undefined') {
                  window.open(`http://${baseUrl}:3002`, '_blank');
                }
              }}
              className="p-4 bg-gradient-to-br from-orange-600 to-orange-700 rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all transform hover:scale-105 shadow-lg"
            >
              <div className="text-3xl mb-2">📊</div>
              <div className="font-bold">Grafana</div>
              <div className="text-xs text-orange-200">Dashboard Principal</div>
            </button>

            <button
              onClick={() => {
                if (typeof window !== 'undefined') {
                  window.open(`http://${baseUrl}:9090`, '_blank');
                }
              }}
              className="p-4 bg-gradient-to-br from-red-600 to-red-700 rounded-lg hover:from-red-500 hover:to-red-600 transition-all transform hover:scale-105 shadow-lg"
            >
              <div className="text-3xl mb-2">📈</div>
              <div className="font-bold">Prometheus</div>
              <div className="text-xs text-red-200">Métricas</div>
            </button>

            <button
              onClick={() => {
                if (typeof window !== 'undefined') {
                  window.open(`http://${baseUrl}:8080`, '_blank');
                }
              }}
              className="p-4 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg hover:from-blue-500 hover:to-blue-600 transition-all transform hover:scale-105 shadow-lg"
            >
              <div className="text-3xl mb-2">📦</div>
              <div className="font-bold">cAdvisor</div>
              <div className="text-xs text-blue-200">Containers</div>
            </button>

            <button
              onClick={() => {
                if (typeof window !== 'undefined') {
                  window.open(`http://${baseUrl}:4566/_localstack/health`, '_blank');
                }
              }}
              className="p-4 bg-gradient-to-br from-yellow-600 to-yellow-700 rounded-lg hover:from-yellow-500 hover:to-yellow-600 transition-all transform hover:scale-105 shadow-lg"
            >
              <div className="text-3xl mb-2">☁️</div>
              <div className="font-bold">LocalStack</div>
              <div className="text-xs text-yellow-200">AWS Local</div>
            </button>
          </div>

          {/* Services by Category */}
          {Object.entries(categories).map(([categoryId, category]) => {
            const categoryServices = services.filter(s => s.category === categoryId);
            
            return (
              <div key={categoryId} className="mb-8">
                <div className="flex items-center space-x-2 mb-4">
                  <span className="text-2xl">{category.icon}</span>
                  <h2 className="text-xl font-bold text-gray-200">{category.name}</h2>
                  <div className="flex-1 h-px bg-gray-700"></div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {categoryServices.map((service) => (
                    <div
                      key={service.id}
                      className="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition-all hover:shadow-xl"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <span className="text-3xl">{service.icon}</span>
                        <span className={`text-xs px-2 py-1 rounded-full bg-${getStatusColor(systemStatus[service.id])}-900 text-${getStatusColor(systemStatus[service.id])}-200 border border-${getStatusColor(systemStatus[service.id])}-700`}>
                          {getStatusText(systemStatus[service.id])}
                        </span>
                      </div>

                      <h3 className="text-lg font-bold mb-1">{service.name}</h3>
                      <p className="text-sm text-gray-400 mb-3">{service.description}</p>

                      <div className="flex space-x-2">
                        <button
                          onClick={() => window.open(`http://${baseUrl}:${service.port}`, '_blank')}
                          className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-semibold transition-colors"
                        >
                          Abrir
                        </button>
                        <button
                          onClick={() => {
                            const url = `http://${baseUrl}:${service.port}`;
                            navigator.clipboard.writeText(url);
                            alert('URL copiada!');
                          }}
                          className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
                          title="Copiar URL"
                        >
                          📋
                        </button>
                      </div>

                      <div className="mt-2 text-xs text-gray-500 font-mono truncate">
                        http://{baseUrl}:{service.port}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}

          {/* System Info */}
          <div className="mt-8 bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4">ℹ️ Informações do Sistema</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-gray-400 mb-1">Host</div>
                <div className="font-mono text-blue-400">{baseUrl}</div>
              </div>
              
              <div>
                <div className="text-gray-400 mb-1">Serviços Online</div>
                <div className="font-bold text-green-400">
                  {Object.values(systemStatus).filter(s => s === 'online').length} de {services.length}
                </div>
              </div>
              
              <div>
                <div className="text-gray-400 mb-1">Última Verificação</div>
                <div className="text-gray-300">
                  {loading ? 'Verificando...' : 'Atualizado agora'}
                </div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-700">
              <div className="text-gray-400 text-xs">
                💡 <strong>Dica:</strong> Adicione esta página aos favoritos para acesso rápido a todos os serviços!
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div className="mt-6 flex flex-wrap gap-3 text-sm">
            <a href="/dashboard" className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
              ← Voltar ao CRM
            </a>
            <a href="/api/metrics" target="_blank" className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
              📊 Métricas
            </a>
            <a href="/api/health" target="_blank" className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
              ❤️ Health Check
            </a>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
            >
              🔄 Atualizar Status
            </button>
          </div>
        </main>

        {/* Footer */}
        <footer className="mt-12 border-t border-gray-800 py-6 text-center text-gray-500 text-sm">
          <p>🎛️ Admin Console - CRM System</p>
          <p className="mt-1">Desenvolvido com ❤️ para gerenciar 77M+ registros</p>
        </footer>
      </div>
    </>
  );
}

