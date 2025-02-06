import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pyodbc

from core.utils import logger


def get_connection(
    server_name: Union[str, None],
    username: Union[str, None],
    password: Union[str, None],
    database: Union[str, None] = None,
    driver: str = "{ODBC Driver 17 for SQL Server}",
) -> Tuple[pyodbc.Cursor, pyodbc.Connection]:
    logger.debug("get_connection: cria a conexão com o banco de dados.")
    try:
        # Construindo a string de conexão dinamicamente
        connection_string = (
            f"DRIVER={driver};SERVER={server_name};UID={username};PWD={password}"
        )
        if database:
            connection_string += f";DATABASE={database}"

        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.fast_executemany = True
        logger.info("A conexão com o banco de dados foi estabelecida.")
        return cursor, conn
    except pyodbc.Error as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        raise


def close_connection(cursor: pyodbc.Cursor, conn: pyodbc.Connection) -> None:
    try:
        if cursor is not None and isinstance(cursor, pyodbc.Cursor):
            cursor.close()
        if conn is not None and isinstance(conn, pyodbc.Connection):
            conn.close()
    except pyodbc.Error as e:
        logger.error(f"Erro ao fechar a conexao com o banco de dados: {e}")
    return None


def open_json_file(json_file_path: Union[str, Path]) -> Union[Dict[str, str], None]:
    try:
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            data: Dict[str, str] = json.load(json_file)
            logger.debug(f"Arquivo JSON {json_file_path} lido com sucesso.")
            return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Erro ao abrir o arquivo JSON: {e}")
        return None


def validate_constants(
    paths: Union[List[Union[str, Path]], Union[str, Path]],
    values: Union[List[Union[str, None]], Union[str, None]],
) -> None:
    try:

        def _ensure_list(value: Any):
            """Converte um valor em lista se não for lista."""
            if not isinstance(value, list):
                return [value]
            return value

        # Certifica de que os parâmetros sejam listas
        paths = _ensure_list(paths)
        values = _ensure_list(values)

        # Verifica se os caminhos existem
        for path in paths:
            if not isinstance(path, Path):
                path = Path(path)
            if not path.exists():
                raise FileNotFoundError(f"Caminho não encontrado: {path}")

        # Verifica se os valores não são None
        for value in values:
            if value is None:
                raise ValueError("Um dos valores fornecidos é None.")
    except RuntimeError as e:
        logger.error(f"Erro ao validar as constantes: {e}")
        raise


def key_names_list(
    json_file_path: Union[str, Path], print_terminal: bool = True
) -> Union[List[str], None]:
    try:
        with open(str(json_file_path), "r", encoding="utf-8") as json_file:
            json_data: dict = json.load(json_file)

        terminal_list: list = [
            f" — {key_number}: {key_data['key_name']}"
            for key_number, key_data in json_data.items()
        ]

        if print_terminal:
            print(*terminal_list, sep="\n")
        key_number_list: list = [key_number for key_number in json_data.keys()]
        logger.debug(f"Lista de chaves: {key_number_list}")
        return key_number_list
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Erro ao abrir ou ler o arquivo JSON: {e}")
        return None


def get_json_config(
    key_name: str,
    json_file_path: Union[str, Path],
    required_keys: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    try:
        # Carrega o arquivo JSON
        with open(json_file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        # Verifica se a chave existe no JSON
        if key_name not in json_data:
            raise KeyError(f"A chave {key_name} não foi encontrada no arquivo JSON.")

        config: dict = json_data[key_name]

        # Valida as chaves obrigatórias, se especificadas
        if required_keys:
            missing_keys = [key for key in required_keys if key not in config]
            if missing_keys:
                raise KeyError(
                    f"As seguintes chaves estão faltando para a chave {key_name}: "
                    f"{', '.join(missing_keys)}"
                )

        return config
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        logger.error(f"Erro ao obter a configuração do JSON: {e}")
        raise


def should_continue(action: str) -> bool:
    try:
        response = input(
            f"\n-> Deseja realizar outra {action}? (0 para não, 1 para sim): "
        )
        while response not in ["0", "1"]:
            response = input("-> Digite uma opção válida (0 para não, 1 para sim): ")
        return response == "1"
    except RuntimeError as e:
        logger.error(f"Erro ao capturar a resposta: {e}")
        return False


def load_configuration(
    selected_key: str, config_path: Path, required_keys: List[str]
) -> Optional[Dict[str, str]]:
    try:
        config = get_json_config(selected_key, config_path, required_keys)
        if not config:
            logger.error("Não foi possível carregar as configurações do cliente.")
            return None
        return config
    except RuntimeError as e:
        logger.error(f"Erro ao carregar a configuração: {e}")
        return None


def get_available_keys(config_path: Path) -> List[str]:
    try:
        logger.info("Obtendo a lista de chaves disponíveis.")
        available_keys = key_names_list(config_path)
        if not available_keys:
            logger.error(
                "A lista de chaves está vazia ou não foi carregada corretamente."
            )
            raise ValueError("Falha ao carregar a lista de chaves.")
        return available_keys
    except RuntimeError as e:
        logger.error(f"Erro ao obter a lista de chaves: {e}")
        raise


def get_selected_key(available_keys: List[str]) -> str:
    while True:
        try:
            key_name_input = input("-> Insira o número da chave: ")
            logger.debug(f"Entrada do usuário para a chave: {key_name_input}")

            if key_name_input.isdigit() and key_name_input in available_keys:
                logger.debug(f"Chave selecionada: {key_name_input}")
                return key_name_input
            print("Insira um número válido presente na lista de chaves disponíveis.")
        except RuntimeError as e:
            logger.error(f"Erro ao capturar a entrada do usuário: {e}")
            raise
