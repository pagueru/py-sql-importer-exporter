# py-sql-importer-exporter

> [!IMPORTANT]
> Este arquivo README.md está em construção. Algumas informações podem estar incompletas ou imprecisas no momento, e serão atualizadas conforme o projeto evolui.

Este projeto tem como objetivo principal facilitar a importação e exportação de múltiplos arquivos de um banco de dados SQL Server. Ele utiliza arquivos `.sql` para armazenar queries, que são interpretados e processados em dicionários a partir de delimitadores específicos (`--`).

## Funcionalidades

- **Importação de Dados:**
  - Carrega arquivos `.csv` para tabelas no SQL Server.
  - Ajusta automaticamente os tipos de dados e comprimentos das colunas.
  - Criação opcional de scripts SQL com base nos arquivos importados.

- **Exportação de Dados:**
  - Executa queries SQL armazenadas em arquivos `.sql`.
  - Salva os resultados em arquivos `.csv` organizados por cliente.
  - Suporte para diferentes codificações, delimitadores e opções de formatação.

## Estrutura do Projeto

## Pré-requisitos

- **Python** 3.8 ou superior
- Dependências listadas no arquivo `requirements.txt`
- SQL Server e permissões adequadas para conexão.

### Configuração

1. Clone este repositório.
2. Configure as credenciais no arquivo `credentials.env` dentro da pasta `config/`.
3. Instale as dependências com:

```bash
pip install -r requirements.txt
```

Certifique-se de que os diretórios e arquivos necessários (como templates SQL) estejam configurados conforme esperado.

## Uso

### Importação de Dados

1. Insira os arquivos .csv na pasta data/import/.
2. Execute o script importer.py:

```bash
python importer.py
```

3. Siga as instruções no terminal para importar os dados e, opcionalmente, gerar scripts SQL.

### Exportação de Dados

1. Crie ou edite os arquivos .sql na pasta data/sql/.
2. Execute o script exporter.py:

```bash
python exporter.py
```

3. Siga as instruções no terminal para exportar os dados.

## Personalização

# Delimitadores em Queries SQL

As queries nos arquivos .sql são separadas pelo delimitador padrão --. Caso necessário, o delimitador pode ser alterado diretamente na função sql_to_dict no arquivo exporter.py.

# Configurações de Exportação

As configurações de exportação, como codificação, delimitador e formato de cotações, são gerenciadas por meio do arquivo export_config.json na pasta config/.
