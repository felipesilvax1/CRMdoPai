// ═══════════════════════════════════════════════════════════════
// API Route: Exemplo de Uso do S3 / LocalStack
// ═══════════════════════════════════════════════════════════════
// Demonstra como usar o S3 (LocalStack em dev, AWS em produção)
// Acesso: POST /api/s3-example
// ═══════════════════════════════════════════════════════════════

import type { NextApiRequest, NextApiResponse } from 'next';
import { 
  PutObjectCommand, 
  ListObjectsV2Command, 
  GetObjectCommand,
  DeleteObjectCommand 
} from '@aws-sdk/client-s3';
import { s3Client, AWS_BUCKETS, getS3ObjectUrl, isUsingLocalStack } from '../../lib/awsClient';

type S3Response = {
  success: boolean;
  message: string;
  data?: any;
  error?: string;
  localStack?: boolean;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<S3Response>
) {
  const { method, query } = req;
  const action = query.action as string;

  try {
    // ═══════════════════════════════════════════════════════════════
    // Upload de arquivo
    // ═══════════════════════════════════════════════════════════════
    if (method === 'POST' && action === 'upload') {
      const { fileName, content, bucket = AWS_BUCKETS.REPORTS } = req.body;

      if (!fileName || !content) {
        return res.status(400).json({
          success: false,
          message: 'fileName e content são obrigatórios',
        });
      }

      const command = new PutObjectCommand({
        Bucket: bucket,
        Key: fileName,
        Body: content,
        ContentType: 'text/plain',
      });

      await s3Client.send(command);

      return res.status(200).json({
        success: true,
        message: 'Arquivo enviado com sucesso',
        data: {
          bucket,
          key: fileName,
          url: getS3ObjectUrl(bucket, fileName),
        },
        localStack: isUsingLocalStack(),
      });
    }

    // ═══════════════════════════════════════════════════════════════
    // Listar arquivos em um bucket
    // ═══════════════════════════════════════════════════════════════
    if (method === 'GET' && action === 'list') {
      const bucket = (query.bucket as string) || AWS_BUCKETS.REPORTS;

      const command = new ListObjectsV2Command({
        Bucket: bucket,
        MaxKeys: 100,
      });

      const response = await s3Client.send(command);

      return res.status(200).json({
        success: true,
        message: 'Arquivos listados com sucesso',
        data: {
          bucket,
          count: response.KeyCount || 0,
          files: response.Contents?.map(obj => ({
            key: obj.Key,
            size: obj.Size,
            lastModified: obj.LastModified,
            url: getS3ObjectUrl(bucket, obj.Key || ''),
          })) || [],
        },
        localStack: isUsingLocalStack(),
      });
    }

    // ═══════════════════════════════════════════════════════════════
    // Deletar arquivo
    // ═══════════════════════════════════════════════════════════════
    if (method === 'DELETE' && action === 'delete') {
      const { fileName, bucket = AWS_BUCKETS.REPORTS } = req.body;

      if (!fileName) {
        return res.status(400).json({
          success: false,
          message: 'fileName é obrigatório',
        });
      }

      const command = new DeleteObjectCommand({
        Bucket: bucket,
        Key: fileName,
      });

      await s3Client.send(command);

      return res.status(200).json({
        success: true,
        message: 'Arquivo deletado com sucesso',
        data: { bucket, key: fileName },
        localStack: isUsingLocalStack(),
      });
    }

    // ═══════════════════════════════════════════════════════════════
    // Teste de conectividade
    // ═══════════════════════════════════════════════════════════════
    if (method === 'GET' && action === 'test') {
      const command = new ListObjectsV2Command({
        Bucket: AWS_BUCKETS.REPORTS,
        MaxKeys: 1,
      });

      await s3Client.send(command);

      return res.status(200).json({
        success: true,
        message: 'Conexão com S3/LocalStack estabelecida',
        data: {
          environment: process.env.NODE_ENV,
          localStack: isUsingLocalStack(),
          buckets: AWS_BUCKETS,
        },
        localStack: isUsingLocalStack(),
      });
    }

    // Ação não reconhecida
    return res.status(400).json({
      success: false,
      message: 'Ação não reconhecida. Use: upload, list, delete ou test',
    });

  } catch (error) {
    console.error('Erro na operação S3:', error);
    return res.status(500).json({
      success: false,
      message: 'Erro ao executar operação S3',
      error: error instanceof Error ? error.message : 'Unknown error',
      localStack: isUsingLocalStack(),
    });
  }
}

