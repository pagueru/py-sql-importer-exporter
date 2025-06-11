"""Módulo responsável pelo carregamento e validação de configurações do projeto."""

import json
from pathlib import Path
import time
from typing import Any
import winsound

import yaml

from src.common.base.base_class import BaseClass
from src.common.echo import echo
from src.common.errors.errors import SettingsManagerError
from src.config.constants import SETTINGS_FILE
from src.config.constypes import PathLike


# TODO: Refatorar funcionalidades da classe.
class SettingsManager(BaseClass):
    """Classe de repositório de utilitários de configurações."""

    def __init__(self, settings: Path | None = None) -> None:
        """Inicializa a classe de utilitários de configurações."""
        self.timer = time.time()
        """Armazena o tempo de início do script para cálculo de tempo de execução."""

        self.settings: dict[str, Any] = self._load_yaml(settings if settings else SETTINGS_FILE)
        """Carrega o arquivo de configurações YAML: `./src/config/settings.yaml`"""

        self.logger_settings = self.settings["logger"]
        """Dicionário de configurações do `logger`."""

    def separator_line(self, char: str = "-", padding: int = 0) -> None:
        """Imprime uma linha ajustada ao tamanho do terminal."""
        return super()._separator_line(char, padding)

    def start_config(self, *, clear_terminal: bool = True) -> None:
        """Limpa o terminal e marca o início do script."""
        try:
            if clear_terminal:
                print("\033[H\033[J", end="", flush=True)
            self.separator_line()
            echo("Iniciando o script.", "info")
        except SettingsManagerError:
            echo("Erro inesperado ao limpar o terminal.", "error")
            raise

    def execution_time(self, *, beep: bool = False) -> None:
        """Calcula e registra o tempo de execução do script."""
        try:
            self.separator_line()
            echo(f"Tempo de execução: {round(time.time() - self.timer, 2)} segundos.", "info")
            if beep:
                # winsound.Beep(400, 10)
                winsound.MessageBeep()
        except SettingsManagerError:
            echo("Erro inesperado ao calcular o tempo de execução.", "error")
            raise

    def _load_yaml(self, file_path: PathLike, key: str | None = None) -> dict[str, Any]:
        """Carrega um dicionário a partir de um arquivo YAML."""
        try:
            file_path = Path(file_path)
            with file_path.open("r", encoding="utf-8") as file:
                settings = yaml.safe_load(file)
                return settings[key] if key else settings
        except FileNotFoundError:
            echo("Arquivo de configurações não encontrado.", "error")
            raise
        except KeyError:
            echo(f"Chave '{key}' não encontrada no arquivo de configurações.", "error")
            raise
        except yaml.YAMLError:
            echo("Erro ao processar o YAML.", "error")
            raise
        except SettingsManagerError:
            echo("Erro inesperado ao carregar as configurações.", "error")
            raise

    def print_dict(self, data: dict[str, Any] | None = None) -> None:
        """Imprime um dicionário formatado como JSON."""
        try:
            if not isinstance(data, dict):
                echo("O dado fornecido não é um dicionário.", "error")
                return
            if data is not None:
                print(json.dumps(data, indent=4, ensure_ascii=False))
        except SettingsManagerError:
            echo("Erro inesperado ao imprimir o dicionário.", "error")
            raise

    def verify_settings(self, settings: dict[str, Any]) -> None:
        """Verifica se todas as chaves de cada configuração possuem valores não nulos ou vazios."""
        for section, section_dict in settings.items():
            if not isinstance(section_dict, dict):
                continue
            missing_keys = []
            for key, value in section_dict.items():
                if value in (None, ""):
                    missing_keys.append(key)
            if missing_keys:
                echo(
                    f"Campos obrigatórios ausentes ou vazios em '{section}':"
                    f"{', '.join(missing_keys)}.",
                    "error",
                )
                raise SettingsManagerError
