# py-sql-importer-exporter

> [!IMPORTANT]
> Este projeto está em construção. Algumas funcionalidades, documentações ou instruções podem estar incompletas ou sujeitas a alterações conforme o desenvolvimento avança.

Este projeto tem como objetivo simplificar a importação e exportação de múltiplos arquivos de um banco de dados SQL Server. Ele utiliza arquivos `.sql` para armazenar querys, que são interpretados e processados em dicionários a partir de delimitadores específicos.

## Funcionalidades

- **Importação de Dados:**
  - Carrega arquivos `.csv` para tabelas no SQL Server.
  - Ajusta automaticamente os tipos de dados e comprimentos das colunas.
  - Criação opcional de scripts SQL com base nos arquivos importados.

- **Exportação de Dados:**
  - Executa querys SQL armazenadas em arquivos `.sql`.
  - Salva os resultados em arquivos `.csv` organizados por cliente.
  - Suporte para diferentes codificações, delimitadores e opções de formatação.

- **Sorter:**
  - Permite a ordenação dos dados exportados com base em critérios específicos.
