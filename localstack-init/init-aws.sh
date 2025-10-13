#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LocalStack Initialization Script
# ═══════════════════════════════════════════════════════════════
# Este script é executado quando o LocalStack está pronto
# ═══════════════════════════════════════════════════════════════

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Initializing LocalStack AWS resources"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Aguarda LocalStack estar completamente pronto
sleep 5

# Instala o awslocal se não estiver presente
if ! command -v awslocal &> /dev/null; then
    echo "📦 Installing awscli-local..."
    pip install awscli-local
fi

# ═══════════════════════════════════════════════════════════════
# S3 - Simple Storage Service
# ═══════════════════════════════════════════════════════════════

echo ""
echo "🪣 Creating S3 buckets..."

# Bucket para relatórios CNAE
awslocal s3api create-bucket \
    --bucket cnae-reports-bucket \
    --region us-east-1 \
    2>/dev/null || echo "  ℹ️  Bucket cnae-reports-bucket já existe"

# Bucket para backups
awslocal s3api create-bucket \
    --bucket crm-backups-bucket \
    --region us-east-1 \
    2>/dev/null || echo "  ℹ️  Bucket crm-backups-bucket já existe"

# Bucket para exports de dados
awslocal s3api create-bucket \
    --bucket crm-exports-bucket \
    --region us-east-1 \
    2>/dev/null || echo "  ℹ️  Bucket crm-exports-bucket já existe"

# Lista buckets criados
echo ""
echo "📋 Buckets disponíveis:"
awslocal s3api list-buckets --query "Buckets[].Name" --output table

# ═══════════════════════════════════════════════════════════════
# SQS - Simple Queue Service
# ═══════════════════════════════════════════════════════════════

echo ""
echo "📬 Creating SQS queues..."

# Fila para processamento de relatórios
awslocal sqs create-queue \
    --queue-name report-processing-queue \
    2>/dev/null || echo "  ℹ️  Queue report-processing-queue já existe"

# Fila para notificações
awslocal sqs create-queue \
    --queue-name notifications-queue \
    2>/dev/null || echo "  ℹ️  Queue notifications-queue já existe"

# Fila DLQ (Dead Letter Queue)
awslocal sqs create-queue \
    --queue-name report-dlq \
    2>/dev/null || echo "  ℹ️  Queue report-dlq já existe"

# Lista filas criadas
echo ""
echo "📋 Filas disponíveis:"
awslocal sqs list-queues --output table

# ═══════════════════════════════════════════════════════════════
# SNS - Simple Notification Service
# ═══════════════════════════════════════════════════════════════

echo ""
echo "📢 Creating SNS topics..."

# Tópico para alertas
awslocal sns create-topic \
    --name crm-alerts \
    2>/dev/null || echo "  ℹ️  Topic crm-alerts já existe"

# Tópico para notificações de sistema
awslocal sns create-topic \
    --name system-notifications \
    2>/dev/null || echo "  ℹ️  Topic system-notifications já existe"

# Lista tópicos criados
echo ""
echo "📋 Tópicos disponíveis:"
awslocal sns list-topics --output table

# ═══════════════════════════════════════════════════════════════
# DynamoDB - NoSQL Database
# ═══════════════════════════════════════════════════════════════

echo ""
echo "🗄️  Creating DynamoDB tables..."

# Tabela para cache de consultas
awslocal dynamodb create-table \
    --table-name query-cache \
    --attribute-definitions \
        AttributeName=queryId,AttributeType=S \
    --key-schema \
        AttributeName=queryId,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    2>/dev/null || echo "  ℹ️  Table query-cache já existe"

# Tabela para sessões de usuário
awslocal dynamodb create-table \
    --table-name user-sessions \
    --attribute-definitions \
        AttributeName=sessionId,AttributeType=S \
    --key-schema \
        AttributeName=sessionId,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    2>/dev/null || echo "  ℹ️  Table user-sessions já existe"

# Lista tabelas criadas
echo ""
echo "📋 Tabelas disponíveis:"
awslocal dynamodb list-tables --output table

# ═══════════════════════════════════════════════════════════════
# Upload de arquivo de teste no S3
# ═══════════════════════════════════════════════════════════════

echo ""
echo "📤 Uploading test file..."

# Cria arquivo de teste
echo "LocalStack Test File - CRM System" > /tmp/test-file.txt
echo "Created at: $(date)" >> /tmp/test-file.txt

# Faz upload
awslocal s3 cp /tmp/test-file.txt s3://cnae-reports-bucket/test/test-file.txt \
    2>/dev/null && echo "  ✅ Test file uploaded successfully"

# ═══════════════════════════════════════════════════════════════
# Finalização
# ═══════════════════════════════════════════════════════════════

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ LocalStack initialization complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 Access LocalStack at: http://localhost:4566"
echo ""
echo "📚 Example commands:"
echo "  awslocal s3 ls"
echo "  awslocal sqs list-queues"
echo "  awslocal dynamodb list-tables"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

