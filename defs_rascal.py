from __future__ import annotations
from dataclasses import dataclass, field
import ast_rascal as ast
from typing import List, Optional


 # Tipos
class Tipo:...

@dataclass(frozen=True)
class TipoInt(Tipo):
    def __str__(self) -> str: return "integer"

@dataclass(frozen=True)
class TipoBool(Tipo):
    def __str__(self) -> str: return "boolean"

TIPO_INT = TipoInt()
TIPO_BOOL = TipoBool()

def get_tipo_by_name(name: str) -> Tipo | None:
    if name == 'integer': return TIPO_INT
    if name == 'boolean': return TIPO_BOOL
    return None

# Tabela de Símbolos

class Categoria:
    VAR = 'var'
    PARAM = 'param'
    PROC = 'procedure'
    FUNC = 'function'
    PROGRAM = 'program'

@dataclass
class Simbolo:
    nome: str
    categoria: str
    tipo: Optional[Tipo] = None
    
    # Para funções e procedimentos: lista de tipos dos parâmetros
    params_tipos: List[Tipo] = field(default_factory=list)
    
    # Para geração de código (futuro)
    nivel_lexico: int = 0
    deslocamento: int = 0
    rotulo: str = ""

# Visitor genérico
class Visitador:
    def visita(self, no):
        if no is None:
            return
        
        # Se for uma lista (ex: lista de comandos), visita cada item
        if isinstance(no, list):
            for item in no:
                self.visita(item)
            return

        # Descobre o nome da classe do nó (ex: Programa, CmdIf)
        # e tenta chamar o método visita_NomeDaClasse
        nome_metodo = f'visita_{type(no).__name__}'
        visitor = getattr(self, nome_metodo, self.visita_padrao)
        return visitor(no)

    def visita_padrao(self, no):
        raise NotImplementedError(f"O método {type(no).__name__} não foi implementado no printer.")