from __future__ import annotations
from typing import List, Dict, Optional
import ast_rascal as ast
from defs_rascal import (Visitador, Simbolo, Categoria, Tipo, TIPO_INT, TIPO_BOOL, get_tipo_by_name)

class TabelaSimbolos:
    def __init__(self) -> None:
        self.escopos: List[Dict[str, Simbolo]] = [dict()]
        self.nivel_atual = 0

    def abre_escopo(self):
        self.escopos.append({})
        self.nivel_atual += 1

    def fecha_escopo(self):
        if len(self.escopos) > 1:
            self.escopos.pop()
            self.nivel_atual -= 1

    def instala(self, s: Simbolo) -> str | None:
        atual = self.escopos[-1]
        if s.nome in atual:
            return f"Identificador '{s.nome}' já declarado neste escopo."
        
        # s.deslocamento = self.deslocamento_atual
        s.nivel_lexico = self.nivel_atual
        atual[s.nome] = s
        return None

    def busca(self, nome: str) -> Simbolo | None:
        # Busca do escopo mais interno para o mais externo
        for tabela in reversed(self.escopos):
            if nome in tabela:
                return tabela[nome]
        return None

class VerificadorSemantico(Visitador):
    def __init__(self) -> None:
        self.ts = TabelaSimbolos()
        self.erros: List[str] = []
        self.tem_erro: bool = False
        # Para saber qual função estamos analisando (para validar retorno)
        self.funcao_atual: Optional[Simbolo] = None 
        self.encontrou_retorno: bool = False

    def _erro(self, msg: str):
        self.erros.append(msg)
        self.tem_erro = True

    # Programa e Blocos

    def visita_Programa(self, no: ast.Programa):
        # Instala o nome do programa
        simbolo_prog = Simbolo(nome=no.id, categoria=Categoria.PROGRAM)
        self.ts.instala(simbolo_prog)
        
        # Visita o bloco principal
        self.visita(no.bloco)

    def visita_Bloco(self, no: ast.Bloco):
        # Bloco Principal: Declarações e Comandos no escopo Global
        self.visita(no.decl_vars)
        self.visita(no.decl_subrotinas)
        self.visita(no.comando_composto)

    def visita_BlocoSubrotina(self, no: ast.BlocoSubrotina):
        # Bloco Interno: Já estamos dentro de um escopo criado pela DeclProcedimento/Funcao
        self.visita(no.decl_vars)
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
            if erro:
                self._erro(erro)

    def visita_DeclProcedimento(self, no: ast.DeclProcedimento):
        # 1. Instalar procedimento no escopo ATUAL (Pai)
        simbolo_proc = Simbolo(nome=no.id, categoria=Categoria.PROC)
        
        # Coletar tipos dos parâmetros para assinatura
        if no.parametros:
            for param in no.parametros:
                tipo_param = get_tipo_by_name(param.tipo)
                # Cada ID na lista conta como um parâmetro desse tipo
                for _ in param.ids:
                    simbolo_proc.params_tipos.append(tipo_param)
        
        erro = self.ts.instala(simbolo_proc)
        if erro: self._erro(erro)

        # 2. Abrir escopo da subrotina
        self.ts.abre_escopo()

        # 3. Instalar parâmetros como variáveis locais
        if no.parametros:
            for param in no.parametros:
                tipo_param = get_tipo_by_name(param.tipo)
                for pid in param.ids:
                    s_param = Simbolo(nome=pid, categoria=Categoria.PARAM, tipo=tipo_param)
                    self.ts.instala(s_param)

        # 4. Visitar o corpo
        self.visita(no.bloco)

        # 5. Fechar escopo
        self.ts.fecha_escopo()

    def visita_DeclFuncao(self, no: ast.DeclFuncao):
        # 1. Instalar função no escopo ATUAL (Pai)
        tipo_retorno = get_tipo_by_name(no.tipo_retorno)
        simbolo_func = Simbolo(nome=no.id, categoria=Categoria.FUNC, tipo=tipo_retorno)
        
        if no.parametros:
            for param in no.parametros:
                tipo_param = get_tipo_by_name(param.tipo)
                for _ in param.ids:
                    simbolo_func.params_tipos.append(tipo_param)
        
        erro = self.ts.instala(simbolo_func)
        if erro: self._erro(erro)

        # 2. Abrir escopo e definir contexto atual
        self.ts.abre_escopo()
        anterior = self.funcao_atual
        self.funcao_atual = simbolo_func # Marca que estamos dentro desta função

        # 3. Instalar parâmetros
        if no.parametros:
            for param in no.parametros:
                tipo_param = get_tipo_by_name(param.tipo)
                for pid in param.ids:
                    s_param = Simbolo(nome=pid, categoria=Categoria.PARAM, tipo=tipo_param)
                    self.ts.instala(s_param)

        self.encontrou_retorno = False # Reseta para a nova função

        # Verifica se houve retorno
        if not self.encontrou_retorno:
            self._erro(f"Função '{no.id}' deve retornar um valor, mas não retornou.")        

        # 4. Visitar corpo
        self.visita(no.bloco)

        # 5. Restaurar contexto
        self.funcao_atual = anterior
        self.ts.fecha_escopo()

    # Comandos

    def visita_ComandoComposto(self, no: ast.ComandoComposto):
        for cmd in no.comandos:
            self.visita(cmd)

    def visita_CmdAtribuicao(self, no: ast.CmdAtribuicao):
        # Analisa o lado direito (Expressão)
        self.visita(no.expressao)
        
        # Analisa o lado esquerdo (ID)
        simbolo = self.ts.busca(no.id)

        if simbolo is None:
            # Pode ser atribuição de retorno de função (NomeDaFuncao := Valor)
            if self.funcao_atual and no.id == self.funcao_atual.nome:
                simbolo = self.funcao_atual
                self.encontrou_retorno = True
            else:
                self._erro(f"Identificador '{no.id}' não declarado.")
                return

        # Verificações de Tipo
        if simbolo.categoria not in (Categoria.VAR, Categoria.PARAM, Categoria.FUNC):
            self._erro(f"Não é possível atribuir valor a '{no.id}' (Categoria: {simbolo.categoria}).")
            return

        if no.expressao.tipo_inferido is not None:
            if simbolo.tipo != no.expressao.tipo_inferido:
                self._erro(f"Atribuição incompatível para '{no.id}': esperado {simbolo.tipo}, recebido {no.expressao.tipo_inferido}.")

    def visita_CmdIf(self, no: ast.CmdIf):
        self.visita(no.condicao)
        if no.condicao.tipo_inferido != TIPO_BOOL:
            self._erro(f"Condição do 'if' deve ser boolean, recebeu {no.condicao.tipo_inferido}.")
        
        self.visita(no.cmd_then)
        if no.cmd_else:
            self.visita(no.cmd_else)

    def visita_CmdWhile(self, no: ast.CmdWhile):
        self.visita(no.condicao)
        if no.condicao.tipo_inferido != TIPO_BOOL:
            self._erro(f"Condição do 'while' deve ser boolean, recebeu {no.condicao.tipo_inferido}.")
        self.visita(no.cmd_do)

    def visita_CmdRead(self, no: ast.CmdRead):
        for var_id in no.ids:
            simbolo = self.ts.busca(var_id)
            if simbolo is None:
                self._erro(f"Variável '{var_id}' não declarada no read.")
            elif simbolo.categoria not in (Categoria.VAR, Categoria.PARAM):
                self._erro(f"Identificador '{var_id}' no read não é uma variável.")

    def visita_CmdWrite(self, no: ast.CmdWrite):
        for expr in no.expressoes:
            self.visita(expr)

    def visita_CmdChamadaProcedimento(self, no: ast.CmdChamadaProcedimento):
        simbolo = self.ts.busca(no.id)
        if simbolo is None:
            self._erro(f"Procedimento '{no.id}' não declarado.")
            return
        
        if simbolo.categoria != Categoria.PROC:
            self._erro(f"'{no.id}' não é um procedimento.")
            return

        # Verifica argumentos
        self._verifica_argumentos(simbolo, no.argumentos)

    # Expressões

    def visita_ExpBinaria(self, no: ast.ExpBinaria):
        self.visita(no.esq)
        self.visita(no.dir)
        
        te = no.esq.tipo_inferido
        td = no.dir.tipo_inferido

        if te is None or td is None:
            return # Erro já reportado antes

        # Aritméticos: +, -, *, div (INT, INT -> INT)
        if no.op in ('+', '-', '*', 'div'):
            if te == TIPO_INT and td == TIPO_INT:
                no.tipo_inferido = TIPO_INT
            else:
                self._erro(f"Operador '{no.op}' requer inteiros. Recebeu {te} e {td}.")
                no.tipo_inferido = TIPO_INT # Assume int para evitar erros em cascata

        # Relacionais: =, <>, <, >, <=, >= (INT, INT -> BOOL)
        elif no.op in ('=', '<>', '<', '>', '<=', '>='):
            if te == td:
                no.tipo_inferido = TIPO_BOOL
            else:
                self._erro(f"Comparação entre tipos diferentes: {te} e {td}.")
                no.tipo_inferido = TIPO_BOOL

        # Lógicos: and, or (BOOL, BOOL -> BOOL)
        elif no.op in ('and', 'or'):
            if te == TIPO_BOOL and td == TIPO_BOOL:
                no.tipo_inferido = TIPO_BOOL
            else:
                self._erro(f"Operador '{no.op}' requer booleanos. Recebeu {te} e {td}.")
                no.tipo_inferido = TIPO_BOOL

    def visita_ExpUnaria(self, no: ast.ExpUnaria):
        self.visita(no.expressao)
        t = no.expressao.tipo_inferido

        if no.op == '-':
            if t == TIPO_INT:
                no.tipo_inferido = TIPO_INT
            else:
                self._erro(f"Operador unário '-' requer integer. Recebeu {t}.")
        elif no.op == 'not':
            if t == TIPO_BOOL:
                no.tipo_inferido = TIPO_BOOL
            else:
                self._erro(f"Operador 'not' requer boolean. Recebeu {t}.")

    def visita_ExpVariavel(self, no: ast.ExpVariavel):
        simbolo = self.ts.busca(no.id)
        if simbolo is None:
            self._erro(f"Variável '{no.id}' não declarada.")
            return
        
        no.tipo_inferido = simbolo.tipo

    def visita_ExpNumero(self, no: ast.ExpNumero):
        no.tipo_inferido = TIPO_INT

    def visita_ExpBooleano(self, no: ast.ExpBooleano):
        no.tipo_inferido = TIPO_BOOL

    def visita_ExpChamadaFuncao(self, no: ast.ExpChamadaFuncao):
        simbolo = self.ts.busca(no.id)
        if simbolo is None:
            self._erro(f"Função '{no.id}' não declarada.")
            return
        
        if simbolo.categoria != Categoria.FUNC:
            self._erro(f"'{no.id}' não é uma função.")
            return
            
        self._verifica_argumentos(simbolo, no.argumentos)
        no.tipo_inferido = simbolo.tipo

    # Métodos Auxiliares

    def _verifica_argumentos(self, simbolo_func: Simbolo, argumentos_ast: List[ast.Expressao]):
        # Verifica contagem
        qtd_esperada = len(simbolo_func.params_tipos)
        qtd_recebida = len(argumentos_ast) if argumentos_ast else 0

        if qtd_esperada != qtd_recebida:
            self._erro(f"'{simbolo_func.nome}' espera {qtd_esperada} argumentos, recebeu {qtd_recebida}.")
            return

        # Verifica tipos individualmente
        if argumentos_ast:
            for i, arg_expr in enumerate(argumentos_ast):
                self.visita(arg_expr) # Resolve o tipo da expressão
                tipo_esperado = simbolo_func.params_tipos[i]
                tipo_recebido = arg_expr.tipo_inferido

                if tipo_recebido and tipo_esperado != tipo_recebido:
                    self._erro(f"Argumento {i+1} de '{simbolo_func.nome}': esperado {tipo_esperado}, recebido {tipo_recebido}.")