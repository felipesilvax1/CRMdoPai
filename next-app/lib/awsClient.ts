// ═══════════════════════════════════════════════════════════════
// Cliente AWS SDK - Integração com LocalStack
// ═══════════════════════════════════════════════════════════════
// Configuração do SDK da AWS para trabalhar com LocalStack
// ═══════════════════════════════════════════════════════════════

import { S3Client } from '@aws-sdk/client-s3';

// ═══════════════════════════════════════════════════════════════
// Configuração do Ambiente
// ═══════════════════════════════════════════════════════════════

const IS_LOCAL = process.env.NODE_ENV === 'development';
const LOCALSTACK_ENDPOINT = process.env.LOCALSTACK_ENDPOINT || 'http://localstack:4566';

// ═══════════════════════════════════════════════════════════════
// Cliente S3
// ═══════════════════════════════════════════════════════════════

/**
 * Cliente S3 configurado para LocalStack (desenvolvimento) ou AWS (produção)
 */
export const s3Client = new S3Client({
  region: process.env.AWS_REGION || 'us-east-1',
  
  // Configurações para LocalStack (desenvolvimento)
  ...(IS_LOCAL && {
    endpoint: LOCALSTACK_ENDPOINT,
    forcePathStyle: true, // Necessário para LocalStack
    credentials: {
      accessKeyId: 'test',
      secretAccessKey: 'test',
    },
  }),
  
  // Em produção, usar credenciais reais do ambiente
  ...(!IS_LOCAL && {
    credentials: {
      accessKeyId: process.env.AWS_ACCESS_KEY_ID || '',
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || '',
    },
  }),
});

// ═══════════════════════════════════════════════════════════════
// Configurações dos Buckets
// ═══════════════════════════════════════════════════════════════

export const AWS_BUCKETS = {
  REPORTS: 'cnae-reports-bucket',
  BACKUPS: 'crm-backups-bucket',
  EXPORTS: 'crm-exports-bucket',
} as const;

// ═══════════════════════════════════════════════════════════════
// Funções Auxiliares
// ═══════════════════════════════════════════════════════════════

/**
 * Retorna a URL completa de um objeto no S3
 */
export function getS3ObjectUrl(bucket: string, key: string): string {
  if (IS_LOCAL) {
    return `${LOCALSTACK_ENDPOINT}/${bucket}/${key}`;
  }
  return `https://${bucket}.s3.amazonaws.com/${key}`;
}

/**
 * Verifica se estamos usando LocalStack
 */
export function isUsingLocalStack(): boolean {
  return IS_LOCAL;
}

