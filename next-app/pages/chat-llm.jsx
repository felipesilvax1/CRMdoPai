import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import { supabase } from '../lib/supabaseClient';

const DEV_MODE = process.env.NEXT_PUBLIC_DEV_MODE === 'true';
const LLM_URL = process.env.NEXT_PUBLIC_LLM_URL || 'http://localhost:8000';

export default function ChatLLM() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [llmStatus, setLlmStatus] = useState(null);
  const messagesEndRef = useRef(null);
  const router = useRouter();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

      // Verificar status do LLM Service
      checkLLMStatus();
      setLoading(false);
    };

    checkSession();
  }, [router]);

  const checkLLMStatus = async () => {
    try {
      const response = await fetch(`${LLM_URL}/health`);
      const data = await response.json();
      setLlmStatus(data);
    } catch (error) {
      setLlmStatus({ status: 'error', message: error.message });
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    
    // Adicionar mensagem de "pensando"
    const thinkingMessage = {
      role: 'thinking',
      content: '🤖 Gemma está processando...',
      steps: [
        '🔄 Inicializando LangChain...',
        '🤖 Gerando SQL...',
        '🔍 Executando no PostgreSQL...',
        '💬 Formulando resposta...'
      ],
      currentStep: 0
    };
    setMessages(prev => [...prev, thinkingMessage]);
    
    setInput('');
    setSending(true);

    try {
      const response = await fetch(`${LLM_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input })
      });

      const data = await response.json();
      
      // Remover mensagem de "pensando"
      setMessages(prev => prev.filter(m => m.role !== 'thinking'));

      if (data.sucesso) {
        const assistantMessage = {
          role: 'assistant',
          content: data.resposta_texto,
          sql: data.sql_gerado,
          total_resultados: data.total_resultados,
          dados: data.dados
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const errorMessage = {
          role: 'error',
          content: `Erro: ${data.erro}`
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage = {
        role: 'error',
        content: `Erro de conexão: ${error.message}`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setSending(false);
    }
  };

  const handleExport = async (sql, formato) => {
    try {
      const response = await fetch(`${LLM_URL}/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sql, format: formato })
      });

      const data = await response.json();

      if (data.sucesso) {
        // Criar download
        const byteCharacters = atob(data.arquivo_base64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], {
          type: formato === 'csv' ? 'text/csv' : 'application/pdf'
        });

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `export_${Date.now()}.${formato}`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      alert('Erro ao exportar: ' + error.message);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">Carregando...</div>;
  }

  return (
    <main className="min-h-screen flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 font-semibold text-white bg-gray-700 rounded-md hover:bg-gray-600"
            >
              ← Dashboard
            </button>
            <div>
              <h1 className="text-2xl font-bold">🤖 Chat com LLM (Gemma)</h1>
              {llmStatus && (
                <p className="text-sm text-gray-400">
                  {llmStatus.status === 'ok' ? (
                    <span className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                      {llmStatus.ollama_connected ? 'Ollama conectado' : 'Ollama desconectado'}
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                      LLM Service offline
                    </span>
                  )}
                </p>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              <p className="text-lg mb-4">💬 Faça uma pergunta sobre seus dados em linguagem natural!</p>
              
              <div className="mb-6 p-4 bg-blue-900 border border-blue-700 rounded-md text-left max-w-2xl mx-auto">
                <p className="text-sm text-blue-200 mb-3">
                  💡 <strong>Dica:</strong> Para buscas simples, use a <strong>Busca Avançada</strong> (mais rápida e gratuita). 
                  Use o LLM para queries complexas!
                </p>
                <button
                  onClick={() => router.push('/busca-avancada')}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-md text-white font-semibold"
                >
                  🔍 Ir para Busca Avançada
                </button>
              </div>
              
              <div className="text-sm space-y-2">
                <p className="font-semibold text-white mb-3">📝 Exemplos de perguntas para o LLM:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-3xl mx-auto text-left">
                  <div className="bg-gray-800 p-3 rounded-md border border-gray-700">
                    <p className="text-green-400">✅ "Quantos estabelecimentos ativos no Brasil?"</p>
                  </div>
                  <div className="bg-gray-800 p-3 rounded-md border border-gray-700">
                    <p className="text-green-400">✅ "Empresas em Barueri SP"</p>
                    <p className="text-xs text-gray-500 mt-1">Usa JOIN automático</p>
                  </div>
                  <div className="bg-gray-800 p-3 rounded-md border border-gray-700">
                    <p className="text-green-400">✅ "CNAEs mais comuns em MG"</p>
                  </div>
                  <div className="bg-gray-800 p-3 rounded-md border border-gray-700">
                    <p className="text-green-400">✅ "Top 10 cidades com mais empresas"</p>
                  </div>
                </div>
                
                <div className="mt-4 p-3 bg-gray-800 rounded-md border border-gray-700 max-w-2xl mx-auto">
                  <p className="text-xs text-gray-400">
                    ⚠️ <strong>Primeira pergunta demora ~2 minutos</strong> (carregando Gemma). 
                    Próximas: 10-30 segundos.
                  </p>
                </div>
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-3xl rounded-lg p-4 ${
                msg.role === 'user' ? 'bg-indigo-600' :
                msg.role === 'error' ? 'bg-red-900 border border-red-700' :
                msg.role === 'thinking' ? 'bg-yellow-900 border border-yellow-700' :
                'bg-gray-800 border border-gray-700'
              }`}>
                {msg.role === 'user' && (
                  <p className="text-white">{msg.content}</p>
                )}

                {msg.role === 'thinking' && (
                  <div className="space-y-2 text-yellow-200">
                    <p className="font-semibold">{msg.content}</p>
                    <div className="space-y-1 text-sm">
                      {msg.steps.map((step, i) => (
                        <div key={i} className="flex items-center gap-2">
                          <span className="text-yellow-400">•</span>
                          <span>{step}</span>
                        </div>
                      ))}
                    </div>
                    <div className="mt-3 flex items-center gap-2 text-sm">
                      <div className="animate-spin h-4 w-4 border-2 border-yellow-400 border-t-transparent rounded-full"></div>
                      <span>Processando (pode levar 10-30 segundos)...</span>
                    </div>
                  </div>
                )}

                {msg.role === 'assistant' && (
                  <div className="space-y-3">
                    <p className="text-white">{msg.content}</p>
                    
                    {msg.sql && (
                      <details className="text-sm">
                        <summary className="cursor-pointer text-gray-400 hover:text-gray-300">
                          Ver SQL gerado
                        </summary>
                        <pre className="mt-2 p-2 bg-gray-900 rounded text-xs overflow-x-auto">
                          {msg.sql}
                        </pre>
                      </details>
                    )}

                    <div className="flex gap-2 items-center text-sm text-gray-400">
                      <span>📊 {msg.total_resultados} resultados</span>
                      {msg.dados && msg.dados.length > 0 && msg.sql && (
                        <>
                          <button
                            onClick={() => handleExport(msg.sql, 'csv')}
                            className="ml-4 px-3 py-1 bg-green-700 hover:bg-green-600 rounded text-white"
                          >
                            📥 CSV
                          </button>
                          <button
                            onClick={() => handleExport(msg.sql, 'pdf')}
                            className="px-3 py-1 bg-red-700 hover:bg-red-600 rounded text-white"
                          >
                            📥 PDF
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                )}

                {msg.role === 'error' && (
                  <p className="text-red-200">{msg.content}</p>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-gray-700 p-4 bg-gray-800">
        <div className="max-w-4xl mx-auto flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Digite sua pergunta..."
            disabled={sending || !llmStatus?.ollama_connected}
            className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-md text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={sending || !input.trim() || !llmStatus?.ollama_connected}
            className="px-6 py-3 font-bold text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:bg-gray-500 disabled:cursor-not-allowed"
          >
            {sending ? '...' : '🚀'}
          </button>
        </div>
      </div>
    </main>
  );
}

