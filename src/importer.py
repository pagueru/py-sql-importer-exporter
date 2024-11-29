import os
import pyodbc
import pandas as pd
import time
import csv
import json
import chardet
import shutil
from pathlib import Path
from typing import Union, Optional, List, Dict, Any
from datetime import datetime

from core.constants import (
    USERNAME,
    PASSWORD,
    IMPORT_FOLDER_PATH,
    TEMPLATE_FOLDER_PATH,
    IMPORT_SETTINGS_JSON_PATH,
)
from core.logger import logger
from core.functions import (
    start_config,
    get_connection,
    close_connection,
    terminal_line,
    validate_constants,
    should_continue,
    load_configuration,
    execution_time,
    get_available_keys,
    get_selected_key,
)


def load_csv_to_sqlserver(
    file_path: Union[str, Path],
    server: Optional[str],
    database: Optional[str],
    username: Optional[str],
    password: Optional[str],
    table_name: Optional[str] = None,
    batch_size: int = 1000,
) -> str:
    start_time = time.time()

    with open(file_path, "rb") as file:
        result = chardet.detect(file.read())
        encoding: str = str(result["encoding"])
        logger.info(f"Detected encoding: {encoding}")

    with open(file_path, "r", encoding=encoding) as file:
        sample = file.read(2048)
        file.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
            delimiter = dialect.delimiter
            if delimiter == "@":
                delimiter = ","
            logger.info(f"Using delimiter: {delimiter}")
        except csv.Error:
            logger.warning(
                "Não foi possível determinar o delimitador. Usando vírgula como padrão."
            )
            delimiter = ","

    if table_name is None:
        table_name = Path(file_path).stem.replace(" ", "_")

    # Conecta com o servidor
    cursor, conn = get_connection(server, username, password, database)

    # Decidir se usar chunksize ou não baseado no número de linhas no arquivo
    total_lines = sum(1 for line in open(file_path, "r", encoding=encoding))
    use_chunk = total_lines > batch_size

    # Leitura inicial para calcular o comprimento máximo das colunas
    df_reader = pd.read_csv(
        file_path,
        encoding=encoding,
        delimiter=delimiter,
        dtype=str,
        on_bad_lines="warn",
        engine="python",
        chunksize=batch_size,
    )

    # Determina os comprimentos máximos para cada coluna com base no arquivo completo
    max_lengths = {}
    for chunk in df_reader:
        chunk = chunk.astype(str)  # Converte todos os valores para string
        for col in chunk.columns:
            max_len_in_chunk = (
                chunk[col].map(len).max()
            )  # Comprimento máximo no chunk atual
            if col in max_lengths:
                max_lengths[col] = max(max_lengths[col], max_len_in_chunk)
            else:
                max_lengths[col] = max_len_in_chunk

    # Ajusta os comprimentos de acordo com as regras fornecidas
    column_definitions = []
    for col, max_len in max_lengths.items():
        if max_len < 255:
            length = 255
        else:
            length = (max_len + 4) // 5 * 5  # Arredonda para o próximo múltiplo de 5
        column_definitions.append(f"[{col}] NVARCHAR({length})")

    # Criação da tabela com os comprimentos ajustados
    create_table_sql = f'CREATE TABLE [{table_name}] ({", ".join(column_definitions)})'
    cursor.execute(f"DROP TABLE IF EXISTS [{table_name}]")
    cursor.execute(create_table_sql)
    conn.commit()
    logger.info(f"Tabela [{table_name}] criada com sucesso.")

    # Agora processa os dados em chunks e insere na tabela
    df_reader = pd.read_csv(
        filepath_or_buffer=file_path,
        encoding=encoding,
        delimiter=delimiter,
        dtype=str,
        on_bad_lines="warn",
        engine="python",
        chunksize=batch_size,
    )

    try:
        for chunk_index, chunk in enumerate(df_reader, start=1):
            chunk: pd.DataFrame
            if chunk.empty:
                logger.info(f"Chunk {chunk_index} está vazio. Pulando.")
                continue

            chunk = chunk.astype(str)  # Converte os valores do chunk para string
            chunk = chunk.replace("nan", None).replace(
                "", None
            )  # Substitui "nan" e vazios

            placeholders = ", ".join(["?"] * len(chunk.columns))
            insert_sql = f"INSERT INTO [{table_name}] VALUES ({placeholders})"
            cursor.fast_executemany = True
            cursor.executemany(insert_sql, chunk.values.tolist())
            conn.commit()
            rows_in_chunk = len(chunk)
            logger.info(
                f"Chunk {chunk_index}: {rows_in_chunk} linhas inseridas com sucesso."
            )
    except pyodbc.Error as e:
        logger.error(f"Erro ao criar a tabela ou inserir dados: {e}")
        conn.rollback()
    finally:
        close_connection(cursor, conn)

    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"Tempo de execução: {execution_time:.2f} segundos")
    return table_name


def create_sql_script_file(
    csv_file_path: Union[str, Path], template_name: str = "UFS_NOLA_TEMPLATE.sql"
) -> Optional[Path]:
    # Extrai o nome do arquivo CSV e o código do país (presumido nas primeiras letras)
    csv_file_name = Path(csv_file_path).stem
    country_code = csv_file_name[:2]

    # Define o caminho do template
    template_path: Path = Path(TEMPLATE_FOLDER_PATH) / template_name

    # Define o caminho da cópia do template
    copied_template_path = Path(template_path).with_name(
        f"temp_{Path(template_path).name}"
    )

    try:
        # Faz uma cópia do template
        shutil.copy(template_path, copied_template_path)
        logger.debug(f'Cópia do template criada em "{copied_template_path}".')

        # Lê o arquivo SQL template copiado e faz as substituições necessárias
        with open(copied_template_path, "r", encoding="cp1252") as template_file:
            sql_script = template_file.read()

        # Substitui os placeholders no template
        sql_script = sql_script.replace("[TEMPLATE_TABLE_NAME]", f"[{csv_file_name}]")
        sql_script = sql_script.replace(
            "DECLARE @PAIS VARCHAR(2) = 'MX'",
            f"DECLARE @PAIS VARCHAR(2) = '{country_code}'",
        )

        # Cria o caminho para o novo arquivo SQL (mesmo nome do CSV, mas com extensão .sql)
        new_sql_file_path = Path(csv_file_path).with_suffix(".sql")

        # Escreve o novo script SQL no arquivo
        with open(new_sql_file_path, "w", encoding="cp1252") as new_sql_file:
            new_sql_file.write(sql_script)

        logger.info(f"Arquivo SQL criado com sucesso: {new_sql_file_path.name}")

        return new_sql_file_path

    except Exception as e:
        logger.error(f"Erro ao criar o arquivo SQL: {e}")
    finally:
        # Apaga a cópia temporária do template
        if copied_template_path.exists():
            os.remove(copied_template_path)
            logger.debug(
                f'Cópia temporária do template "{copied_template_path}" apagada.'
            )


def process_csv_files(
    file_paths: List[Path],
    server: Optional[str] = None,
    database: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> None:
    for file_path in file_paths:
        file_path: Path
        try:
            table_name = load_csv_to_sqlserver(
                file_path=file_path,
                server=server,
                database=database,
                username=username,
                password=password,
            )
            logger.info(f'Arquivo "{file_path.stem}" importado com sucesso')
        except Exception as e:
            logger.error(f"Erro ao carregar o arquivo {file_path}: {e}")


def get_csv_files_to_process(fg_to_import_folder: bool, trafego_recebidos_path: Path):
    if fg_to_import_folder:
        # Busca todos os arquivos .csv na pasta de importação
        return list(IMPORT_FOLDER_PATH.glob("*.csv"))
    else:
        return list(trafego_recebidos_path.glob("*.csv"))


def process_import(
    config: Dict[str, str],
    fg_to_import_folder: bool,
    fg_create_sql_file: bool,
    key_name: str,
) -> None:
    key_path = config["path"]
    server_name = config["server_name"]
    database = config["database"]

    logger.info(f"Processando importação para a chave: {key_name}")

    client_received_path = Path(key_path) / datetime.now().strftime("%Y%m%d")

    if not fg_to_import_folder and not client_received_path.exists():
        logger.error(
            f"Diretório {client_received_path} não encontrado para a chave: {key_name}."
        )
        return

    try:
        csv_files_to_process = get_csv_files_to_process(
            fg_to_import_folder=fg_to_import_folder,
            trafego_recebidos_path=client_received_path,
        )

        if not csv_files_to_process:
            logger.warning(f"Nenhum arquivo CSV encontrado para a chave: {key_name}.")
            return

        logger.info(
            f"{len(csv_files_to_process)} arquivos encontrados para a chave: {key_name}."
        )

        process_csv_files(
            file_paths=csv_files_to_process,
            server=server_name,
            database=database,
            username=USERNAME,
            password=PASSWORD,
        )

        if fg_create_sql_file:
            for csv_file_path in csv_files_to_process:
                create_sql_script_file(csv_file_path=str(csv_file_path))
                logger.info(f"Arquivo SQL criado para o arquivo: {csv_file_path}")

    except Exception as e:
        logger.error(f"Erro ao processar os arquivos CSV para a chave {key_name}: {e}")


def main() -> None:
    while True:
        try:
            available_keys = get_available_keys(IMPORT_SETTINGS_JSON_PATH)
            selected_key_name = get_selected_key(available_keys)

            fg_to_import_folder = (
                input(
                    "\n-> A importação será feita na pasta local import? "
                    "\n1 - Sim\n0 - Não\n-> Insira o número da opção: "
                ).strip()
                == "1"
            )

            fg_create_sql_file = False
            if selected_key_name == "12":
                fg_create_sql_file = (
                    input(
                        "\n-> Deseja criar um arquivo .sql? "
                        "\n1 - Sim\n0 - Não\n-> Insira o número da opção: "
                    ).strip()
                    == "1"
                )

            start_time = time.time()
            terminal_line()

            validate_constants(
                paths=[
                    IMPORT_SETTINGS_JSON_PATH,
                    IMPORT_FOLDER_PATH,
                    TEMPLATE_FOLDER_PATH,
                ],
                values=[USERNAME, PASSWORD, selected_key_name],
            )

            required_keys = ["key_name", "path", "server_name", "database"]

            config = load_configuration(
                selected_key_name, IMPORT_SETTINGS_JSON_PATH, required_keys
            )
            if not config:
                continue

            process_import(
                config=config,
                fg_to_import_folder=fg_to_import_folder,
                fg_create_sql_file=fg_create_sql_file,
                key_name=selected_key_name,
            )

            execution_time(start_time)

            if not should_continue("importação"):
                break
        except Exception as e:
            logger.error(f"Ocorreu um erro durante a execução: {e}")


if __name__ == "__main__":
    try:
        start_config()
        main()
        logger.info("Script finalizado com sucesso.")
    except KeyboardInterrupt:
        logger.info("Script interrompido pelo usuário.")
    except Exception as e:
        logger.error(f"Ocorreu um erro durante a execução do script: {e}")
