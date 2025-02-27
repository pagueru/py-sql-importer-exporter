import csv
import os
import shutil
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import chardet
import pandas as pd
import pyodbc

from core.constants import (
    IMPORT_FOLDER_PATH,
    IMPORT_SETTINGS_JSON_PATH,
    PASS_DW,
    TEMPLATE_FOLDER_PATH,
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
from core.utils import execution_time, logger, start_config, terminal_line


@dataclass
class ImportConfig:
    file_path: Union[str, Path]
    server: Optional[str]
    database: Optional[str]
    username: Optional[str]
    password: Optional[str]
    table_name: Optional[str] = None
    batch_size: int = 1000


def detect_delimiter(file_path: str, encoding: str) -> str:
    """
    Detecta o delimitador do CSV tentando diferentes separadores comuns.
    Retorna o delimitador mais provável com base na distribuição de colunas.
    """
    common_delimiters = [
        ",",
        ";",
        "\t",
        "|",
        " ",
    ]  # Adiciona os delimitadores mais usados
    best_delimiter = ","
    max_columns = 0

    with open(file_path, "r", encoding=encoding) as file:
        sample = file.read(2048)  # Lê apenas um trecho para análise

    for delimiter in common_delimiters:
        df_test = pd.read_csv(
            pd.io.common.StringIO(sample),
            delimiter=delimiter,
            nrows=5,
            dtype=str,
            engine="python",
        )
        num_columns = len(df_test.columns)

        if num_columns > max_columns:
            max_columns = num_columns
            best_delimiter = delimiter

    logger.info(f"Delimitador detectado: {best_delimiter}")
    return best_delimiter


def load_csv_to_sqlserver(import_config: ImportConfig) -> str:
    start_time = time.time()

    # Detectar o encoding do arquivo
    with open(import_config.file_path, "rb") as file:
        result = chardet.detect(file.read(10000))  # Lê apenas uma parte para eficiência
        encoding: str = str(result["encoding"])
        logger.info(f"Detectando encoding: {encoding}")

    # Detectar delimitador de forma confiável
    delimiter = detect_delimiter(import_config.file_path, encoding)

    # Gerar nome da tabela
    table_name = (
        Path(import_config.file_path).stem.replace(" ", "_")
        if not import_config.table_name
        else import_config.table_name
    )

    # Conectar ao banco de dados SQL Server
    cursor, conn = get_connection(
        import_config.server,
        import_config.username,
        import_config.password,
        import_config.database,
    )

    # Determinar número total de linhas
    with open(import_config.file_path, "r", encoding=encoding) as file:
        total_lines = sum(1 for _ in file)
    logger.info(f"Total de linhas no arquivo: {total_lines}")

    # Determinar comprimentos máximos de colunas
    df_reader = pd.read_csv(
        import_config.file_path,
        encoding=encoding,
        delimiter=delimiter,
        dtype=str,
        on_bad_lines="warn",
        engine="python",
        chunksize=import_config.batch_size,
    )

    max_lengths: Dict[str, int] = {}
    for chunk in df_reader:
        chunk = chunk.astype(str)  # Garante que os dados são strings
        for col in chunk.columns:
            max_len_in_chunk = chunk[col].map(len).max()
            max_lengths[col] = max(max_lengths.get(col, 0), max_len_in_chunk)

    # Criar definição das colunas da tabela
    column_definitions = [
        f"[{col}] NVARCHAR({(max_len + 4) // 5 * 5 if max_len >= 255 else 255})"
        for col, max_len in max_lengths.items()
    ]

    # Criar tabela no banco de dados
    create_table_sql = f'CREATE TABLE [{table_name}] ({", ".join(column_definitions)})'
    cursor.execute(f"DROP TABLE IF EXISTS [{table_name}]")
    cursor.execute(create_table_sql)
    conn.commit()
    logger.info(f"Tabela [{table_name}] criada com sucesso.")

    # Inserir os dados no banco
    df_reader = pd.read_csv(
        import_config.file_path,
        encoding=encoding,
        delimiter=delimiter,
        dtype=str,
        on_bad_lines="warn",
        engine="python",
        chunksize=import_config.batch_size,
    )

    try:
        for chunk_index, chunk in enumerate(df_reader, start=1):
            if chunk.empty:
                logger.info(f"Chunk {chunk_index} está vazio. Pulando.")
                continue

            chunk = chunk.astype(str).replace("nan", None).replace("", None)
            placeholders = ", ".join(["?"] * len(chunk.columns))
            insert_sql = f"INSERT INTO [{table_name}] VALUES ({placeholders})"
            cursor.fast_executemany = True
            cursor.executemany(insert_sql, chunk.values.tolist())
            conn.commit()
            logger.info(
                f"Chunk {chunk_index}: {len(chunk)} linhas inseridas com sucesso."
            )
    except pyodbc.Error as e:
        logger.error(f"Erro ao criar a tabela ou inserir dados: {e}")
        conn.rollback()
    finally:
        close_connection(cursor, conn)

    # Log de tempo de execução
    logger.info(f"Tempo de execução: {time.time() - start_time:.2f} segundos")
    return table_name


def create_sql_script_file(
    csv_file_path: Union[str, Path], template_name: str = "UFS_NOLA_TEMPLATE.sql"
) -> Optional[Path]:
    # Preparação para criação de script SQL baseado em template
    csv_file_name = Path(csv_file_path).stem
    country_code = csv_file_name[:2]
    template_path: Path = Path(TEMPLATE_FOLDER_PATH) / template_name

    copied_template_path = Path(template_path).with_name(
        f"temp_{Path(template_path).name}"
    )

    try:
        shutil.copy(template_path, copied_template_path)
        logger.debug(f"Cópia do template criada em '{copied_template_path}'.")

        with open(copied_template_path, "r", encoding="cp1252") as template_file:
            sql_script = template_file.read()

        sql_script = sql_script.replace("[TEMPLATE_TABLE_NAME]", f"[{csv_file_name}]")
        sql_script = sql_script.replace(
            "DECLARE @PAIS VARCHAR(2) = 'MX'",
            f"DECLARE @PAIS VARCHAR(2) = '{country_code}'",
        )

        new_sql_file_path = Path(csv_file_path).with_suffix(".sql")

        with open(new_sql_file_path, "w", encoding="cp1252") as new_sql_file:
            new_sql_file.write(sql_script)

        logger.info(f"Arquivo SQL criado com sucesso: {new_sql_file_path.name}")
        return new_sql_file_path

    except RuntimeError as e:
        logger.error(f"Erro ao criar o arquivo SQL: {e}")
        raise
    finally:
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
            import_config = ImportConfig(
                file_path=file_path,
                server=server,
                database=database,
                username=username,
                password=password,
            )
            load_csv_to_sqlserver(import_config=import_config)
            logger.info(f'Arquivo "{file_path.stem}" importado com sucesso')
        except Exception as e:
            logger.error(f"Erro ao carregar o arquivo {file_path}: {e}")


def get_csv_files_to_process(fg_to_import_folder: bool, trafego_recebidos_path: Path):
    if fg_to_import_folder:
        # Busca todos os arquivos .csv na pasta de importação
        return list(IMPORT_FOLDER_PATH.glob("*.csv"))
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
            username=USER_DW,
            password=PASS_DW,
        )

        if fg_create_sql_file:
            for csv_file_path in csv_files_to_process:
                create_sql_script_file(csv_file_path=str(csv_file_path))
                logger.info(f"Arquivo SQL criado para o arquivo: {csv_file_path}")

    except Exception as e:
        logger.error(f"Erro ao processar os arquivos CSV para a chave {key_name}: {e}")


def main() -> None:
    while True:
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
            values=[USER_DW, PASS_DW, selected_key_name],
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


if __name__ == "__main__":
    try:
        start_config()
        main()
        logger.info("Script finalizado com sucesso.")
    except KeyboardInterrupt:
        logger.info("Script interrompido pelo usuário.")
    except Exception as e:
        logger.error(f"Ocorreu um erro durante a execução do script: {e}")
