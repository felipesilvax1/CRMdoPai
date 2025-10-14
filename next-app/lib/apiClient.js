/**
 * Cliente API - Gerenciador de conexão com backend
 * Lida com erros de conexão e fallback gracioso
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
const LLM_URL = process.env.NEXT_PUBLIC_LLM_URL || 'http://localhost:8000';

/**
 * Verificar se API está acessível
 */
export async function checkAPIHealth() {
  try {
    const response = await fetch(`${API_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(3000) // 3s timeout
    });
    return response.ok;
  } catch (error) {
    console.warn('API não está acessível:', error.message);
    return false;
  }
}

/**
 * Verificar se LLM está acessível
 */
export async function checkLLMHealth() {
  try {
    const response = await fetch(`${LLM_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(3000)
    });
    return response.ok;
  } catch (error) {
    console.warn('LLM não está acessível:', error.message);
    return false;
  }
}

/**
 * Fazer requisição à API com tratamento de erros
 */
export async function apiRequest(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Erro na requisição para ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Fazer requisição ao LLM com tratamento de erros
 */
export async function llmRequest(endpoint, options = {}) {
  const url = `${LLM_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Erro na requisição LLM para ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Status de saúde do sistema
 */
export async function getSystemHealth() {
  const [apiOk, llmOk] = await Promise.all([
    checkAPIHealth(),
    checkLLMHealth()
  ]);

  return {
    api: apiOk,
    llm: llmOk,
    overall: apiOk && llmOk
  };
}

/**
 * Legacy function - Check API health (formato antigo compatível)
 * Retorna objeto com success e data para compatibilidade
 */
export async function checkApiHealth() {
  try {
    const response = await fetch(`${API_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(3000)
    });
    
    if (response.ok) {
      const data = await response.json();
      return {
        success: true,
        data: data
      };
    }
    
    return { success: false };
  } catch (error) {
    console.warn('API não está acessível:', error.message);
    return { success: false };
  }
}

/**
 * Legacy function - Get empresas (formato antigo compatível)
 */
export async function getEmpresas(limit = 50) {
  try {
    const response = await fetch(`${API_URL}/query/completo?limit=${limit}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });

    if (response.ok) {
      const data = await response.json();
      return {
        success: true,
        data: data
      };
    }

    return { success: false };
  } catch (error) {
    console.error('Erro ao buscar empresas:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Legacy function - Query database
 */
export async function queryDatabase(query) {
  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });

    if (response.ok) {
      const data = await response.json();
      return {
        success: true,
        data: data
      };
    }

    return { success: false };
  } catch (error) {
    console.error('Erro ao executar query:', error);
    return { success: false, error: error.message };
  }
}

// Aliases para compatibilidade
export const checkLlmHealth = checkLLMHealth;

export { API_URL, LLM_URL };
