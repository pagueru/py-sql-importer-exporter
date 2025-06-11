"""Módulo."""

import logging
from pathlib import Path

from src.config.constypes import PathLike

logger = logging.getLogger(__name__)


# TODO: Remanejar classe.
class SqlHandler:
    """Classe responsável por manipular arquivos SQL."""

    def __init__(self) -> None:
        pass

    def sql_to_dict(self, sql_file: PathLike, classifier: str = "--") -> dict[str, str]:
        """Lê um arquivo SQL e o converte em um dicionário."""
        sql_file = Path(sql_file)
        if not sql_file.is_file():
            logger.exception(f"Arquivo SQL não encontrado: {sql_file}")
            raise FileNotFoundError

        query_list = {}
        file_name, query = None, ""

        try:
            # Lê o arquivo SQL linha por linha
            with sql_file.open("r", encoding="utf-8") as file:
                for line in file:
                    stripped_line = line.strip()

                    # Verifica se a linha começa com o classificador
                    if classifier and stripped_line.startswith(classifier):
                        # Salva a consulta anterior no dicionário
                        if file_name:
                            query_list[file_name] = query.rstrip()
                        # Inicia uma nova consulta
                        file_name, query = stripped_line.lstrip(classifier).strip(), ""
                    else:
                        # Concatena a linha na consulta atual
                        query += stripped_line + " "

                # Salva a última consulta, se existir
                if file_name:
                    query_list[file_name] = query.rstrip()

        except RuntimeError:
            logger.exception(f"Erro ao processar o arquivo SQL '{sql_file}'")

        # Verifica se o dicionário contém consultas válidas
        if not query_list:
            logger.error(f"O arquivo SQL '{sql_file}' não contém consultas válidas.")
            raise ValueError

        return query_list
