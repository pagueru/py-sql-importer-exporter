from datetime import datetime
from pathlib import Path
import sys
from typing import Any

from src.common.echo import echo
from src.config.constants import BRT, EXPORT_DIR, SETTINGS_FILE
from src.enum.operation_types import OperationType
from src.infrastructure.database.database_connection_manager import (
    ConnectionString,
    DatabaseConnectionManager,
)
from src.repositories.file_handler import YamlHandler
from src.services.exporter import main


def test_database_connection() -> None:
    """Testa a conexão e executa uma consulta simples no banco de dados."""
    conn_str = ConnectionString(
        # server_name="172.25.0.1,1420",
        # server_name="127.0.0.1,1420",
        server_name="localhost,1420",
        username="importer_exporter",
        password="Mssqlpassword1!",  # noqa: S106
        database="DB_CLIENTES",
    )
    with DatabaseConnectionManager(conn_str) as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"Resultado do teste: {result[0]}")


# test_database_connection()
# sys.exit()

choice_0_1 = OperationType.CHOICE_1_0.value
yaml_handler = YamlHandler()
global_config: dict[str, Any] = yaml_handler.read_file(SETTINGS_FILE)
arrow = "➔"

main()
sys.exit()


def get_formatted_datetime(date_format: str = "%Y%m%d") -> str:
    """Retorna a data atual formatada no padrão especificado."""
    return datetime.now(BRT).strftime(date_format)


def ensure_valid_response(response: str) -> str:
    while response not in ["0", "1"]:
        response = input(f"{arrow} Digite uma opção válida {choice_0_1}: ")
    return str(response)


execution_mode = global_config["execution_mode"]
print(f"execution_mode: {execution_mode}")
crendentials_dict = global_config["credentials"][execution_mode]
# print(f"crendentials_dict: {crendentials_dict}")
data_sources_dict = global_config["data_sources"][execution_mode]
# print(f"data_sources_dict: {data_sources_dict}")
mapping_dict = global_config["mapping"]
print(f"mapping_dict: {mapping_dict}")
special_config_dict = global_config["special_config"]


general_rules_dict = global_config["general_rules"]
contains_date = general_rules_dict["contains_date"]["clients"]
print(f"contains_date: {contains_date}")


# sys.exit()

# print(json.dumps(data_sources_dict, indent=4, ensure_ascii=False))
available_keys = yaml_handler.get_available_keys(data_sources_dict)
user_selected_key = yaml_handler.get_selected_key(available_keys)
print()
echo(f"Chave selecionada: {user_selected_key}", "info")


selected_client = data_sources_dict[user_selected_key]
server_selected_client = selected_client["server_name"]["local"]
database_selected_client = selected_client["database"]["local"]


credential_selected_key = mapping_dict[server_selected_client]
credential_connection_dict = crendentials_dict[credential_selected_key]


config_dict = {
    "client_name": user_selected_key,
    "server_name": server_selected_client,
    "username": credential_connection_dict["username"],
    "password": credential_connection_dict["password"],
    "database": database_selected_client,
}

# print(json.dumps(config_dict, indent=4, ensure_ascii=False))


export_config = ExportConfig(
    output_path=Path(EXPORT_DIR) / get_formatted_datetime(),
    client_name=config_dict["client_name"],
    # encoding=config["encoding"],
    # quotechar=config["quotechar"],
    # delimiter=config["delimiter"],
    # contains_data=config["contains_data"],
)

print(export_config.to_debug_config())

# def get_manual_export_config() -> dict[str, Any]:
#     """Pergunta ao usuário se ele deseja configurar manualmente as opções de exportação."""
#     echo("Gostaria de configurar manualmente as opções de exportação? (1 - Sim, 0 - Não)", "info")
#     user_choice = input("Escolha: ").strip()

#     if user_choice == "1":
#         # Pergunta sobre o delimitador
#         delimiters = [",", ";", "\t", "|"]
#         echo(f"Escolha um delimitador ({', '.join(delimiters)}):", "info")
#         delimiter = input("Delimitador: ").strip()
#         if delimiter not in delimiters:
#             echo("Delimitador inválido! Usando ',' como padrão.", "warning")
#             delimiter = ","

#         # Pergunta sobre o quotechar
#         quotechars = ['"', "'"]
#         echo(f"Escolha um quotechar ({', '.join(quotechars)}):", "info")
#         quotechar = input("Quotechar: ").strip()
#         if quotechar not in quotechars:
#             echo("Quotechar inválido! Usando '\"' como padrão.", "warning")
#             quotechar = '"'

#         # Pergunta se deve inserir a data no início do arquivo
#         echo("A exportação deve inserir a data no início do arquivo? (1 - Sim, 0 - Não)", "info")
#         contains_data = input("Escolha: ").strip()
#         if contains_data not in ["1", "0"]:
#             echo("Escolha inválida! Usando '1' como padrão.", "warning")
#             contains_data = "1"

#         return {
#             "delimiter": delimiter,
#             "quotechar": quotechar,
#             "contains_data": contains_data == "1",
#         }
#     echo("Usando configurações padrão de exportação.", "info")
#     return {
#         "delimiter": ",",
#         "quotechar": '"',
#         "contains_data": True,
#     }
