import csv
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Union

import pandas as pd
import pyodbc

from core.constants import (
    EXPORT_FOLDER_PATH,
    EXPORT_SETTINGS_JSON_PATH,
    PASS_DW,
    QUERYS_FOLDER_PATH,
    USER_DW,
)
from core.functions import (
    close_connection,
    get_available_keys,
    get_connection,
    get_selected_key,
    load_configuration,
    should_continue,
    validate_constants,
)
from src.core.utils import execution_time, logger, start_config, terminal_line


@dataclass
class ExportConfig:
    output_path: Union[str, Path]
    client_name: str
    encoding: str = "utf-8"
    quotechar: str = '"'
    delimiter: str = ","
    contains_data: bool = False


def sql_to_dict(sql_file: Union[str, Path], classifier: str = "--") -> Dict[str, str]:
    """
    Lê um arquivo SQL e o converte em um dicionário onde a chave é um nome
    (extraído das linhas iniciadas pelo classificador) e o valor é a query SQL.

    Args:
        sql_file (Union[str, Path]): Caminho para o arquivo SQL.
        classifier (str): Identificador que separa as consultas no arquivo SQL.

    Returns:
        Dict[str, str]: Dicionário com os nomes das queries como chaves e as consultas como valores.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
        ValueError: Se o arquivo não contiver consultas válidas.
    """
    if not Path(sql_file).is_file():
        raise FileNotFoundError(f"Arquivo SQL não encontrado: {sql_file}")

    query_list: Dict[str, str] = {}
    file_name, consulta = None, ""

    try:
        # Lê o arquivo SQL linha por linha
        with open(sql_file, "r", encoding="utf-8") as file:
            for linha in file:
                linha = linha.strip()

                # Verifica se a linha começa com o classificador
                if classifier and linha.startswith(classifier):
                    # Salva a consulta anterior no dicionário
                    if file_name:
                        query_list[file_name] = consulta.rstrip()
                    # Inicia uma nova consulta
                    file_name, consulta = linha.lstrip(classifier).strip(), ""
                else:
                    # Concatena a linha na consulta atual
                    consulta += linha.strip() + " "

            # Salva a última consulta, se existir
            if file_name:
                query_list[file_name] = consulta.rstrip()

    except RuntimeError as e:
        logger.error(f"Erro ao processar o arquivo SQL '{sql_file}': {e}")
        raise

    # Verifica se o dicionário contém consultas válidas
    if not query_list:
        raise ValueError(f"O arquivo SQL '{sql_file}' não contém consultas válidas.")

    return query_list


def export_dict_to_csv(
    conn: pyodbc.Connection,
    query_dict: Dict[str, str],
    export_config: ExportConfig,
) -> None:
    """
    Exporta consultas SQL (dicionário) para arquivos CSV.

    Args:
        conn (pyodbc.Connection): Conexão com o banco de dados.
        query_dict (Dict[str, str]): Dicionário contendo os nomes das queries e suas consultas SQL.
        export_config (ExportConfig): Configuração da exportação.

    Raises:
        ValueError: Se o dicionário de queries estiver vazio.
        RuntimeError: Para erros ao acessar sistema de arquivos ou executar queries.
    """
    if not query_dict:
        raise ValueError("O dicionário de queries está vazio.")

    # Criação do diretório de exportação para o cliente
    client_folder: Path = Path(export_config.output_path) / export_config.client_name

    try:
        client_folder.mkdir(parents=True, exist_ok=True)
    except RuntimeError as e:
        logger.error(f"Erro ao criar a pasta do cliente '{client_folder}': {e}")
        raise

    for key, value in query_dict.items():
        try:
            # Executa a query e carrega o resultado em um DataFrame
            df_queries = pd.read_sql(value, conn)  # type: ignore
        except RuntimeError as e:
            logger.error(f"Erro ao executar a query '{key}': {e}")
            raise

        # Define o nome do arquivo com base na configuração
        file_name = (
            f"{datetime.now().strftime('%Y%m%d')}_{key}.csv"
            if export_config.contains_data
            else f"{key}.csv"
        )
        output_file = client_folder / file_name

        try:
            # Remove o arquivo existente (se houver)
            if output_file.exists():
                output_file.unlink()

            # Configura os parâmetros de exportação CSV
            quote_params = {}
            if export_config.quotechar:
                quote_params["quotechar"] = export_config.quotechar
                quote_params["quoting"] = csv.QUOTE_ALL

            # Salva o DataFrame no arquivo CSV
            df_queries.to_csv(
                output_file,
                encoding=export_config.encoding,
                index=False,
                sep=export_config.delimiter,
                **quote_params,
            )
            logger.info(f'O arquivo "{Path(output_file).stem}" foi criado com sucesso.')
        except RuntimeError as e:
            logger.error(f"Erro ao salvar o arquivo CSV '{output_file}': {e}")
            raise


def process_export(config: Dict[str, str]) -> None:
    """
    Processa a exportação de dados para arquivos CSV com base em uma configuração.

    Args:
        config (Dict[str, str]): Dicionário contendo as configurações da exportação.

    Raises:
        RuntimeError: Para erros de configuração ou execução de exportação.
    """
    try:
        # Valida e extrai informações da configuração
        key_name = config.get("key_name")
        server_name = config.get("server_name")

        if not key_name or not server_name:
            raise ValueError(
                "Configuração inválida: 'key_name' ou 'server_name' está ausente."
            )

        # Cria o objeto ExportConfig
        export_config = ExportConfig(
            output_path=str(
                EXPORT_FOLDER_PATH / f'{datetime.now().strftime("%Y%m%d")}'
            ),
            client_name=key_name,
            encoding=config["encoding"],
            quotechar=config["quotechar"],
            delimiter=config["delimiter"],
            contains_data=bool(config["contains_data"]),
        )

        # Estabelece a conexão com o banco de dados
        cursor, conn = get_connection(
            server_name=server_name, username=USER_DW, password=PASS_DW
        )
    except RuntimeError as e:
        logger.error(f"Erro ao configurar a exportação: {e}")
        raise

    try:
        # Carrega as consultas SQL do arquivo
        query_dict = sql_to_dict(
            sql_file=str(QUERYS_FOLDER_PATH / Path(f"{key_name}.sql"))
        )

        # Exporta as consultas para arquivos CSV
        export_dict_to_csv(
            conn=conn, query_dict=query_dict, export_config=export_config
        )
    except RuntimeError as e:
        logger.error(f"Erro durante o processamento da exportação: {e}")
        raise
    finally:
        # Fecha a conexão com o banco de dados
        close_connection(cursor=cursor, conn=conn)


def main() -> None:
    """
    Loop principal do script para processar exportações com base nas configurações disponíveis.
    """
    while True:
        try:
            # Configura o terminal e desabilita warnings do Pandas
            start_config()

            # Obtém as chaves disponíveis para exportação
            available_keys = get_available_keys(EXPORT_SETTINGS_JSON_PATH)
            selected_key_name = get_selected_key(available_keys)

            start_time = time.time()
            terminal_line()

            # Valida constantes e caminhos necessários
            validate_constants(
                paths=[EXPORT_SETTINGS_JSON_PATH, EXPORT_FOLDER_PATH],
                values=[USER_DW, PASS_DW, selected_key_name],
            )

            # Define as chaves obrigatórias na configuração
            required_keys = [
                "key_name",
                "encoding",
                "quotechar",
                "delimiter",
                "contains_data",
                "server_name",
            ]

            # Carrega a configuração baseada na chave selecionada
            config = load_configuration(
                selected_key_name, EXPORT_SETTINGS_JSON_PATH, required_keys
            )
            if not config:
                logger.warning(
                    f"Configuração ausente para a chave '{selected_key_name}'."
                )
                continue

            # Processa a exportação com a configuração carregada
            process_export(config)

            # Exibe o tempo de execução
            execution_time(start_time)

            # Pergunta ao usuário se deve continuar
            if not should_continue("exportação"):
                break
        except RuntimeError as e:
            logger.error(f"Erro no loop principal: {e}")
            raise


if __name__ == "__main__":
    try:
        main()
        logger.info("Script finalizado com sucesso.")
    except KeyboardInterrupt:
        logger.info("Script interrompido pelo usuário.")
    except RuntimeError as e:
        logger.error(f"Ocorreu um erro inesperado durante a execução do script: {e}")
