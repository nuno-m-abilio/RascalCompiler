from __future__ import annotations
from typing import List, Dict, Optional
import ast_rascal as ast
from defs_rascal import (Visitador, Simbolo, Categoria, TIPO_INT, TIPO_BOOL, get_tipo_by_name)

class TabelaSimbolos:
    def __init__(self) -> None:
        self.escopos: List[Dict[str, Simbolo]] = [dict()]
        self.nivel_atual = 0
        # Pilha para controlar o deslocamento de variáveis em cada escopo
        self.deslocamentos: List[int] = [0] 

    def abre_escopo(self):
        self.escopos.append({})
        self.deslocamentos.append(0) # Novo escopo começa com deslocamento 0
        self.nivel_atual += 1

    def fecha_escopo(self):
        if len(self.escopos) > 1:
            self.escopos.pop()
            self.deslocamentos.pop()
            self.nivel_atual -= 1

    def instala(self, s: Simbolo) -> str | None:
        atual = self.escopos[-1]
        if s.nome in atual:
            return f"Identificador '{s.nome}' já declarado neste escopo."
        
        s.nivel_lexico = self.nivel_atual
        
        # Se for variável ou parâmetro, define o endereço de memória (offset)
        if s.categoria in (Categoria.VAR, Categoria.PARAM):
            s.deslocamento = self.deslocamentos[-1]
            self.deslocamentos[-1] += 1
            
        atual[s.nome] = s
        return None

    def busca(self, nome: str) -> Simbolo | None:
        for tabela in reversed(self.escopos):
            if nome in tabela:
                return tabela[nome]
        return None
    
    # Retorna quantas variáveis foram alocadas no escopo atual
    def total_vars_escopo_atual(self) -> int:
        return self.deslocamentos[-1]

class VerificadorSemantico(Visitador):
    def __init__(self) -> None:
        self.ts = TabelaSimbolos()
        self.erros: List[str] = []
        self.tem_erro: bool = False
        self.funcao_atual: Optional[Simbolo] = None 
        self.encontrou_retorno: bool = False

    def _erro(self, msg: str):
        self.erros.append(msg)
        self.tem_erro = True

    # Programa e Blocos

    def visita_Programa(self, no: ast.Programa):
        simbolo_prog = Simbolo(nome=no.id, categoria=Categoria.PROGRAM)
        self.ts.instala(simbolo_prog)
        self.visita(no.bloco)
        # Salva o total de variáveis globais para o AMEM do programa principal
        no.total_vars_globais = self.ts.total_vars_escopo_atual()

    def visita_Bloco(self, no: ast.Bloco):
        self.visita(no.decl_vars)
        self.visita(no.decl_subrotinas)
        self.visita(no.comando_composto)

    # Declarações

    def visita_DeclVariaveis(self, no: ast.DeclVariaveis):
        tipo_real = get_tipo_by_name(no.tipo)
        if tipo_real is None:
            self._erro(f"Tipo desconhecido '{no.tipo}'.")
            return

        for ident in no.ids:
            simbolo = Simbolo(nome=ident, categoria=Categoria.VAR, tipo=tipo_real)
            erro = self.ts.instala(simbolo)
            if erro: self._erro(erro)

    def visita_DeclProcedimento(self, no: ast.DeclProcedimento):
        simbolo_proc = Simbolo(nome=no.id, categoria=Categoria.PROC)
        
        if no.parametros:
            for param in no.parametros:
                tipo = get_tipo_by_name(param.tipo)
                for _ in param.ids:
                    simbolo_proc.params_tipos.append(tipo)
        
        if erro := self.ts.instala(simbolo_proc): self._erro(erro)

        self.ts.abre_escopo()
        
        if no.parametros:
            
            offset_atual = -5
            
            for param in no.parametros:
                t = get_tipo_by_name(param.tipo)
                for pid in param.ids:
                    s_param = Simbolo(nome=pid, categoria=Categoria.PARAM, tipo=t)
                    # Forçamos o deslocamento manual (bypass no instala)
                    s_param.nivel_lexico = self.ts.nivel_atual
                    s_param.deslocamento = offset_atual
                    
                    # Instala manualmente no dicionário para não usar o contador de locais
                    if pid in self.ts.escopos[-1]:
                         self._erro(f"Parâmetro '{pid}' repetido.")
                    else:
                         self.ts.escopos[-1][pid] = s_param
                    
                    offset_atual -= 1 

        # Visita variáveis locais e corpo
        self.visita(no.bloco)
        
        no.total_vars_locais = self.ts.total_vars_escopo_atual()
        no.simbolo = simbolo_proc 
        
        self.ts.fecha_escopo()

    def visita_DeclFuncao(self, no: ast.DeclFuncao):
        tipo_ret = get_tipo_by_name(no.tipo_retorno)
        simbolo_func = Simbolo(nome=no.id, categoria=Categoria.FUNC, tipo=tipo_ret)
        
        if no.parametros:
            for param in no.parametros:
                t = get_tipo_by_name(param.tipo)
                for _ in param.ids:
                    simbolo_func.params_tipos.append(t)
        
        if erro := self.ts.instala(simbolo_func): self._erro(erro)

        self.ts.abre_escopo()
        ant_func = self.funcao_atual
        self.funcao_atual = simbolo_func
        
        total_params = 0
        if no.parametros:
            total_params = sum(len(p.ids) for p in no.parametros)

        simbolo_func.deslocamento = -5 - total_params
        
        if no.parametros:
            offset_atual = -5
            for param in no.parametros:
                t = get_tipo_by_name(param.tipo)
                for pid in param.ids:
                    s_param = Simbolo(nome=pid, categoria=Categoria.PARAM, tipo=t)
                    s_param.nivel_lexico = self.ts.nivel_atual
                    s_param.deslocamento = offset_atual
                    
                    if pid in self.ts.escopos[-1]:
                         self._erro(f"Parâmetro '{pid}' repetido.")
                    else:
                         self.ts.escopos[-1][pid] = s_param
                    
                    offset_atual -= 1

        # Reset flag de retorno
        ant_ret = self.encontrou_retorno
        self.encontrou_retorno = False

        self.visita(no.bloco)
        
        if not self.encontrou_retorno:
            self._erro(f"Função '{no.id}' sem retorno.")

        no.total_vars_locais = self.ts.total_vars_escopo_atual()
        no.simbolo = simbolo_func

        self.encontrou_retorno = ant_ret
        self.funcao_atual = ant_func
        self.ts.fecha_escopo()

    def visita_BlocoSubrotina(self, no: ast.BlocoSubrotina):
        self.visita(no.decl_vars)
        self.visita(no.comando_composto)

    # Comandos e Expressões (Anotando Símbolos na AST)

    def visita_CmdAtribuicao(self, no: ast.CmdAtribuicao):
        self.visita(no.expressao)
        
        simbolo = None
        
        # Verifica se estamos atribuindo ao nome da função atual (Retorno)
        if self.funcao_atual and no.id == self.funcao_atual.nome:
            simbolo = self.funcao_atual
            self.encontrou_retorno = True
            # Se for retorno, o tipo esperado é o tipo de retorno da função
            tipo_esperado = simbolo.tipo
        else:
            # Se não for, busca na tabela normalmente
            simbolo = self.ts.busca(no.id)
            if simbolo is None:
                self._erro(f"Identificador '{no.id}' não declarado.")
                return
            tipo_esperado = simbolo.tipo

        # Anota o símbolo no nó
        no.simbolo = simbolo
        
        # Verifica se o identificador é válido para atribuição
        if simbolo.categoria not in (Categoria.VAR, Categoria.PARAM, Categoria.FUNC):
            self._erro(f"Atribuição inválida a '{no.id}' (Categoria: {simbolo.categoria}).")
            return
            
        # Verificação de tipos
        if no.expressao.tipo_inferido and tipo_esperado != no.expressao.tipo_inferido:
            self._erro(f"Tipo incompatível em '{no.id}': esperado {tipo_esperado}, recebeu {no.expressao.tipo_inferido}.")

    def visita_ExpVariavel(self, no: ast.ExpVariavel):
        simbolo = self.ts.busca(no.id)
        if simbolo:
            no.tipo_inferido = simbolo.tipo
            no.simbolo = simbolo 
        else:
            self._erro(f"Variável '{no.id}' não declarada.")

    def visita_CmdRead(self, no: ast.CmdRead):
        no.simbolos = [] 
        for var_id in no.ids:
            simbolo = self.ts.busca(var_id)
            if simbolo:
                no.simbolos.append(simbolo)
                if simbolo.categoria not in (Categoria.VAR, Categoria.PARAM):
                    self._erro(f"'{var_id}' não é variável.")
            else:
                self._erro(f"Variável '{var_id}' não declarada.")

    def visita_CmdChamadaProcedimento(self, no: ast.CmdChamadaProcedimento):
        simbolo = self.ts.busca(no.id)
        if simbolo and simbolo.categoria == Categoria.PROC:
            no.simbolo = simbolo # Anotação
            self._verifica_argumentos(simbolo, no.argumentos)
        else:
            self._erro(f"Procedimento '{no.id}' inválido.")

    def visita_ExpChamadaFuncao(self, no: ast.ExpChamadaFuncao):
        simbolo = self.ts.busca(no.id)
        if simbolo and simbolo.categoria == Categoria.FUNC:
            no.tipo_inferido = simbolo.tipo
            no.simbolo = simbolo # Anotação
            self._verifica_argumentos(simbolo, no.argumentos)
        else:
            self._erro(f"Função '{no.id}' inválida.")
    
    def visita_CmdIf(self, no: ast.CmdIf):
        self.visita(no.condicao)

        if no.condicao.tipo_inferido != TIPO_BOOL:
            self._erro(f"Condição do 'if' deve ser do tipo boolean, mas recebeu {no.condicao.tipo_inferido}.")

        self.visita(no.cmd_then)
        if no.cmd_else: self.visita(no.cmd_else)

    def visita_CmdWhile(self, no: ast.CmdWhile):
        self.visita(no.condicao)

        if no.condicao.tipo_inferido != TIPO_BOOL:
            self._erro(f"Condição do 'while' deve ser do tipo boolean, mas recebeu {no.condicao.tipo_inferido}.")

        self.visita(no.cmd_do)

    def visita_CmdWrite(self, no: ast.CmdWrite):
        for expr in no.expressoes:
            self.visita(expr)
    
    def visita_ComandoComposto(self, no: ast.ComandoComposto):
        for cmd in no.comandos:
            self.visita(cmd)

    def visita_ExpBinaria(self, no: ast.ExpBinaria):
        self.visita(no.esq)
        self.visita(no.dir)
        if no.op in ('<', '>', '=', '<=', '>=', '<>', 'and', 'or'):
            no.tipo_inferido = TIPO_BOOL
        else:
            no.tipo_inferido = TIPO_INT

    def visita_ExpUnaria(self, no: ast.ExpUnaria):
        self.visita(no.expressao)
        t = no.expressao.tipo_inferido

        if t is None:
            no.tipo_inferido = None
            return

        if no.op == '-':
            if t != TIPO_INT:
                self._erro(f"Operador unário '-' requer integer. Recebeu {t}.")
                no.tipo_inferido = TIPO_INT # Assume INT para evitar erros em cascata
            else:
                no.tipo_inferido = TIPO_INT

        elif no.op == 'not':
            if t != TIPO_BOOL:
                self._erro(f"Operador 'not' requer boolean. Recebeu {t}.")
                no.tipo_inferido = TIPO_BOOL # Assume BOOL para evitar erros em cascata
            else:
                no.tipo_inferido = TIPO_BOOL
        
    def visita_ExpNumero(self, no): no.tipo_inferido = TIPO_INT

    def visita_ExpBooleano(self, no): no.tipo_inferido = TIPO_BOOL

    def _verifica_argumentos(self, simbolo, args):
        expected = len(simbolo.params_tipos)
        given = len(args) if args else 0
        if expected != given:
            self._erro(f"'{simbolo.nome}' espera {expected} args, recebeu {given}.")
        if args:
            for i, arg in enumerate(args):
                self.visita(arg)
                tipo_recebido = arg.tipo_inferido
                tipo_esperado = simbolo.params_tipos[i]

                if tipo_recebido and tipo_recebido != tipo_esperado:
                    self._erro(f"Argumento {i+1} de '{simbolo.nome}': esperado {tipo_esperado}, recebido {tipo_recebido}.")