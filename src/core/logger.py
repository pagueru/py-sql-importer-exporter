import logging

from .constants import LOG_FILE_PATH

# Atribui um logger com o nome do módulo atual
logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Nível mínimo de severidade que será capturado

# Atribui um handler para registrar logs em um arquivo
file_handler: logging.FileHandler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
file_handler.setLevel(logging.INFO)  # Nível de log para arquivo

# Atribui um handler para exibir logs no console
console_handler: logging.StreamHandler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Nível de log para console

# Atribui um formato de log tanto para o arquivo quanto para o console
formatter: logging.Formatter = logging.Formatter(
    fmt="%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",  # Formato de data/hora sem microsegundos
)

# Atribui o formato definido ao handler do arquivo e do console
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Atribui os handlers (arquivo e console) ao logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Teste de mensagens de log
# logger.info('Mensagem de informação.')
