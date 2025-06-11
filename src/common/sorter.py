"""Módulo para organizar arquivos CSV exportados em uma estrutura ordenada."""

from pathlib import Path
import shutil

from src.config.constants import EXPORT_DIR
from src.infrastructure.logger import LoggerSingleton

# Constantes
DATE_FOLDER_NAME_LENGTH: int = 8


class CSVFileSorter:
    """Classe responsável por organizar arquivos CSV exportados em uma estrutura ordenada."""

    def __init__(
        self,
        export_path: Path | None = None,
        sorted_path: Path | None = None,
    ) -> None:
        """Inicializa a classe Sorted com os caminhos necessários."""
        self.export_path = export_path or Path(EXPORT_DIR)
        self.sorted_path = sorted_path or Path(EXPORT_DIR) / "sorted"
        self.logger = LoggerSingleton()

    def _ensure_sorted_path(self) -> None:
        """Garante que o caminho de destino para os arquivos organizados exista."""
        # Garantindo que o método mkdir seja chamado corretamente
        if not self.sorted_path.exists():
            self.sorted_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Criada a pasta de destino: {self.sorted_path}")
        else:
            self.logger.debug("A pasta de destino já existe.")

    def move_files(
        self, client_folder: Path, date_folder: Path, *, overwrite: bool = False
    ) -> None:
        """Move arquivos CSV da pasta do cliente para a estrutura organizada."""
        # Garante que o caminho de destino para os arquivos organizados exista
        destination_folder = self.sorted_path / client_folder.name / date_folder.name
        if not destination_folder.exists():
            destination_folder.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Criada a pasta de destino: {destination_folder}")

        # Itera sobre os arquivos CSV na pasta do cliente
        csv_files = list(client_folder.glob("*.csv"))
        if not csv_files:
            self.logger.info(f"Nenhum arquivo CSV encontrado na pasta do cliente: {client_folder}")
        for file in csv_files:
            if file.is_file():
                # Define o caminho completo para mover o arquivo
                destination_file = destination_folder / file.name

                # Verifica se o arquivo já existe
                if destination_file.exists():
                    if overwrite:
                        # Sobrescreve o arquivo existente
                        shutil.move(str(file), str(destination_file))
                        self.logger.info(f"Arquivo sobrescrito: {file.name}.")
                    else:
                        # Loga a existência do arquivo e pula para o próximo
                        self.logger.info(f"Arquivo já existe e não foi movido: {file.name}.")
                else:
                    # Move o arquivo para a pasta organizada, pois não existe conflito
                    shutil.move(str(file), str(destination_file))
                    self.logger.info(f"Arquivo movido: {file.name}.")

    def get_relative_folder_path(self, path: Path, base_folder: str) -> Path:
        """Obtém o caminho da pasta relativa a partir da pasta base."""
        try:
            # Encontra o índice da pasta base e retorna o caminho relativo
            index = path.parts.index(base_folder)
            return Path(*path.parts[index + 1 :])
        except ValueError:
            # Caso a pasta base não seja encontrada, retorna o caminho completo (fallback)
            return path

    def remove_empty_folders(self, path: Path) -> None:
        """Remove pastas vazias após os arquivos serem movidos."""
        # Itera sobre as subpastas e verifica recursivamente as subpastas mais internas primeiro
        for subfolder in sorted(path.iterdir(), reverse=True):
            if subfolder.is_dir():
                self.remove_empty_folders(subfolder)

        # Após verificar e remover as subpastas, verifica se a pasta atual está vazia
        if not any(path.iterdir()):
            relative_path = self.get_relative_folder_path(path, "./")
            path.rmdir()
            self.logger.info(f"Pasta vazia removida: {relative_path}")

    def organize_files(self, *, overwrite: bool = False) -> None:
        """Organiza arquivos por data e cliente."""
        found_valid_folders = False

        # Itera sobre as pastas de datas no diretório export
        for date_folder in self.export_path.iterdir():
            # Verifica se a pasta é válida (diretório com nome no formato YYYYMMDD)
            if (
                date_folder.is_dir()
                and date_folder.name.isdigit()
                and len(date_folder.name) == DATE_FOLDER_NAME_LENGTH
            ):
                found_valid_folders = True
                # Itera sobre as pastas de clientes dentro de cada data
                for client_folder in date_folder.iterdir():
                    if client_folder.is_dir():
                        self.move_files(client_folder, date_folder, overwrite=overwrite)
                # Após processar todos os arquivos, remove pastas de data vazias, se necessário
                self.remove_empty_folders(date_folder)

        if not found_valid_folders:
            self.logger.info("Nenhuma pasta válida para organizar foi encontrada.")
        else:
            self.logger.info("Organização completa!")

    def run(self, *, overwrite: bool = False) -> None:
        """Executa o processo completo de organização de arquivos."""
        self.organize_files(overwrite=overwrite)
