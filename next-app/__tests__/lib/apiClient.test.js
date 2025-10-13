import { checkApiHealth, queryDatabase, getEmpresas } from '../../lib/apiClient'

describe('API Client', () => {
  beforeEach(() => {
    global.fetch = jest.fn()
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  describe('checkApiHealth', () => {
    it('retorna sucesso quando API está ok', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'ok', database: 'PostgreSQL' }),
      })

      const result = await checkApiHealth()
      
      expect(result.success).toBe(true)
      expect(result.data.status).toBe('ok')
    })

    it('retorna erro quando API falha', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'))

      const result = await checkApiHealth()
      
      expect(result.success).toBe(false)
      expect(result.error).toBe('Network error')
    })
  })

  describe('queryDatabase', () => {
    it('executa query com sucesso', async () => {
      const mockResponse = {
        resposta_texto: 'Encontrei 10 resultados',
        dados_completos: [{ id: 1 }],
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await queryDatabase('empresas')
      
      expect(result.success).toBe(true)
      expect(result.data.resposta_texto).toBe('Encontrei 10 resultados')
    })

    it('retorna erro quando query falha', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Query error'))

      const result = await queryDatabase('invalid')
      
      expect(result.success).toBe(false)
      expect(result.error).toBe('Query error')
    })
  })

  describe('getEmpresas', () => {
    it('busca empresas com sucesso', async () => {
      const mockData = {
        dados_completos: [
          { cnpj: '123', nome: 'Empresa 1' },
          { cnpj: '456', nome: 'Empresa 2' },
        ],
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      })

      const result = await getEmpresas(2)
      
      expect(result.success).toBe(true)
      expect(result.data.dados_completos).toHaveLength(2)
    })
  })
})

