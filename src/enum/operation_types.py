"""Enum para definir os tipos de operações disponíveis no sistema."""

from enum import Enum


class OperationType(Enum):
    """Define os tipos de operações disponíveis no sistema."""

    EXPORT = "exportação"
    """Texto: exportação"""

    IMPORT = "importação"
    """Texto: importação"""

    CHOICE_1_0 = "(1 para sim, 0 para não)"
    """Texto: (1 para sim, 0 para não)"""

    CONTAINS_DATA = "contains_data"
    """Texto: contains_data"""


class SpecialChars(Enum):
    """Define os caracteres especiais."""

    ARROW = "➔"
    """Texto: ➔"""
