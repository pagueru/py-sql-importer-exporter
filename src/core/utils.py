import json
import logging
import platform
import subprocess
import time
import warnings
import winsound
from pathlib import Path
from typing import Dict, List, Optional, TypeAlias, Union

from .constants import LOG_FILE_PATH

FilePathStr: TypeAlias = Union[str, Path, List[Union[str, Path]]]


def setup_logger(
    log_file_path: Optional[Path] = None,
    enable_file_log: bool = False,
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Configura e retorna um logger com handlers para console e arquivo (opcional).

    Args:
        name (str): Nome do logger (geralmente `__name__`).
        log_file_path (Optional[Path]): Caminho do arquivo de log.
        enable_file_log (bool): Ativa ou desativa o log em arquivo (padrão: False).
        level (int): Nível de log (padrão: INFO).

    Returns:
        logging.Logger: Logger configurado.
    """
    logger_setup: logging.Logger = logging.getLogger(__name__)
    logger_setup.setLevel(level)

    # Evita adicionar handlers duplicados
    if logger_setup.hasHandlers():
        return logger_setup

    # Formato do log
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger_setup.addHandler(console_handler)

    # Handler opcional para arquivo
    if enable_file_log and log_file_path:
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger_setup.addHandler(file_handler)

    return logger_setup


# Inicializa o logger global
logger = setup_logger(log_file_path=LOG_FILE_PATH)


def organize_json(file_path: FilePathStr) -> None:
    """
    Organiza um arquivo JSON com chaves sequenciais.

    Args:
        file_path (JsonFilePath): Caminho do arquivo JSON ou lista de caminhos.
    """
    if isinstance(file_path, (str, Path)):
        file_path = [file_path]

    file_paths = [
        Path(fpath) if isinstance(fpath, str) else fpath for fpath in file_path
    ]

    for path in file_paths:
        logger.info(f"Processando arquivo JSON: {path.name}")
        try:
            with open(path, "r", encoding="utf-8") as file:
                data: Dict[str, Dict[str, str]] = json.load(file)

            data_list = list(data.values())
            data_list.sort(key=lambda item: item["key_name"])
            sorted_data = {str(i + 1): item for i, item in enumerate(data_list)}

            with open(path, "w", encoding="utf-8") as file:
                json.dump(sorted_data, file, indent=4, ensure_ascii=False)

            logger.info(f"Arquivo JSON reorganizado com sucesso: {path.name}")
        except Exception as e:
            logger.error(f"Erro ao processar o arquivo JSON {path.name}: {e}")

    logger.info("Todos os arquivos JSON foram processados.")


def start_config() -> None:
    try:
        subprocess.run(
            ["cls" if platform.system() == "Windows" else "clear"],
            shell=True,
            check=False,
        )
        warnings.filterwarnings(
            action="ignore", message="pandas only supports SQLAlchemy connectable"
        )
        logger.info("Iniciando o script.")
    except RuntimeError as e:
        logger.error(f"Erro ao limpar o terminal: {e}")
        raise


def terminal_line(value: int = 79, char: str = "-") -> None:
    if not isinstance(value, int) or not isinstance(char, str):
        raise TypeError("Os argumentos devem ser int e str, respectivamente.")
    if value <= 0:
        raise ValueError("O valor deve ser maior que 0.")
    print(char * value)


def execution_time(start_time: float) -> None:
    logger.info(f"Tempo de execução: {round(time.time() - start_time, 2)} segundos")
    winsound.Beep(750, 300)
