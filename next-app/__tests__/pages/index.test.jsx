import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import LoginPage from '../../pages/index'

describe('Página de Login', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  it('renderiza o formulário de login em modo dev', () => {
    render(<LoginPage />)
    
    expect(screen.getByText('🚀 Modo Desenvolvimento')).toBeInTheDocument()
    expect(screen.getByText('Entrar no Dashboard (Sem Login)')).toBeInTheDocument()
  })

  it('salva usuário dev no localStorage ao clicar no botão', () => {
    render(<LoginPage />)
    
    const button = screen.getByText('Entrar no Dashboard (Sem Login)')
    fireEvent.click(button)

    // Verifica que localStorage.setItem foi chamado
    expect(localStorage.setItem).toHaveBeenCalled()
    const calls = localStorage.setItem.mock.calls
    expect(calls[0][0]).toBe('dev_user')
  })

  it('mostra instruções sobre o modo dev', () => {
    render(<LoginPage />)
    
    expect(screen.getByText(/Você está no modo de desenvolvimento/i)).toBeInTheDocument()
    expect(screen.getByText(/NEXT_PUBLIC_DEV_MODE/i)).toBeInTheDocument()
  })
})

