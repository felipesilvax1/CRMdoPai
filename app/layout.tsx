import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CRM - Converse com seus Dados',
  description: 'Interface de consulta ao banco de dados com IA',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  )
}

