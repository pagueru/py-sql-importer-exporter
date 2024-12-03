import csv
import json
from pathlib import Path
import time
from typing import Union, Dict
from datetime import datetime

import pyodbc
from pandas import read_sql

from core.constants import (
    EXPORT_FOLDER_PATH,
    EXPORT_SETTINGS_JSON_PATH,
    QUERYS_FOLDER_PATH,
    USERNAME,
    PASSWORD,
)
from core.logger import logger
from core.functions import (
    start_config,
    terminal_line,
    get_connection,
    close_connection,
    validate_constants,
    should_continue,
    load_configuration,
    execution_time,
    get_available_keys,
    get_selected_key,
)
from core.decorators import handle_exceptions


@handle_exceptions()
def open_json_file(json_file_path: Union[str, Path]) -> Union[dict, None]:
    with open(json_file_path, "r") as json_file:
        data: dict = json.load(json_file)
        logger.debug(f"Arquivo JSON {json_file_path} lido com sucesso.")
        return data


@handle_exceptions()
def sql_to_dict(sql_file: Union[str, Path], classifier: str = "--") -> dict:
    query_list: dict = {}
    file_name, consulta = None, ""
    sql_file = str(sql_file)
    with open(sql_file, "r", encoding="utf-8") as file:
        for linha in file:
            linha = linha.strip()
            if classifier and linha.startswith(classifier):
                if file_name:
                    query_list[file_name] = consulta.rstrip()
                file_name, consulta = linha.lstrip(classifier).strip(), ""
            else:
                consulta += linha.strip() + " "
        if file_name:
            query_list[file_name] = consulta.rstrip()
    return query_list


@handle_exceptions()
def export_dict_to_csv(
    conn: pyodbc.Connection,
    query_dict: dict,
    output_path: Union[str, Path],
    client_name: str,
    encoding: str,
    quotechar: str,
    delimiter: str,
    contains_data: bool = False,
) -> None:
    if not query_dict:
        raise ValueError("O dicionário de queries está vazio.")

    # Criando a subpasta com o nome do cliente
    client_folder: Path = Path(output_path) / client_name
    client_folder.mkdir(parents=True, exist_ok=True)

    for key, value in query_dict.items():
        df = read_sql(value, conn)

        file_name = (
            f"{datetime.now().strftime('%Y%m%d')}_{key}.csv"
            if contains_data
            else f"{key}.csv"
        )
        output_file = client_folder / file_name

        # Verifica e remove o arquivo se já existir
        if output_file.exists():
            output_file.unlink()

        quote_params = {}
        if quotechar:
            quote_params["quotechar"] = quotechar
            quote_params["quoting"] = csv.QUOTE_ALL

        df.to_csv(
            output_file, encoding=encoding, index=False, sep=delimiter, **quote_params
        )
        logger.info(f'O arquivo "{Path(output_file).stem}" foi criado com sucesso.')


@handle_exceptions()
def process_export(config: Dict[str, str], selected_key: str) -> None:
    key_name = config["key_name"]
    encoding = config["encoding"]
    quotechar = config["quotechar"]
    delimiter = config["delimiter"]
    contains_data = bool(config["contains_data"])
    server_name = config["server_name"]

    cursor, conn = get_connection(
        server_name=server_name, username=USERNAME, password=PASSWORD
    )

    try:
        query_dict = sql_to_dict(
            sql_file=str(QUERYS_FOLDER_PATH / Path(f"{key_name}.sql"))
        )

        export_dict_to_csv(
            conn=conn,
            query_dict=query_dict,
            output_path=str(
                EXPORT_FOLDER_PATH / f'{datetime.now().strftime("%Y%m%d")}'
            ),
            client_name=key_name,
            encoding=encoding,
            quotechar=quotechar,
            delimiter=delimiter,
            contains_data=contains_data,
        )
    finally:
        close_connection(cursor=cursor, conn=conn)


def main() -> None:
    while True:
        available_keys = get_available_keys(EXPORT_SETTINGS_JSON_PATH)
        selected_key_name = get_selected_key(available_keys)

        start_time = time.time()
        terminal_line()

        validate_constants(
            paths=[EXPORT_SETTINGS_JSON_PATH, EXPORT_FOLDER_PATH],
            values=[USERNAME, PASSWORD, selected_key_name],
        )

        required_keys = [
            "key_name",
            "encoding",
            "quotechar",
            "delimiter",
            "contains_data",
            "server_name",
        ]

        config = load_configuration(
            selected_key_name, EXPORT_SETTINGS_JSON_PATH, required_keys
        )
        if not config:
            continue

        process_export(config, selected_key_name)

        execution_time(start_time)

        if not should_continue("exportação"):
            break


if __name__ == "__main__":
    try:
        start_config()
        main()
        logger.info("Script finalizado com sucesso.")
    except KeyboardInterrupt:
        logger.info("Script interrompido pelo usuário.")
    except Exception as e:
        logger.error(f"Ocorreu um erro durante a execução do script: {e}")
