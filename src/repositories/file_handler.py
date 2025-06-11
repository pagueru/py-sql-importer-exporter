"""Módulo."""

import logging
from pathlib import Path
import sys
from typing import Any

import yaml

from src.common.echo import echo
from src.config.constypes import PathLike

logger = logging.getLogger(__name__)
arrow = "➔"


# TODO: Remanejar classe.
class YamlHandler:
    """Classe responsável por manipular arquivos YAML."""

    def read_file(self, yaml_file: PathLike) -> dict[str, Any]:
        """Abre um arquivo YAML e retorna seu conteúdo como um dicionário."""
        try:
            yaml_file = Path(yaml_file)
            with yaml_file.open("r", encoding="utf-8") as file:
                yaml_data = yaml.safe_load(file)
                logger.debug(f"Arquivo YAML {yaml_file} lido com sucesso.")
                return yaml_data
        except FileNotFoundError:
            logger.exception(f"Arquivo {yaml_file} não encontrado.")
            raise
        except (RuntimeError, yaml.YAMLError):
            logger.exception("Erro inesperado ao carregar arquivo YAML.")
            raise

    def get_yaml_key(
        self, yaml_data: dict[str, Any], key_name: str, required_keys: list[str] | None = None
    ) -> str:
        """Obtém o valor de uma chave específica em um arquivo YAML."""
        if key_name not in yaml_data:
            logger.error(f"A chave '{key_name}' não foi encontrada no arquivo YAML.")
            raise KeyError

        yaml_key_value: Any = yaml_data[key_name]

        if required_keys:
            missing_keys = [key for key in required_keys if key not in yaml_key_value]
            if missing_keys:
                logger.error(
                    f"Das chaves requeridas, faltam as seguintes: {missing_keys}. "
                    f"Configuração atual: {yaml.safe_dump(yaml_key_value, allow_unicode=True)}"
                )
                raise KeyError
            logger.debug(f"Todas as chaves requeridas estão presentes: {required_keys}")

        return yaml_key_value

    def get_available_keys(self, yaml_data: dict[str, Any]) -> list[str]:
        """Obtém a lista de chaves disponíveis em um arquivo YAML."""
        try:
            logger.info("Obtendo a lista de chaves disponíveis.")
            available_keys = self.list_yaml_keys(yaml_data)
            if not available_keys:
                logger.error("A lista de chaves está vazia ou não foi carregada corretamente.")
                raise ValueError
        except RuntimeError:
            logger.exception("Erro ao obter a lista de chaves.")
            raise
        else:
            return available_keys

    def list_yaml_keys(
        self, yaml_data: dict[str, Any], *, print_terminal: bool = True
    ) -> list[str]:
        """Obtém a lista de chaves de um arquivo YAML e imprime se solicitado."""
        key_list: list[str] = list(yaml_data.keys())
        if print_terminal:
            self._output_indexed_keys(key_list)
        logger.debug(f"Lista de chaves: {key_list}")
        return key_list

    def _output_indexed_keys(self, keys: list[str]) -> None:
        """Imprime a lista de chaves com índices sequenciais."""
        terminal_list: list[str] = [f" {idx}. {key}" for idx, key in enumerate(keys, start=1)]
        print(*terminal_list, sep="\n")

    def get_selected_key(self, available_keys: list[str]) -> str:
        """Obtém a chave selecionada pelo usuário."""
        while True:
            try:
                key_name_input = input(f"{arrow} Insira o número da chave: ")
                logger.debug(f"Entrada do usuário para a chave: {key_name_input}")

                if key_name_input.isdigit():
                    key_index = int(key_name_input) - 1
                    if 0 <= key_index < len(available_keys):
                        selected_key = available_keys[key_index]
                        logger.debug(f"Chave selecionada: {selected_key}")
                        return selected_key

                print("Insira um número válido presente na lista de chaves disponíveis.")
            except KeyboardInterrupt:
                print()
                echo("Processo interrompido pelo usuário.", "warn")
                sys.exit(0)

    def search_in_dict(self, data: dict, target: str, key_index: int) -> str:
        """Procura recursivamente uma string em um dicionário e retorna a chave pelo índice."""
        results: list[tuple[str, Any]] = []

        def recursive_search(d: dict, path: str = "s") -> None:
            """Procura recursivamente a string no dicionário."""
            for key, value in d.items():
                current_path: str = f"{path}.{key}" if path else key
                if isinstance(value, dict):
                    recursive_search(value, current_path)
                elif target in str(value):
                    results.append((current_path, value))

        recursive_search(data)
        if not results:
            logger.error(f"A string '{target}' não foi encontrada no dicionário.")
            raise ValueError
        if key_index < 1 or key_index > len(results):
            logger.error(
                f"O índice fornecido ({key_index}) está fora do intervalo (1 a {len(results)})."
            )
            raise IndexError
        selected_path: str = results[0][0]
        selected_key = selected_path.split(".")[-key_index]
        logger.debug(f"Chave selecionada pelo índice {key_index}: {selected_key}")
        return selected_key
