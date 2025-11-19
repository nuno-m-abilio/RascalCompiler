from __future__ import annotations
from dataclasses import dataclass
from typing import List, Any
import sys

class No: ...
class Comando(No): ...
class Expr(No): ...

@dataclass
class Programa(No):
    lista_comandos: List[Comando]

@dataclass
class CmdInput(Comando):
    id: Id

@dataclass
class CmdOutput(Comando):
    id: Id

@dataclass
class CmdAtrib(Comando):
    id: Id
    expr: Expr

@dataclass
class OpBin(Expr):
    op: str  # '+', '-', '*', '/'
    esq: Expr
    dir: Expr

@dataclass
class Num(Expr):
    valor: float

@dataclass
class Id(Expr):
    nome: str

# Padrão "visitor"
class Visitador:
    
    def visita(self, no: No) -> Any:
        nome_do_metodo = f'visita_{no.__class__.__name__}'
        metodo = getattr(self, nome_do_metodo, self.visita_default)
        
        return metodo(no)

    def visita_default(self, no: No):
        raise NotImplementedError(f"Nenhum método visita_{no.__class__.__name__} definido")

class Impressora_AST(Visitador):
    def __init__(self, saida=sys.stdout):
        self.saida = saida

    def imprime(self, texto: str):
        self.saida.write(texto)
    
    def visita_Programa(self, no: Programa):
        self.imprime("(programa")
        for c in no.lista_comandos:
            self.imprime(" ")
            self.visita(c)
        self.imprime(")")

    def visita_CmdInput(self, no: CmdInput):
        self.imprime("(input ")
        self.visita(no.id)
        self.imprime(")")

    def visita_CmdOutput(self, no: CmdOutput):
        self.imprime("(output ")
        self.visita(no.id)
        self.imprime(")")

    def visita_CmdAtrib(self, no: CmdAtrib):
        self.imprime("(atr ")
        self.visita(no.id)
        self.imprime(" ")
        self.visita(no.expr)
        self.imprime(")")

    def visita_OpBin(self, no: OpBin):
        self.imprime(f"({no.op} ")
        self.visita(no.esq)
        self.imprime(" ")
        self.visita(no.dir)
        self.imprime(")")

    def visita_Num(self, no: Num):
        self.imprime(repr(no.valor))

    def visita_Id(self, no: Id):
        self.imprime(no.nome)
