from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from typing import Union

from pathlib import Path
from typing import Union


def find_dir_ancestors(
    dir_name: str,
    start_dir: Union[str, Path] = __file__,
) -> Path:

    try:
        start_path = (
            Path(start_dir) if isinstance(start_dir, str) else start_dir.resolve()
        )
        for parent in start_path.parents:
            potential_dir = parent / dir_name
            if potential_dir.is_dir():
                return potential_dir
        raise FileNotFoundError(
            f'O diretório "{dir_name}" não encontrado a partir de "{start_path}".'
        )
    except Exception:
        raise


# Atribui as constantes raízes
FILE_PATH = Path(__file__).resolve()
PROJECT_PATH: Path = find_dir_ancestors("src").parent

# Atribui as constantes de pastas
CONFIG_FOLDER_PATH: Path = PROJECT_PATH / "config"
DATA_FOLDER_PATH: Path = PROJECT_PATH / "data"
LOG_FOLDER_PATH: Path = PROJECT_PATH / "log"

# Atribui as constantes da pasta 'data'
TEMPLATE_FOLDER_PATH: Path = DATA_FOLDER_PATH / "template"
QUERYS_FOLDER_PATH: Path = DATA_FOLDER_PATH / "sql"
EXPORT_FOLDER_PATH: Path = DATA_FOLDER_PATH / "export"
IMPORT_FOLDER_PATH: Path = DATA_FOLDER_PATH / "import"

# Atribui as constantes de arquivos
LOG_FILE_PATH: Path = LOG_FOLDER_PATH / "app.log"
EXPORT_SETTINGS_JSON_PATH: Path = CONFIG_FOLDER_PATH / "export_config.json"
IMPORT_SETTINGS_JSON_PATH: Path = CONFIG_FOLDER_PATH / "import_config.json"

# Atribui as constantes de nomes de pasta
PROJECT_PATH_NAME: str = PROJECT_PATH.name

try:
    load_dotenv(PROJECT_PATH / "config" / "credentials.env")
    USERNAME: Union[str, None] = getenv("USERNAME")
    PASSWORD: Union[str, None] = getenv("PASSWORD")
except Exception as e:
    print(f"Erro ao carregar as variáveis de ambiente: {e}")
