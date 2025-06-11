"""Módulo exporter."""

import csv
from datetime import datetime
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from src.common.base.base_class import BaseClass
from src.config.constants import (
    BRT,
    EXPORT_DIR,
    SETTINGS_FILE,
    SQL_DIR,
)
from src.enum.operation_types import OperationType, SpecialChars
from src.infrastructure.database.database_connection_manager import (
    ConnectionString,
    DatabaseConnectionManager,
)
from src.infrastructure.logger import LoggerSingleton
from src.repositories.file_handler import YamlHandler
from src.repositories.sql_handler import SqlHandler

if TYPE_CHECKING:
    from logging import Logger


class ExporterService(BaseClass):
    """Gerencia operações de exportação de dados."""

    def __init__(self) -> None:
        """Inicializa o gerenciador de exportação."""
        self.logger: Logger = LoggerSingleton.logger or LoggerSingleton.get_logger()
        """Logger singleton para registrar eventos e erros."""

        self.yaml_handler = YamlHandler()
        self.global_config: dict[str, Any] = self.yaml_handler.read_file(SETTINGS_FILE)
        self.execution_mode: dict[str, Any] = self.global_config["execution_mode"]
        self.logger_config: dict[str, Any] = self.global_config["logger"]
        self.data_sources_config: dict[str, Any] = self.global_config["data_sources"][
            self.execution_mode
        ]
        self.credentials_config = self.global_config["credentials"][self.execution_mode]
        self.mapping_config: dict[str, Any] = self.global_config["mapping"]
        self.general_rules_config: dict[str, Any] = self.global_config["general_rules"]

        self.rule_contains_date: list[str] = self.general_rules_config["contains_date"]["clients"]
        self.file_handler = SqlHandler()
        self.choice_0_1 = OperationType.CHOICE_1_0.value
        self.arrow = SpecialChars.ARROW.value
        self.export = OperationType.EXPORT.value

    def run(self) -> None:
        """Executa o loop principal de exportação."""
        while True:
            export_config = self._define_config()
            self._process_export(export_config)
            if not self._should_continue(self.export):
                break
        super()._separator_line()

    def _define_config(self) -> dict[str, Any]:
        """Define a configuração de exportação com base no modo de execução."""
        available_clients_list = self.yaml_handler.get_available_keys(self.data_sources_config)
        selected_client_key = self.yaml_handler.get_selected_key(available_clients_list)
        selected_client = self.data_sources_config[selected_client_key]
        server_selected_client = selected_client["server_name"]["local"]
        database_selected_client = selected_client["database"]["local"]
        credential_selected_key = self.mapping_config[server_selected_client]
        credential_connection_dict = self.credentials_config[credential_selected_key]

        return {
            "client_name": selected_client_key,
            "server_name": server_selected_client,
            "username": credential_connection_dict["username"],
            "password": credential_connection_dict["password"],
            "database": database_selected_client,
        }

    def _process_export(self, client_config: dict[str, Any]) -> None:
        """Processa a exportação de dados para arquivos CSV com base em uma configuração."""
        try:
            client_name = client_config["client_name"]
            sql_file_path = self._define_sql_file_path(client_name)
            export_config = self._create_export_config(client_config)
            self.logger.debug(f"export_config: {self.dump_export_config(client_config)}")
            query_dict = self.file_handler.sql_to_dict(sql_file=sql_file_path)
            db_handler = self._initialize_database_handler(client_config)
            self._export_dict_to_csv(
                db_handler=db_handler,
                query_dict=query_dict,
                export_config=export_config,
            )
        except RuntimeError:
            self.logger.exception("Erro durante o processamento da exportação.")
            raise

    def _define_sql_file_path(self, selected_client: str) -> Path:
        """Define o caminho do arquivo SQL com base no cliente selecionado."""
        sql_file_path = Path(SQL_DIR) / f"{selected_client}.sql"
        if not sql_file_path.exists():
            self.logger.error(f"O arquivo SQL '{sql_file_path}' não existe.")
            raise FileNotFoundError
        return sql_file_path

    def _save_dataframe_to_csv(
        self, df: pd.DataFrame, output_file: Path, export_config: dict[str, Any]
    ) -> None:
        """Salva o DataFrame em um arquivo CSV."""
        if output_file.exists():
            output_file.unlink()
        quote_params: dict[str, Any] = {}
        if export_config["quotechar"]:
            quote_params["quotechar"] = export_config["quotechar"]
            quote_params["quoting"] = csv.QUOTE_ALL
        if df.empty:
            self.logger.warning("O DataFrame está vazio. Nenhum arquivo será salvo.")
            return
        try:
            df.to_csv(
                output_file,
                encoding=export_config["encoding"],
                index=False,
                sep=export_config["delimiter"],
                **quote_params,
            )
            self.logger.info(f'O arquivo "{output_file.stem}" foi criado com sucesso.')
        except Exception as e:
            self.logger.exception("Erro ao salvar o DataFrame em CSV.")
            raise RuntimeError from e

    def _export_dict_to_csv(
        self,
        db_handler: DatabaseConnectionManager,
        query_dict: dict[str, str],
        export_config: dict[str, Any],
    ) -> None:
        """Exporta consultas SQL (dicionário) para arquivos CSV."""
        client_folder = Path(export_config["output_path"] / export_config["client_name"])
        client_folder.mkdir(parents=True, exist_ok=True)
        with db_handler:
            if db_handler.conn is None:
                self.logger.error("Conexão com o banco de dados não estabelecida.")
                raise RuntimeError
            for key, value in query_dict.items():
                self._process_single_query(
                    key=key,
                    value=value,
                    db_handler=db_handler,
                    client_folder=client_folder,
                    export_config=export_config,
                )

    def _process_single_query(
        self,
        key: str,
        value: str,
        db_handler: DatabaseConnectionManager,
        client_folder: Path,
        export_config: dict[str, Any],
    ) -> None:
        """Processa uma única consulta SQL e salva o resultado em CSV."""
        try:
            df_queries = pd.read_sql_query(
                sql=value,
                con=db_handler.conn,  # type: ignore[reportArgumentType]
            )
        except (pd.errors.DatabaseError, ValueError):
            self.logger.exception(f"Erro ao executar a query '{key}'")
            raise
        file_name = self._generate_file_name(key)
        output_file = client_folder / file_name
        try:
            self._save_dataframe_to_csv(
                df=df_queries, output_file=output_file, export_config=export_config
            )
        except RuntimeError:
            self.logger.exception(f"Erro ao salvar o arquivo CSV '{output_file}'")
            raise

    def _check_client_key_in_general_rules(self, selected_client: str) -> bool:
        """Verifica se o cliente selecionado está dentro de `general_rules`."""
        if str(selected_client) in self.general_rules_config["contains_date"]["clients"]:
            self.logger.debug(
                f"O cliente selecionado '{selected_client}' está dentro de `general_rules`."
            )
            return True
        return False

    def _generate_formatted_datetime(self, date_format: str = "%Y%m%d") -> str:
        """Retorna a data atual formatada no padrão especificado."""
        return datetime.now(BRT).strftime(date_format)

    def _ensure_valid_response(self, response: str) -> str:
        """Garante que a resposta do usuário seja válida."""
        response = response.strip()
        while response not in ["0", "1"]:
            response = input(f"{self.arrow} Digite uma opção válida {self.choice_0_1}: ")
        return str(response)

    def _generate_file_name(self, selected_client: str) -> str:
        """Gera o nome do arquivo com base na chave selecionada e na escolha do usuário."""
        if not self._check_client_key_in_general_rules(selected_client):
            return f"{selected_client}.csv"
        user_decision = self._ensure_valid_response(
            input(
                f"{self.arrow} Deseja adicionar a data no início do nome do arquivo? "
                f"{self.choice_0_1}: "
            )
        )
        self.logger.debug(f"user_decision: {user_decision}")
        add_date_to_filename = user_decision == "1" if user_decision else False
        if add_date_to_filename:
            return f"{self._generate_formatted_datetime()}_{selected_client}.csv"
        return f"{selected_client}.csv"

    def _should_continue(self, operation_type: str) -> bool:
        """Pergunta ao usuário se deseja continuar com a operação."""
        try:
            response = self._ensure_valid_response(
                input(f"\n{self.arrow} Deseja realizar outra {operation_type}? {self.choice_0_1}: ")
            )
        except RuntimeError:
            self.logger.exception("Erro ao capturar a resposta.")
            return False
        else:
            self.logger.debug(f"Resposta capturada: {response}")
            return response == "1"

    def _get_output_path(self, selected_client: str) -> Path:
        """Retorna o caminho de saída formatado com a data atual."""
        export_folder = Path(EXPORT_DIR)

        if not export_folder.exists():
            self.logger.debug(f"Diretório {export_folder} não existe. Criando...")
            export_folder.mkdir(parents=True, exist_ok=True)
            # (export_folder / ".gitkeep").touch()

        file_name = self._generate_file_name(selected_client)
        return export_folder / file_name

    def _create_export_config(self, export_config: dict[str, Any]) -> dict[str, Any]:
        """Cria um objeto ExportConfig com base na configuração fornecida."""
        return {
            "output_path": self._get_output_path(export_config["client_name"]),
            "client_name": export_config["client_name"],
            # "encoding": export_config["encoding"],
            # quotechar=export_config["quotechar"],
            # delimiter=export_config["delimiter"],
            # contains_data=config["contains_data"],
        }

    def _initialize_database_handler(
        self, export_config: dict[str, Any]
    ) -> DatabaseConnectionManager:
        """Cria um handler de banco de dados com base na configuração."""
        conn_string = ConnectionString(
            server_name=export_config["server_name"],
            username=export_config["username"],
            password=export_config["password"],
            database=export_config["database"],
        )
        self.logger.debug(f"conn_string: {conn_string.dump_connection()}")
        return DatabaseConnectionManager(conn_string)

    def dump_export_config(self, export_config: dict[str, Any]) -> str:
        """Retorna a configuração de exportação como uma string JSON."""
        # Cria uma cópia para não modificar o original
        config_copy = export_config.copy()
        if "password" in config_copy:
            config_copy["password"] = "***"
        return json.dumps(config_copy)


def main() -> None:
    """Função principal do script."""
    try:
        exporter = ExporterService()
        exporter.run()
        print("Script finalizado com sucesso!")
    except KeyboardInterrupt:
        print("\nScript interrompido pelo usuário.")
    except Exception:
        print("Ocorreu um erro inesperado durante a execução do script.")
        raise
