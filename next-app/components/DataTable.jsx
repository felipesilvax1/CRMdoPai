export default function DataTable({ data, loading }) {
  if (loading) {
    return <div className="text-center p-8 text-gray-400">Carregando dados...</div>
  }
  if (!data || data.length === 0) {
    return <div className="text-center p-8 text-gray-500">Nenhum dado encontrado ou você não tem permissão para ver esta tabela.</div>
  }
  const headers = Object.keys(data[0]);
  return (
    <div className="overflow-x-auto rounded-lg shadow-md border border-gray-700">
      <table className="min-w-full text-sm text-left text-gray-300 bg-gray-800">
        <thead className="bg-gray-700 text-xs text-gray-200 uppercase">
          <tr>{headers.map((h) => <th key={h} scope="col" className="px-6 py-3">{h}</th>)}</tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="border-b border-gray-700 hover:bg-gray-600">
              {headers.map((h) => <td key={`${i}-${h}`} className="px-6 py-4">{String(row[h])}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

