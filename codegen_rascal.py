from __future__ import annotations
from typing import List
import ast_rascal as ast
from defs_rascal import Visitador, Categoria

class GeradorCodigoMEPA(Visitador):
    MEPA_OP = {
        '+': 'SOMA', '-': 'SUBT', '*': 'MULT', 'div': 'DIVI',
        'and': 'CONJ', 'or': 'DISJ', 'not': 'NEGA',
        '=': 'CMIG', '<>': 'CMDG', '<': 'CMME',
        '<=': 'CMEG', '>': 'CMMA', '>=': 'CMAG'
    }

    def __init__(self):
        self.codigo: List[str] = []
        self.erros: List[str] = []
        self.tem_erro = False
        self.label_counter = -1
        self.rotulos_procs = {} 
        self.current_level = 0

    def _erro(self, msg: str):
        self.erros.append(f"Erro CodeGen: {msg}")
        self.tem_erro = True

    def _emite(self, instr: str, arg1=None, arg2=None):
        line = f"   {instr}"
        if arg1 is not None:
            line += f" {arg1}"
            if arg2 is not None:
                line += f",{arg2}" 
        self.codigo.append(line)

    def _novo_rotulo(self) -> str:
        self.label_counter += 1
        return f"R{self.label_counter:02d}"

    def _emite_rotulo(self, rotulo: str):
        self.codigo.append(f"{rotulo}: NADA")

    # Programa Principal

    def visita_Programa(self, no: ast.Programa):
        self._emite("INPP")
        
        if no.total_vars_globais > 0:
            self._emite("AMEM", no.total_vars_globais)
        
        if no.bloco.decl_subrotinas:
            rotulo_main = self._novo_rotulo()
            self._emite("DSVS", rotulo_main)
            
            for sub in no.bloco.decl_subrotinas:
                self.visita(sub)
            
            self._emite_rotulo(rotulo_main)
        
        # Bloco principal
        self.visita(no.bloco.comando_composto)
        
        # Desaloca globais
        if no.total_vars_globais > 0:
            self._emite("DMEM", no.total_vars_globais)
            
        self._emite("PARA")
        self._emite("FIM")

    # Subrotinas
    
    def _gera_subrotina(self, no, tipo_decl):
        rotulo = self._novo_rotulo()
        self.rotulos_procs[no.simbolo.nome] = rotulo
        
        self._emite_rotulo(rotulo)
        
        nivel_anterior = self.current_level
        self.current_level = no.simbolo.nivel_lexico + 1
        
        self._emite("ENPR", self.current_level) 
        
        total_locais = no.total_vars_locais
        if total_locais > 0:
            self._emite("AMEM", total_locais)
            
        self.visita(no.bloco.comando_composto)
        
        if total_locais > 0:
            self._emite("DMEM", total_locais)
            
        total_params = 0
        if no.parametros:
            for p in no.parametros: total_params += len(p.ids)
            
        self._emite("RTPR", total_params)

        self.current_level = nivel_anterior

    def visita_DeclProcedimento(self, no: ast.DeclProcedimento):
        self._gera_subrotina(no, "PROC")

    def visita_DeclFuncao(self, no: ast.DeclFuncao):
        self._gera_subrotina(no, "FUNC")

    # Comandos

    def visita_ComandoComposto(self, no: ast.ComandoComposto):
        for cmd in no.comandos:
            self.visita(cmd)

    def visita_CmdAtribuicao(self, no: ast.CmdAtribuicao):
        self.visita(no.expressao)
        
        nivel = no.simbolo.nivel_lexico
        offset = no.simbolo.deslocamento

        if no.simbolo.categoria == Categoria.FUNC:
             nivel += 1
             
        self._emite("ARMZ", nivel, offset)

    def visita_CmdIf(self, no: ast.CmdIf):
        # Verifica se tem ELSE para decidir a estratégia de rótulos
        if no.cmd_else:
            # COM ELSE: Precisa de 2 rótulos
            rot_fim = self._novo_rotulo()
            rot_else = self._novo_rotulo()
            
            self.visita(no.condicao)
            self._emite("DSVF", rot_else) # Pula para o Else se falso
            
            self.visita(no.cmd_then)
            self._emite("DSVS", rot_fim)  # Pula o Else ao terminar o Then
            
            self._emite_rotulo(rot_else)
            self.visita(no.cmd_else)
            self._emite_rotulo(rot_fim)
        else:
            # Só precisa de 1 rótulo
            rot_saida = self._novo_rotulo()
            
            self.visita(no.condicao)
            self._emite("DSVF", rot_saida)
            
            self.visita(no.cmd_then)
            self._emite_rotulo(rot_saida)

    def visita_CmdWhile(self, no: ast.CmdWhile):
        rot_inicio = self._novo_rotulo()
        rot_fim = self._novo_rotulo()
        
        self._emite_rotulo(rot_inicio)
        self.visita(no.condicao)
        self._emite("DSVF", rot_fim)
        
        self.visita(no.cmd_do)
        self._emite("DSVS", rot_inicio)
        
        self._emite_rotulo(rot_fim)

    def visita_CmdRead(self, no: ast.CmdRead):
        for simbolo in no.simbolos:
            self._emite("LEIT")
            self._emite("ARMZ", simbolo.nivel_lexico, simbolo.deslocamento)

    def visita_CmdWrite(self, no: ast.CmdWrite):
        for expr in no.expressoes:
            self.visita(expr)
            self._emite("IMPR")

    def visita_CmdChamadaProcedimento(self, no: ast.CmdChamadaProcedimento):
        for arg in reversed(no.argumentos):
            self.visita(arg)
        
        nome = no.simbolo.nome
        if nome in self.rotulos_procs:
            rotulo = self.rotulos_procs[nome]
            self._emite("CHPR", rotulo, self.current_level)
        else:
            self._erro(f"Rótulo para '{nome}' não encontrado.")

    # Expressões

    def visita_ExpBinaria(self, no: ast.ExpBinaria):
        self.visita(no.esq)
        self.visita(no.dir)
        op_mepa = self.MEPA_OP.get(no.op)
        if op_mepa: self._emite(op_mepa)

    def visita_ExpUnaria(self, no: ast.ExpUnaria):
        self.visita(no.expressao)
        if no.op == '-': self._emite("INVR")
        elif no.op == 'not': self._emite("NEGA")

    def visita_ExpNumero(self, no: ast.ExpNumero):
        self._emite("CRCT", no.valor)

    def visita_ExpBooleano(self, no: ast.ExpBooleano):
        val = 1 if no.valor else 0
        self._emite("CRCT", val)

    def visita_ExpVariavel(self, no: ast.ExpVariavel):
        self._emite("CRVL", no.simbolo.nivel_lexico, no.simbolo.deslocamento)

    def visita_ExpChamadaFuncao(self, no: ast.ExpChamadaFuncao):
        self._emite("AMEM", 1) 
        for arg in reversed(no.argumentos):
            self.visita(arg)
        rotulo = self.rotulos_procs.get(no.simbolo.nome)
        self._emite("CHPR", rotulo, self.current_level)