# parser.py
import sys
import ply.yacc as yacc
from lexer import tokens, make_lexer
from calculadin_ast import *

precedence = (
    ("left", '+', '-'),
	("left", '*', '/')
)

# Regras gramaticais
def p_programa(p):
    "programa : INICIAR CALCULADIN ':' lista_comandos FINALIZAR CALCULADIN PONTO"
    p[0] = Programa(p[4])

def p_lista_comandos_vazia(p):
    "lista_comandos : "
    p[0] = []

def p_lista_comandos(p):
    "lista_comandos : lista_comandos comando ';'"
    p[1].append(p[2])
    p[0] = p[1]

def p_comando_funcao_input(p):
    """comando : INPUT '(' ID ')'"""
    p[0] = CmdInput(id=Id(nome=p[3]))

def p_comando_funcao_output(p):
    """comando : OUTPUT '(' ID ')'"""
    p[0] = CmdOutput(id=Id(nome=p[3]))

def p_comando_atribuicao(p):
    "comando : ID '=' expr"
    p[0] = CmdAtrib(id=Id(nome=p[1]), expr=p[3])

def p_expr_binaria(p):
    """expr : expr '+' expr
            | expr '-' expr
            | expr '*' expr
            | expr '/' expr"""
    p[0] = OpBin(op=p[2], esq=p[1], dir=p[3])

def p_expr_parenteses(p):
    """expr : '(' expr ')'"""
    p[0] = p[2]

def p_expr_num(p):
    """expr : NUM"""
    p[0] = Num(valor=p[1])

def p_expr_id(p):
    """expr : ID"""
    p[0] = Id(nome=p[1])

# Erro sintático
def p_error(tok):
    if tok is None:
        print("ERRO SINTÁTICO: fim de arquivo inesperado (EOF).")
    else:
        print(f"ERRO SINTÁTICO na linha {tok.lineno}: token inesperado ({tok.value!r})")

# Instancia o parser
def make_parser():
    return yacc.yacc()

# Para testar o parser: python3 parser.py <exemplo.calc
if __name__ == "__main__":
    data = sys.stdin.read()
    parser = make_parser()
    parser.parse(data, lexer=make_lexer())
    print()
