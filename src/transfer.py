import time
from pathlib import Path
from typing import Dict

import pyodbc

from core.constants import (
    PASS_DW,
    PASS_PROD,
    QUERYS_FOLDER_PATH,
    SERVER_DW_14,
    SERVER_PROD,
    TRANSFER_SETTINGS_JSON_PATH,
    USER_DW,
    USER_PROD,
)
from core.functions import close_connection, get_connection
from src.core.utils import execution_time, logger, terminal_line
from src.exporter import load_configuration, sql_to_dict


def fetch_queries_from_dw(
    query_dict: Dict[str, str], source_conn: pyodbc.Connection
) -> Dict[str, Dict[str, list]]:
    results = {}
    cursor = source_conn.cursor()
    for query_name, query in query_dict.items():
        try:
            logger.info(f"Executando query '{query_name}' no banco DW...")
            cursor.execute(query)
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            results[query_name] = {"data": data, "columns": columns}
            logger.info(f"Query '{query_name}' executada com sucesso no DW.")
        except pyodbc.Error as e:
            logger.error(f"Erro ao executar a query '{query_name}': {e}")
        except Exception as e:
            logger.error(f"Erro inesperado ao executar a query '{query_name}': {e}")
    cursor.close()
    return results


def insert_data_into_prod(
    results: Dict[str, Dict[str, list]], target_conn: pyodbc.Connection
) -> None:
    cursor = target_conn.cursor()
    for query_name, result in results.items():
        try:
            logger.info(f"Inserindo dados da query '{query_name}' no banco PROD...")
            columns = ", ".join(result["columns"])
            placeholders = ", ".join("?" for _ in result["columns"])
            insert_query = (
                f"INSERT INTO {query_name} ({columns}) VALUES ({placeholders})"
            )

            for row in result["data"]:
                cursor.execute(insert_query, row)

            target_conn.commit()
            logger.info(
                f"Dados da query '{query_name}' importados com sucesso no PROD."
            )
        except pyodbc.Error as e:
            logger.error(f"Erro ao inserir dados da query '{query_name}': {e}")
            target_conn.rollback()
        except Exception as e:
            logger.error(
                f"Erro inesperado ao inserir dados da query '{query_name}': {e}"
            )
            target_conn.rollback()
    cursor.close()


def process_import_dw_to_prod(config: Dict[str, str]) -> None:
    """
    Conecta ao DW (origem) e PROD (destino) e realiza o fluxo de importação.
    """
    key_name = config["key_name"]

    # Conexões
    logger.info("Conectando ao banco DW (origem)...")
    cursor_source, conn_source = get_connection(
        server_name=SERVER_DW_14, username=USER_DW, password=PASS_DW
    )

    logger.info("Conectando ao banco PROD (destino)...")
    cursor_target, conn_target = get_connection(
        server_name=SERVER_PROD, username=USER_PROD, password=PASS_PROD
    )

    try:
        # Carregar as queries do arquivo SQL
        query_dict = sql_to_dict(
            sql_file=str(QUERYS_FOLDER_PATH / Path(f"{key_name}.sql"))
        )

        # Executar queries no DW e buscar os dados
        results = fetch_queries_from_dw(query_dict=query_dict, source_conn=conn_source)

        # Inserir dados no PROD
        insert_data_into_prod(results=results, target_conn=conn_target)

    finally:
        close_connection(cursor=cursor_source, conn=conn_source)
        close_connection(cursor=cursor_target, conn=conn_target)


def main() -> None:
    while True:
        terminal_line()

        # Carregar configuração para o banco de origem e destino
        required_keys = ["key_name"]
        config = load_configuration(
            "default_import_dw_to_prod", TRANSFER_SETTINGS_JSON_PATH, required_keys
        )

        if not config:
            logger.error("Falha ao carregar a configuração.")
            return

        try:
            start_time = time.time()
            process_import_dw_to_prod(config)
            execution_time(start_time)
            logger.info("Importação DW para PROD finalizada com sucesso.")
        except Exception as e:
            logger.error(f"Erro durante o processo de importação: {e}")

        if input("Deseja continuar importando? (s/n): ").lower() != "s":
            break


if __name__ == "__main__":
    try:
        logger.info("Iniciando script de importação DW -> PROD.")
        main()
    except KeyboardInterrupt:
        logger.info("Script interrompido pelo usuário.")
    except Exception as e:
        logger.error(f"Erro durante execução do script: {e}")
