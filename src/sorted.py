import shutil
from pathlib import Path

from core.constants import EXPORT_FOLDER_PATH, PROJECT_PATH_NAME
from core.utils import logger


# Função para criar uma pasta se ela não existir
def create_folder(path: Path) -> None:
    if not path.exists():
        path.mkdir(
            parents=True, exist_ok=True
        )  # Cria a pasta, incluindo pais se necessário
        logger.info(f"Pasta criada: {path}")


# Função que move arquivos CSV da pasta do cliente para a estrutura organizada
def move_files(
    client_folder: Path, date_folder: Path, sorted_path: Path, overwrite: bool = False
) -> None:
    # Define a pasta de destino dentro da estrutura 'sorted'
    destination_folder = sorted_path / client_folder.name / date_folder.name
    create_folder(destination_folder)  # Cria a pasta de destino se necessário

    # Itera sobre os arquivos CSV na pasta do cliente
    for file in client_folder.glob("*.csv"):
        if file.is_file():
            # Define o caminho completo para mover o arquivo
            destination_file = destination_folder / file.name

            # Verifica se o arquivo já existe e decide o que fazer com base no parâmetro 'overwrite'
            if destination_file.exists():
                if overwrite:
                    # Sobrescreve o arquivo existente
                    shutil.move(str(file), str(destination_file))
                    logger.info(f"Arquivo sobrescrito: {file.name}")
                else:
                    # Loga a existência do arquivo e pula para o próximo
                    logger.info(f"Arquivo já existe e não foi movido: {file.name}")
            else:
                # Move o arquivo para a pasta organizada, pois não existe conflito
                shutil.move(str(file), str(destination_file))
                logger.info(f"Arquivo movido: {file.name}")


# Função para obter o caminho da pasta relativa a partir de 'data'
def get_relative_folder_path(path: Path, base_folder: str = PROJECT_PATH_NAME) -> Path:
    try:
        # Encontra o índice da pasta 'data' e retorna o caminho relativo a partir de 'data'
        index = path.parts.index(base_folder)
        return Path(*path.parts[index + 1 :])  # Ignora 'data' no retorno
    except ValueError:
        # Caso a pasta 'data' não seja encontrada, retorna o caminho completo (fallback)
        return path


# Função para remover pastas vazias após os arquivos serem movidos
def remove_empty_folders(path: Path) -> None:
    # Itera sobre as subpastas e verifica recursivamente as subpastas mais internas primeiro
    for subfolder in sorted(
        path.iterdir(), reverse=True
    ):  # Inverte a ordem para ir do mais profundo para o mais raso
        if subfolder.is_dir():
            remove_empty_folders(
                subfolder
            )  # Chama a função recursivamente para as subpastas

    # Após verificar e remover as subpastas, verifica se a pasta atual está vazia
    if not any(path.iterdir()):  # Se a pasta estiver vazia
        relative_path = get_relative_folder_path(path)
        path.rmdir()  # Remove a pasta vazia
        logger.info(f"Pasta vazia removida: {relative_path}")


# Função principal que organiza arquivos por data e cliente
def organize_files(
    export_path: Path, sorted_path: Path, overwrite: bool = False
) -> None:
    found_valid_folders = (
        False  # Variável para rastrear se alguma pasta válida foi encontrada
    )

    # Itera sobre as pastas de datas no diretório export
    for date_folder in export_path.iterdir():
        # Verifica se a pasta é válida (diretório com nome no formato YYYYMMDD)
        if (
            date_folder.is_dir()
            and date_folder.name.isdigit()
            and len(date_folder.name) == 8
        ):
            found_valid_folders = True  # Marca que foi encontrada ao menos uma pasta
            # Itera sobre as pastas de clientes dentro de cada data
            for client_folder in date_folder.iterdir():
                if client_folder.is_dir():  # Verifica se é uma pasta de cliente
                    move_files(
                        client_folder, date_folder, sorted_path, overwrite=overwrite
                    )  # Move os arquivos
            # Após processar todos os arquivos, remove pastas de data vazias, se necessário
            remove_empty_folders(date_folder)

    if not found_valid_folders:
        logger.info("Nenhuma pasta válida para organizar foi encontrada.")
    else:
        logger.info("Organização completa!")


# Função que inicializa todo o processo de organização dos arquivos
def main() -> None:
    # Defina overwrite=True para substituir arquivos
    overwrite = False

    # Define os caminhos de exportação e da pasta 'sorted'
    sorted_path: Path = EXPORT_FOLDER_PATH / "sorted"

    create_folder(sorted_path)  # Cria a pasta 'sorted' se necessário
    organize_files(
        EXPORT_FOLDER_PATH, sorted_path, overwrite=overwrite
    )  # Inicia a organização dos arquivos


# Executa o script chamando a função main
if __name__ == "__main__":
    main()
