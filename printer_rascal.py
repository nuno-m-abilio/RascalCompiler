from __future__ import annotations
import sys
import ast_rascal as ast
from defs_rascal import Visitador

class ImpressoraAST(Visitador):
    def __init__(self, saida=sys.stdout):
        self.saida = saida

    def imprime(self, texto: str):
        self.saida.write(texto)

    # Programa e Bloco
    def visita_Programa(self, no: ast.Programa):
        self.imprime("(Programa ")
        self.imprime(no.id)
        self.imprime("\n  ")
        self.visita(no.bloco)
        self.imprime("\n)\n")

    def visita_Bloco(self, no: ast.Bloco):
        self.imprime("(Bloco")
        # Variáveis
        if no.decl_vars:
            self.imprime("\n    (Vars")
            for decl in no.decl_vars:
                self.imprime(" ")
                self.visita(decl)
            self.imprime(")")
        
        # Subrotinas
        if no.decl_subrotinas:
            self.imprime("\n    (Subrotinas")
            for sub in no.decl_subrotinas:
                self.imprime("\n      ")
                self.visita(sub)
            self.imprime(")")

        # Comandos
        self.imprime("\n    ")
        self.visita(no.comando_composto)
        self.imprime(")")

    def visita_BlocoSubrotina(self, no: ast.BlocoSubrotina):
        # Similar ao Bloco, mas sem subrotinas aninhadas
        self.imprime("(Corpo")
        if no.decl_vars:
            self.imprime(" (Vars")
            for decl in no.decl_vars:
                self.imprime(" ")
                self.visita(decl)
            self.imprime(")")
        
        self.imprime(" ")
        self.visita(no.comando_composto)
        self.imprime(")")

    # Declarações

    def visita_DeclVariaveis(self, no: ast.DeclVariaveis):
        # Ex: (Decl x,y : integer)
        ids = ",".join(no.ids)
        self.imprime(f"[{ids} : {no.tipo}]")

    def visita_DeclProcedimento(self, no: ast.DeclProcedimento):
        self.imprime(f"(Proc {no.id} params:[")
        if no.parametros:
            for p in no.parametros:
                self.visita(p)
        self.imprime("] ")
        self.visita(no.bloco)
        self.imprime(")")

    def visita_DeclFuncao(self, no: ast.DeclFuncao):
        self.imprime(f"(Func {no.id} :{no.tipo_retorno} params:[")
        if no.parametros:
            for p in no.parametros:
                self.visita(p)
        self.imprime("] ")
        self.visita(no.bloco)
        self.imprime(")")

    def visita_Parametro(self, no: ast.Parametro):
        ids = ",".join(no.ids)
        self.imprime(f" {{{ids}:{no.tipo}}} ")

    # Comandos

    def visita_ComandoComposto(self, no: ast.ComandoComposto):
        self.imprime("(Begin")
        for cmd in no.comandos:
            self.imprime("\n      ")
            self.visita(cmd)
        self.imprime(")")

    def visita_CmdAtribuicao(self, no: ast.CmdAtribuicao):
        self.imprime(f"(Atrib {no.id} ")
        self.visita(no.expressao)
        self.imprime(")")

    def visita_CmdIf(self, no: ast.CmdIf):
        self.imprime("(If ")
        self.visita(no.condicao)
        self.imprime("\n        Then ")
        self.visita(no.cmd_then)
        if no.cmd_else:
            self.imprime("\n        Else ")
            self.visita(no.cmd_else)
        self.imprime(")")

    def visita_CmdWhile(self, no: ast.CmdWhile):
        self.imprime("(While ")
        self.visita(no.condicao)
        self.imprime("\n        Do ")
        self.visita(no.cmd_do)
        self.imprime(")")

    def visita_CmdRead(self, no: ast.CmdRead):
        ids = ", ".join(no.ids)
        self.imprime(f"(Read {ids})")

    def visita_CmdWrite(self, no: ast.CmdWrite):
        self.imprime("(Write")
        for expr in no.expressoes:
            self.imprime(" ")
            self.visita(expr)
        self.imprime(")")

    def visita_CmdChamadaProcedimento(self, no: ast.CmdChamadaProcedimento):
        self.imprime(f"(CallProc {no.id}")
        if no.argumentos:
            for arg in no.argumentos:
                self.imprime(" ")
                self.visita(arg)
        self.imprime(")")

    # Expressões

    def visita_ExpBinaria(self, no: ast.ExpBinaria):
        self.imprime(f"({no.op} ")
        self.visita(no.esq)
        self.imprime(" ")
        self.visita(no.dir)
        self.imprime(")")

    def visita_ExpUnaria(self, no: ast.ExpUnaria):
        self.imprime(f"({no.op} ")
        self.visita(no.expressao)
        self.imprime(")")

    def visita_ExpVariavel(self, no: ast.ExpVariavel):
        self.imprime(f"(Var {no.id})")

    def visita_ExpNumero(self, no: ast.ExpNumero):
        self.imprime(str(no.valor))

    def visita_ExpBooleano(self, no: ast.ExpBooleano):
        self.imprime("true" if no.valor else "false")

    def visita_ExpChamadaFuncao(self, no: ast.ExpChamadaFuncao):
        self.imprime(f"(CallFunc {no.id}")
        if no.argumentos:
            for arg in no.argumentos:
                self.imprime(" ")
                self.visita(arg)
        self.imprime(")")