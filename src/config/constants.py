"""Módulo de definição de constantes globais para o projeto."""

from pathlib import Path
from zoneinfo import ZoneInfo

APP_NAME: str = "py-sql-importer-exporter"
"""Nome da aplicação: `py-sql-importer-exporter`"""

VERSION: str = "0.1.0"
"""Versão da aplicação: `0.1.0`"""

SETTINGS_FILE: Path = Path("./src/config/files/settings.yaml")
"""Caminho para o arquivo de configuração global: `./src/config/files/settings.yaml`"""

EXPORT_DIR: Path = Path("./src/config/files/export")
"""Caminho para o diretório de exportação: `./src/config/files/export`"""

IMPORT_DIR: Path = Path("./src/config/files/import")
"""Caminho para o diretório de importação: `./src/config/files/import`"""

SQL_DIR: Path = Path("./src/config/files/sql")
"""Caminho para o diretório de arquivos SQL: `./src/config/files/sql`"""

BRT: ZoneInfo = ZoneInfo("America/Sao_Paulo")
"""Define o objeto de fuso horário para o horário de Brasília:  `America/Sao_Paulo`"""

REQUIRED_KEYWORDS = ["DRIVER=", "SERVER=", "UID=", "PWD="]
"""Keywords obrigatórias na string de conexão: `["DRIVER=", "SERVER=", "UID=", "PWD="]`"""
