# parqview

Inspetor local de arquivos Parquet via navegador. Arraste um `.parquet` e visualize schema, amostra de dados e estatísticas — tudo rodando localmente via Docker.

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado e em execução

## Inicialização

### 1. Build da imagem

```bash
docker build -t parqview .
```

### 2. Execução

```bash
docker run -p 8501:8501 parqview
```

### 3. Acesso

Abra o navegador em:

```
http://localhost:8501
```

## Como usar

1. Arraste um arquivo `.parquet` para a área de upload (ou clique para selecionar)
2. A análise é exibida automaticamente em três abas:

| Aba | Conteúdo |
|-----|----------|
| **Schema** | Nome e tipo de cada coluna |
| **Amostra** | Primeiras 100 linhas do arquivo |
| **Estatísticas** | Nulos por coluna + estatísticas descritivas das colunas numéricas |

No topo da página são exibidas três métricas rápidas: total de linhas, número de colunas e uso de memória.

## Estrutura do projeto

```
parqview/
├── app.py            # Aplicação Streamlit
├── requirements.txt  # Dependências Python
├── Dockerfile        # Imagem Docker
└── .dockerignore     # Arquivos excluídos do build
```

## Dependências

| Pacote | Versão | Função |
|--------|--------|--------|
| streamlit | 1.43.2 | Interface web |
| pandas | 2.2.3 | Manipulação de dados |
| pyarrow | 19.0.1 | Leitura de Parquet |

## Notas

- O tamanho máximo de upload padrão do Streamlit é **200 MB**. Para arquivos maiores, adicione `--server.maxUploadSize=<MB>` ao `ENTRYPOINT` no `Dockerfile`.
- O arquivo processado é mantido em cache enquanto o container estiver rodando. Para limpar o cache, reinicie o container.
- Nenhum dado é enviado para fora da máquina — todo o processamento é local.
