'use client';

import { useState } from 'react';

// A importação de 'jspdf' e 'jspdf-autotable' será feita de forma dinâmica
// para otimizar o carregamento e resolver possíveis problemas de compilação.

// Define a estrutura dos dados que esperamos receber da API
interface ApiResponse {
  resposta_texto?: string;
  sql_gerado?: string;
  total_resultados?: number;
  dados_completos?: any[];
  erro?: string;
}

type Status = 'idle' | 'loading' | 'success' | 'error';

// --- Componente para a Tabela de Pré-visualização ---
const PreviewTable = ({ data, onExportCSV, onExportPDF }: { data: any[], onExportCSV: () => void, onExportPDF: () => void }) => {
  if (!data || data.length === 0) return null;

  const headers = Object.keys(data[0]);

  return (
    <div className="mt-6 border border-gray-700 rounded-lg p-4 bg-gray-900">
        <h3 className="font-bold text-lg mb-4 text-gray-300">Pré-visualização dos Dados</h3>
        <div className="flex gap-4 mb-4">
            <button onClick={onExportCSV} className="px-4 py-2 bg-green-600 rounded-lg text-sm font-semibold hover:bg-green-700 transition">
                Exportar para CSV
            </button>
            <button onClick={onExportPDF} className="px-4 py-2 bg-red-600 rounded-lg text-sm font-semibold hover:bg-red-700 transition">
                Exportar para PDF
            </button>
        </div>
      <div className="overflow-x-auto max-h-96">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-700 sticky top-0">
            <tr>
              {headers.map(header => <th key={header} className="p-3">{header}</th>)}
            </tr>
          </thead>
          <tbody className="bg-gray-800">
            {data.map((row, rowIndex) => (
              <tr key={rowIndex} className="border-b border-gray-700 hover:bg-gray-700/50">
                {headers.map(header => <td key={`${rowIndex}-${header}`} className="p-3">{row[header]}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};


export default function Home() {
  const [pergunta, setPergunta] = useState<string>('');
  const [resposta, setResposta] = useState<ApiResponse | null>(null);
  const [status, setStatus] = useState<Status>('idle');
  const [showPreview, setShowPreview] = useState<boolean>(false);

  const getStatusMessage = () => {
    switch (status) {
      case 'loading': return 'Aguardando resposta do servidor de IA...';
      case 'error': return 'Tentar Novamente';
      default: return 'Perguntar';
    }
  };

  const handleExportCSV = () => {
    if (!resposta?.dados_completos || resposta.dados_completos.length === 0) return;
    const data = resposta.dados_completos;
    const headers = Object.keys(data[0]);
    const csvRows = [
      headers.join(','), // header row
      ...data.map(row => headers.map(header => JSON.stringify(row[header])).join(','))
    ];
    
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'export_dados.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportPDF = async () => {
    if (!resposta?.dados_completos || resposta.dados_completos.length === 0) return;

    // Carregamento dinâmico das bibliotecas de PDF
    const { default: jsPDF } = await import('jspdf');
    await import('jspdf-autotable');

    const data = resposta.dados_completos;
    const doc = new jsPDF({ orientation: 'landscape' });
    
    doc.autoTable({
      head: [Object.keys(data[0])],
      body: data.map(row => Object.values(row).map(val => String(val))), // Garante que todos os valores são strings
      startY: 20,
      theme: 'grid',
      styles: {
        fontSize: 8,
      },
      headStyles: {
        fillColor: [22, 163, 74]
      }
    });

    doc.text("Relatório de Consulta", 14, 15);
    doc.save('export_dados.pdf');
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!pergunta.trim() || status === 'loading') return;

    setStatus('loading');
    setResposta(null);
    setShowPreview(false);

    try {
      console.log('Passo 1: Enviando pergunta para a API Flask...');
      const res = await fetch('http://localhost:5000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: pergunta }),
      });
      
      console.log('Passo 2: Recebendo resposta da API...');
      if (!res.ok) {
        throw new Error(`Erro na API: ${res.statusText}`);
      }

      const data: ApiResponse = await res.json();
      console.log('Passo 3: Resposta recebida e processada.', data);
      
      setResposta(data);
      setStatus(data.erro ? 'error' : 'success');

    } catch (error) {
      console.error('Falha ao conectar com o servidor da API:', error);
      setResposta({ erro: 'Não foi possível conectar ao servidor da API. Verifique se ele está rodando.' });
      setStatus('error');
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-8 bg-gray-900 text-white font-sans">
      <div className="w-full max-w-4xl">
        <h1 className="text-4xl font-bold text-center mb-2">Converse com seus Dados</h1>
        <p className="text-center text-gray-400 mb-8">Faça uma pergunta em português para consultar seu banco de dados SQLite local.</p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="text"
            value={pergunta}
            onChange={(e) => setPergunta(e.target.value)}
            placeholder="Ex: Quais empresas de Barueri têm CNAE de logística?"
            className="w-full p-4 rounded-lg bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            disabled={status === 'loading'}
          />
          <button
            type="submit"
            className="w-full p-4 bg-blue-600 rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-gray-600 disabled:cursor-not-allowed"
            disabled={status === 'loading'}
          >
            {getStatusMessage()}
          </button>
        </form>

        {status === 'loading' && <p className="text-center text-gray-400 mt-4 animate-pulse">Comunicando com a IA...</p>}

        {resposta && (
          <div className="mt-8 p-6 rounded-lg bg-gray-800 border border-gray-700 animate-fade-in">
            {resposta.erro ? (
              <div className="text-red-400">
                <h2 className="font-bold text-lg mb-2">Ocorreu um Erro</h2>
                <p>{resposta.erro}</p>
              </div>
            ) : (
              <div>
                <h2 className="font-bold text-xl mb-4">Resposta</h2>
                <p className="mb-6 text-gray-300">{resposta.resposta_texto}</p>

                <div className="bg-gray-900 p-4 rounded-md">
                  <h3 className="font-semibold mb-2 text-gray-400">Detalhes da Execução</h3>
                  <p className="text-sm text-gray-500">
                    <span className="font-mono bg-gray-700 px-2 py-1 rounded-md">{resposta.total_resultados}</span> resultados encontrados.
                  </p>
                  <details className="mt-3 text-sm">
                    <summary className="cursor-pointer text-blue-400">Ver SQL Gerado</summary>
                    <pre className="text-xs bg-black p-3 rounded-md mt-2 overflow-x-auto">
                      <code>{resposta.sql_gerado}</code>
                    </pre>
                  </details>
                </div>
                
                {resposta.total_resultados && resposta.total_resultados > 0 && (
                    <div className="mt-6">
                        <button onClick={() => setShowPreview(!showPreview)} className="w-full p-3 bg-indigo-600 rounded-lg font-semibold hover:bg-indigo-700 transition">
                            {showPreview ? 'Ocultar' : 'Pré-visualizar'} Dados Completos
                        </button>
                        {showPreview && resposta.dados_completos && <PreviewTable data={resposta.dados_completos} onExportCSV={handleExportCSV} onExportPDF={handleExportPDF} />}
                    </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}

