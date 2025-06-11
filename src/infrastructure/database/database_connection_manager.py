"""Gerencia conexões com um banco de dados SQL Server via ODBC."""

import json
import re
import types
from typing import TYPE_CHECKING

import pyodbc

from src.common.base.base_class import BaseClass
from src.config.constants import REQUIRED_KEYWORDS
from src.infrastructure.database.connection_string import ConnectionString
from src.infrastructure.logger import LoggerSingleton

if TYPE_CHECKING:
    from logging import Logger


# DONE: Classe revisada e validada.
class DatabaseConnectionManager:
    """Gerencia conexões com um banco de dados SQL Server via ODBC."""

    def __init__(self, connection_params: ConnectionString):
        """Inicializa os parâmetros de conexão com os dados fornecidos."""
        self.logger: Logger = LoggerSingleton.logger or LoggerSingleton.get_logger()

        # Verifica se connection_params é uma instância de ConnectionString
        if not isinstance(connection_params, ConnectionString):
            self.logger.error("Parâmetro inválido: connection_params deve ser ConnectionString.")
            raise TypeError

        self.connection_string: str = connection_params.connection_string
        """String de conexão para o banco de dados SQL Server."""

        # Valida a connection string antes de prosseguir
        if not self._is_valid_connection_string(self.connection_string):
            self.logger.error("A connection string fornecida é inválida.")
            raise ValueError

        self.conn: pyodbc.Connection | None = None
        """Conexão com o banco de dados, iniciada como None."""

        self.cursor: pyodbc.Cursor | None = None
        """Cursor para executar comandos SQL, iniciado como None."""

    def check_connection(self, timeout: int = 10) -> bool:
        """Testa a conexão com o banco de dados sem abrir contexto completo.

        **Exemplo de uso**:

            if db.check_connection():
                print("Conexão está OK!")
            else:
                print("Conexão falhou.")
        """
        try:
            self.logger.info("Testando conexão com o banco de dados...")
            conn = pyodbc.connect(self.connection_string, timeout=timeout)
            conn.close()
            self.logger.info("Teste de conexão bem-sucedido.")
        except pyodbc.Error as e:
            self.logger.warning(f"Falha ao testar a conexão: {e}")
            return False
        else:
            return True

    def __enter__(self) -> pyodbc.Cursor:
        """Abre a conexão automaticamente ao entrar no contexto."""
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            self.cursor.fast_executemany = True
            self.logger.info("Conexão com o banco de dados estabelecida.")
        except pyodbc.Error as e:
            self.logger.exception("Erro ao conectar ao banco de dados.")
            raise ConnectionError from e
        return self.cursor

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Garante que a conexão será fechada ao sair do contexto."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            self.logger.info("Conexão com o banco de dados fechada.")
        except pyodbc.Error as e:
            self.logger.exception("Erro ao fechar a conexão com o banco de dados.")
            raise ConnectionError from e

    @staticmethod
    def _is_valid_connection_string(conn_str: str) -> bool:
        """Valida superficialmente a connection string."""
        return all(keyword in conn_str for keyword in REQUIRED_KEYWORDS)
