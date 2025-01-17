from os import getenv
from pathlib import Path
from typing import Final, Optional

from dotenv import load_dotenv


def find_project_root(start_dir: Optional[Path] = None) -> Path:
    """
    Encontra o diretório raiz do projeto a partir do diretório informado.

    A busca é feita procurando pelo arquivo 'pyproject.toml' em todos os
    diretórios pais do diretório informado. Caso o arquivo seja encontrado, o
    diretório pai é considerado o diretório raiz do projeto.

    Args:
        start_dir (Path, optional): O diretório a partir do qual a busca
            começará. Se omitido, o diretório atual (onde o script está
            localizado) será usado.

    Returns:
        Path: O diretório raiz do projeto localizado.

    Raises:
        FileNotFoundError: Se o arquivo 'pyproject.toml' não for encontrado em
            nenhum diretório pai.
    """
    start_path: Path = Path(start_dir or __file__).resolve()
    for parent in start_path.parents:
        if (parent / "pyproject.toml").exists():
            return parent

    raise FileNotFoundError(
        "O arquivo 'pyproject.toml' não foi encontrado em nenhum diretório pai."
    )


# Caminho base do projeto
PROJECT_PATH: Path = find_project_root()

# Diretórios principais
CONFIG_FOLDER_PATH: Path = PROJECT_PATH / "config"
DATA_FOLDER_PATH: Path = PROJECT_PATH / "data"
LOG_FOLDER_PATH: Path = PROJECT_PATH / "log"

# Subdiretórios dentro de 'data'
TEMPLATE_FOLDER_PATH: Path = DATA_FOLDER_PATH / "template"
QUERYS_FOLDER_PATH: Path = DATA_FOLDER_PATH / "sql"
EXPORT_FOLDER_PATH: Path = DATA_FOLDER_PATH / "export"
IMPORT_FOLDER_PATH: Path = DATA_FOLDER_PATH / "import"

# Arquivos principais
LOG_FILE_PATH: Path = LOG_FOLDER_PATH / "app.log"
EXPORT_SETTINGS_JSON_PATH: Path = CONFIG_FOLDER_PATH / "export_config.json"
IMPORT_SETTINGS_JSON_PATH: Path = CONFIG_FOLDER_PATH / "import_config.json"
TRANSFER_SETTINGS_JSON_PATH: Path = CONFIG_FOLDER_PATH / "transfer_config.json"

# Nome do projeto
PROJECT_PATH_NAME: str = PROJECT_PATH.name

# Carrega variáveis do .env
try:
    # Define o caminho para o arquivo .env
    ENV_PATH: Final[Path] = PROJECT_PATH / "config" / "credentials.env"

    # Verificação de existência do arquivo .env
    if not ENV_PATH.exists():
        raise FileNotFoundError(
            f"O arquivo .env não foi encontrado no caminho: {ENV_PATH}"
        )

    # Carrega as variáveis
    load_dotenv(ENV_PATH)

    # Atribui as variáveis a constantes
    USER_DW: Final[Optional[str]] = getenv("USER_DW")
    PASS_DW: Final[Optional[str]] = getenv("PASS_DW")
    USER_PROD: Final[Optional[str]] = getenv("USER_PROD")
    PASS_PROD: Final[Optional[str]] = getenv("PASS_PROD")
    SERVER_DW_21: Final[Optional[str]] = getenv("SERVER_DW_21")
    SERVER_DW_14: Final[Optional[str]] = getenv("SERVER_DW_14")
    SERVER_PROD: Final[Optional[str]] = getenv("SERVER_PROD")

    # Variáveis obrigatórias
    required_vars = {
        "USER_DW": USER_DW,
        "PASS_DW": PASS_DW,
        "USER_PROD": USER_PROD,
        "PASS_PROD": PASS_PROD,
        "SERVER_DW_21": SERVER_DW_21,
        "SERVER_DW_14": SERVER_DW_14,
        "SERVER_PROD": SERVER_PROD,
    }

    # Valida variáveis nulas
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(
            f"As variáveis estão ausentes ou vazias no arquivo .env: {', '.join(missing_vars)}"
        )

except Exception as e:
    raise RuntimeError(
        f"Ocorreu um erro ao carregar as variáveis de ambiente: {e}"
    ) from e
