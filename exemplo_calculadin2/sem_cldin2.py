from __future__ import annotations
from typing import List, Dict
import ast_cldin2 as ast
from defs_cldin2 import Visitador, Simbolo, Categoria, Tipo, TIPO_REAL, TIPO_BOOL

# Tabela de Símbolos
class TabelaSimbolos:
    def __init__(self) -> None:
        self.escopos: List[Dict[str, Simbolo]] = [dict()]
        self.deslocamento_atual: int = 0

    def abre_escopo(self):
        self.escopos.append({})

    def fecha_escopo(self):
        if len(self.escopos) > 1:
            self.escopos.pop()

    def instala(self, s: Simbolo) -> str|None:
        atual = self.escopos[-1]
        if s.nome in atual:
            return f"Identificador '{s.nome}' já declarado neste escopo"
        s.deslocamento = self.deslocamento_atual
        atual[s.nome] = s
        self.deslocamento_atual += 1
        return None

    def busca(self, nome: str) -> Simbolo|None:
        for tabela in reversed(self.escopos):
            if nome in tabela:
                return tabela[nome]
        return None
    
    @property
    def total_vars_alocadas(self) -> int:
        return self.deslocamento_atual

class VerificadorSemantico(Visitador):
    def __init__(self) -> None:
        self.ts: TabelaSimbolos = TabelaSimbolos()
        self.erros: List[str] = []
        self.tem_erro: bool = False

    def _erro(self, msg: str):
        self.erros.append(f"{msg}")
        self.tem_erro = True

    def _verifica_tipo_bin(self, op: str, t_esq: Tipo, t_dir: Tipo) -> Tipo|None:
        # Operadores aritméticos: (real, real) -> real
        if op in ('+', '-', '*', '/'):
            if t_esq is not TIPO_REAL or t_dir is not TIPO_REAL:
                self._erro(f"Operador '{op}' exige operandos 'real' (recebeu {t_esq}, {t_dir})")
            return TIPO_REAL
        
        # Operadores lógicos: (bool, bool) -> bool
        if op in ('and', 'or'):
            if t_esq is not TIPO_BOOL or t_dir is not TIPO_BOOL:
                self._erro(f"Operador '{op}' exige operandos 'booleano' (recebeu {t_esq}, {t_dir})")
            return TIPO_BOOL
        
        # Operadores de diferença: (real, real) -> bool OU (bool, bool) -> bool
        if op in ('==', '!='):
            if t_esq is not t_dir:
                self._erro(f"Operador '{op}' não pode comparar tipos diferentes ({t_esq} vs {t_dir})")
            return TIPO_BOOL
        
        # Operadores relacionais: (real, real) -> bool
        if op in ('<', '<=', '>', '>='):
            if t_esq is not TIPO_REAL and t_dir is not TIPO_REAL:
                self._erro(f"Operador '{op}' exige operandos 'real' (recebeu {t_esq}, {t_dir})")
            return TIPO_BOOL
        
        return None

    def _verifica_tipo_unario(self, op: str, t_calculo: Tipo) -> Tipo|None:
        # Operador unário 'not': (bool) -> bool
        if op == 'not':
            if t_calculo is not TIPO_BOOL:
                self._erro(f"Operador 'not' exige 'booleano' (recebeu {t_calculo})")
            return TIPO_BOOL
        return None
    
    # Visitação
    def visita_Programa(self, prog: ast.Programa):
        self.visita(prog.bloco_cmds)
        prog.total_vars = self.ts.total_vars_alocadas


    def visita_BlocoCmds(self, bloco: ast.BlocoCmds):
        for cmd in bloco.lista_cmds:
            self.visita(cmd)


    def visita_Declaracao(self, decl: ast.Declaracao):
        if decl.nome_tipo == "real":
            tipo_var = TIPO_REAL
        elif decl.nome_tipo == "bool":
            tipo_var = TIPO_BOOL
        else:
            self._erro(f"Tipo desconhecido '{decl.nome_tipo}' na declaração de '{decl.id.nome}'.")
            return

        simbolo = Simbolo(nome=decl.id.nome, cat=Categoria.VAR, tipo=tipo_var)
        
        erro_instala = self.ts.instala(simbolo)
        if erro_instala:
            self._erro(erro_instala)
            return

        self.visita(decl.id)


    def visita_Atribuicao(self, cmd: ast.Atribuicao):
        self.visita(cmd.calculo)
        self.visita(cmd.id) 
        
        # deu erro em algum lado
        if cmd.id.tipo is None or cmd.calculo.tipo is None:
            return

        tipo_id = cmd.id.tipo
        tipo_calc = cmd.calculo.tipo
        
        if tipo_id is not tipo_calc:
             self._erro(f"Atribuição inválida: Variável '{cmd.id.nome}' é do tipo {tipo_id} e não pode receber valor do tipo {tipo_calc}.")


    def visita_Condicional(self, cmd: ast.Condicional):
        self.visita(cmd.condicao)

        if cmd.condicao.tipo is not TIPO_BOOL:
            self._erro(f"Condição 'if' exige expressão booleana (recebeu {cmd.condicao.tipo}).")

        self.ts.abre_escopo()
        self.visita(cmd.bloco_then)
        self.ts.fecha_escopo()
        
        if cmd.bloco_else:
            self.ts.abre_escopo()
            self.visita(cmd.bloco_else)
            self.ts.fecha_escopo()


    def visita_Funcao(self, func: ast.Funcao):
        self.visita(func.argumento)
        

    def visita_CalculoBinario(self, calc: ast.CalculoBinario):
        self.visita(calc.esq)
        self.visita(calc.dir)

        # deu erro em algum lado
        if calc.esq.tipo is None or calc.dir.tipo is None:
            calc.tipo = None
            return

        tipo_resultado = self._verifica_tipo_bin(calc.op, calc.esq.tipo, calc.dir.tipo)
        calc.tipo = tipo_resultado


    def visita_CalculoUnario(self, calc: ast.CalculoUnario):
        self.visita(calc.calculo)

        if calc.calculo.tipo is None:
            calc.tipo = None
            return

        tipo_resultado = self._verifica_tipo_unario(calc.op, calc.calculo.tipo)
        calc.tipo = tipo_resultado


    def visita_CalcId(self, id: ast.CalcId):
        simbolo = self.ts.busca(id.nome)
        
        if simbolo is None:
            self._erro(f"Variável '{id.nome}' não foi declarada neste escopo.")
            id.tipo = None
            return

        id.tipo = simbolo.tipo
        id.simbolo = simbolo


    def visita_CalcConstNum(self, const: ast.CalcConstNum):
        const.tipo = TIPO_REAL


    def visita_CalcConstBool(self, const: ast.CalcConstBool):
        const.tipo = TIPO_BOOL