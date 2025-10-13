# ===============================================================
# SCRIPT CORRIGIDO DE PREPARAÇÃO - PC XEON (DESTINO)
# ===============================================================

# --- PASSO 1: LIMPEZA COMPLETA ---
docker stop cnpj_postgres_final
docker rm cnpj_postgres_final
docker volume rm cnpj_postgres_data_final

# --- PASSO 2: CONFIRMAÇÃO DO IP ---
# O IP desta máquina é 192.168.15.22.
ipconfig

# --- PASSO 3: INICIE O CONTAINER COM O BANCO DE DADOS CORRETO ---
# A flag "-e POSTGRES_DB=cnpj_processed" foi adicionada.
# Isto irá criar um container com o banco de dados "cnpj_processed" vazio, pronto para receber os dados.
docker run --name cnpj_postgres_final -e POSTGRES_PASSWORD=password -e POSTGRES_DB=cnpj_processed -p 5432:5432 -d postgres:15

# --- PASSO 4: VERIFIQUE O FIREWALL ---
# Garanta que a regra para a porta 5432 ainda está ativa.

# --- AGORA, VÁ PARA O THINKPAD T14 E EXECUTE O SCRIPT DE LÁ. ---

# --- PASSO 5: VERIFICAÇÃO FINAL (CHECKSUM) ---
# Rode este comando APÓS a transferência do T14 ter sido concluída.
docker exec -it cnpj_postgres_final psql -U postgres -d cnpj_processed -c "SELECT COUNT(*) FROM estabelecimentos;"