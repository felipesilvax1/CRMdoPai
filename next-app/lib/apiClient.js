/**
 * Cliente para comunicação com a API local (PostgreSQL)
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

/**
 * Verifica o status da API
 */
export async function checkApiHealth() {
  try {
    const response = await fetch(`${API_URL}/health`);
    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Executa uma consulta no banco de dados PostgreSQL
 * @param {string} question - Pergunta em linguagem natural ou SQL direto
 * @returns {Promise} - Retorna os resultados da consulta
 */
export async function queryDatabase(question) {
  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Obtém estatísticas gerais do banco de dados
 */
export async function getStatistics() {
  return queryDatabase('estatisticas gerais');
}

/**
 * Busca empresas
 * @param {number} limit - Número máximo de resultados
 */
export async function getEmpresas(limit = 20) {
  return queryDatabase(`empresas razao social`);
}

/**
 * Executa uma consulta SQL customizada (use com cuidado!)
 * @param {string} sql - Query SQL
 */
export async function executeCustomSQL(sql) {
  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        question: sql,
        // Flag para indicar que é SQL direto (se a API suportar no futuro)
        directSQL: true 
      }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

