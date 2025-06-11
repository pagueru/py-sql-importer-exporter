"""Módulo de utilitários do projeto."""

import os
from pathlib import Path
import time
from typing import Any
import winsound

import yaml

from src.common.logger import LoggerSingleton
from src.config.constypes import PathLike


# TODO: Refatorar funcionalidades da classe.
class ProjectUtils:
    """Classe de utilitários do projeto."""

    def __init__(self, start_dir: Path | None = None):
        """Inicializa a classe ProjectUtils."""
        self.start_dir = start_dir or Path.cwd()
        self.repo_path = Path(__file__).resolve().parents[2]  # Subindo três níveis
        self.logger = LoggerSingleton()
        self.timer = time.time()

    def find_project_root(self) -> Path:
        """Encontra o diretório raiz do projeto a partir do diretório que instancia a classe."""
        for parent in self.start_dir.parents:
            if (parent / "pyproject.toml").exists():
                return parent
        return Path("./").resolve()

    def create_gitkeep_for_empty_dirs(self) -> None:
        """Adiciona um arquivo .gitkeep em diretórios vazios do repositório."""
        # Garantindo que o erro esperado seja levantado durante os testes
        if not self.repo_path.exists():
            self.logger.error("Diretório do repositório não encontrado.")
            raise FileNotFoundError
        self.logger.debug("Diretório do repositório encontrado com sucesso.")

        self.logger.debug(f"Verificando diretórios vazios em {self.repo_path}.")
        total_dirs = 0
        existing_gitkeep = 0
        created_gitkeep = 0

        for current_path, subdirectories, filenames in os.walk(self.repo_path):
            # Ignorar diretórios .git e .venv
            filtered_subdirectories: list[str] = []
            for subdir in subdirectories:
                if subdir not in [".git", ".venv"]:
                    filtered_subdirectories.append(subdir)
            subdirectories[:] = filtered_subdirectories

            total_dirs += 1

            # Verificar se o diretório está vazio
            if not filenames and not subdirectories:
                gitkeep_path = Path(current_path) / ".gitkeep"
                gitkeep_path.touch()
                created_gitkeep += 1
                self.logger.debug(f"Adicionado .gitkeep em {current_path}")
            # Verificar se .gitkeep já existe
            elif ".gitkeep" in filenames:
                existing_gitkeep += 1
                self.logger.debug(f".gitkeep já existe em {current_path}")

        self.logger.info(
            f"Verificação de diretórios vazios concluída. Total: {total_dirs}, "
            f"Existentes: {existing_gitkeep}, Criados: {created_gitkeep}"
        )

    def print_terminal_line(self, value: int = 80, char: str = "-") -> None:
        """Imprime uma linha no terminal com o caractere especificado."""
        if value <= 0:
            msg = "O valor deve ser maior que 0."
            raise ValueError(msg)
        print(char * value)

    def start_config(self, *, clear_terminal: bool = True) -> None:
        """Limpa o terminal e marca o início do script."""
        try:
            if clear_terminal:
                print("\033[H\033[J", end="", flush=True)
            self.print_terminal_line()
            self.logger.info("Iniciando o script.")
        except RuntimeError:
            self.logger.exception("Erro ao limpar o terminal.")

    def execution_time(self, *, beep: bool = False) -> None:
        """Calcula e registra o tempo de execução do script."""
        self.logger.info(f"Tempo de execução: {round(time.time() - self.timer, 2)} segundos.")
        if beep:
            winsound.Beep(750, 300)
