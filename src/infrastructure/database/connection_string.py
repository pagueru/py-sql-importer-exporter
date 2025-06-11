"""Gerencia e valida strings de conexão ODBC para SQL Server."""

import json
import re
from typing import TYPE_CHECKING

from src.common.base.base_class import BaseClass
from src.config.constants import REQUIRED_KEYWORDS
from src.infrastructure.logger import LoggerSingleton

if TYPE_CHECKING:
    from logging import Logger


# DONE: Classe revisada e validada.
class ConnectionString(BaseClass):
    """Gerencia e valida strings de conexão ODBC para SQL Server."""

    def __init__(
        self,
        server_name: str,
        username: str,
        password: str,
        database: str | None = None,
        driver: str | None = None,
    ):
        """Inicializa a string de conexão com os parâmetros fornecidos."""
        self.logger: Logger = LoggerSingleton.logger or LoggerSingleton.get_logger()
        """Logger singleton para registrar eventos e erros."""

        self.server_name: str = server_name
        """Nome do servidor SQL Server."""

        self.username: str = username
        """Nome do usuário para autenticação no SQL Server."""

        self.password: str = password
        """Senha para autenticação no SQL Server."""

        self.database: str | None = database
        """Nome do banco de dados, se fornecido."""

        self.driver: str | None = driver if driver else "{ODBC Driver 17 for SQL Server}"
        """Driver ODBC padrão para SQL Server, se não for fornecido."""

        # Valida os parâmetros da string de conexão.
        self._validate_parameters()

        self.connection_string: str = self.create_connection_string()
        """String de conexão com base nos parâmetros fornecidos."""

        # Valida a estrutura da connection string final.
        self._validate_connection_string()

    def _validate_str_field(self, field_name: str, *, allow_none: bool = False) -> None:
        value = getattr(self, field_name)
        if allow_none and value is None:
            return
        # Valida se o campo é uma string não vazia
        if not isinstance(value, str):
            self.logger.error(
                f"{field_name} deve ser uma string{' ou None' if allow_none else ''}."
            )
            raise TypeError
        # Verifica se a string não é vazia ou composta apenas por espaços
        if not value.strip():
            self.logger.error(f"{field_name} não pode ser vazio ou só espaços.")
            raise ValueError

    def _validate_parameters(self) -> None:
        """Valida os parâmetros da string de conexão."""
        for field_name in ["server_name", "username", "password", "driver"]:
            # Validação para os campos obrigatórios (devem ser strings não vazias)
            self._validate_str_field(field_name)

        # Validação específica para database, que pode ser None
        self._validate_str_field("database", allow_none=True)

        # Exemplo de validação extra (opcional)
        if "\\" not in self.server_name and "." not in self.server_name:
            self.logger.warning(
                "O nome do servidor pode estar em formato incompleto: '%s'", self.server_name
            )

    def _validate_connection_string(self) -> None:
        """Valida a estrutura da connection string final usando expressões regulares."""
        for keyword in REQUIRED_KEYWORDS:
            pattern = rf"{re.escape(keyword)}[^;]+"

            # Verifica se todos os campos obrigatórios estão presentes usando regex
            if not re.search(pattern, self.connection_string):
                self.logger.error(f"A connection string está incompleta. Faltando: {keyword}")
                raise ValueError

        # Verifica delimitadores inválidos
        if re.search(r";;", self.connection_string) or re.search(r"=;", self.connection_string):
            self.logger.error(
                "A connection string contém delimitadores inválidos (ex: ';;' ou '=;')."
            )
            raise ValueError

        # Verifica valores nulos explícitos
        if re.search(r"None", self.connection_string):
            self.logger.error("A connection string contém valores nulos ('None').")
            raise ValueError

        self.logger.info("Connection string validada.")

    def create_connection_string(self) -> str:
        """Cria a string de conexão com base nos parâmetros fornecidos."""
        try:
            connection_string = (
                f"DRIVER={self.driver};"
                f"SERVER={self.server_name};"
                f"UID={self.username};"
                f"PWD={self.password}"
            )

            # Adiciona database se fornecido
            if self.database:
                connection_string += f";DATABASE={self.database}"

            # Máscara da senha para log seguro
            masked_connection_string = re.sub(r"(PWD=)[^;]+", r"\1******", connection_string)

            self.logger.info(f"String de conexão criada: '{masked_connection_string}'")

        except Exception:
            self.logger.exception("Erro ao criar a string de conexão.")
            raise
        else:
            return connection_string

    def dump_connection(self) -> str:
        """Retorna a string de conexão como uma string JSON."""
        try:
            connection_dict = {
                "server_name": self.server_name,
                "username": self.username,
                "password": self.password,
                "database": self.database,
                "driver": self.driver,
            }
            return json.dumps(connection_dict)
        except (TypeError, ValueError):
            self.logger.exception("Erro ao serializar a conexão para JSON.")
            raise
