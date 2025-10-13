import { render, screen } from '@testing-library/react'
import DataTable from '../../components/DataTable'

describe('Componente DataTable', () => {
  it('mostra loading quando está carregando', () => {
    render(<DataTable data={[]} loading={true} />)
    expect(screen.getByText('Carregando dados...')).toBeInTheDocument()
  })

  it('mostra mensagem quando não há dados', () => {
    render(<DataTable data={[]} loading={false} />)
    expect(screen.getByText(/Nenhum dado encontrado/i)).toBeInTheDocument()
  })

  it('renderiza a tabela com dados', () => {
    const mockData = [
      { id: 1, nome: 'Teste 1', cidade: 'SP' },
      { id: 2, nome: 'Teste 2', cidade: 'RJ' },
    ]

    render(<DataTable data={mockData} loading={false} />)
    
    expect(screen.getByText('id')).toBeInTheDocument()
    expect(screen.getByText('nome')).toBeInTheDocument()
    expect(screen.getByText('cidade')).toBeInTheDocument()
    expect(screen.getByText('Teste 1')).toBeInTheDocument()
    expect(screen.getByText('Teste 2')).toBeInTheDocument()
  })

  it('renderiza todos os cabeçalhos corretamente', () => {
    const mockData = [
      { cnpj: '12345', empresa: 'ABC', uf: 'SP' },
    ]

    render(<DataTable data={mockData} loading={false} />)
    
    expect(screen.getByText('cnpj')).toBeInTheDocument()
    expect(screen.getByText('empresa')).toBeInTheDocument()
    expect(screen.getByText('uf')).toBeInTheDocument()
  })
})

