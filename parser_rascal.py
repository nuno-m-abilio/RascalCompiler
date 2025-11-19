import sys
from dataclasses import dataclass
import ply.yacc as yacc
from lexer import tokens, make_lexer

# ============================================================================
# CLASSES PARA A AST (Abstract Syntax Tree) - VERSÃO SIMPLIFICADA
# ============================================================================

@dataclass
class No:
    """Classe base para todos os nós da AST"""
    pass

@dataclass
class Programa(No):
    nome: str
    bloco: object

@dataclass
class OpBin(No):
    op: str
    esq: object
    dir: object

@dataclass
class OpUn(No):
    op: str
    expr: object

@dataclass
class Num(No):
    valor: int

@dataclass
class Id(No):
    nome: str

@dataclass
class Chamada(No):
    nome: str
    args: list

# ============================================================================
# FUNÇÃO PARA GERAR STRING DA AST
# ============================================================================

def gera_string_ast(n) -> str:
    """Gera representação em string da AST"""
    if isinstance(n, Programa):
        return f"(program {n.nome} {gera_string_ast(n.bloco)})"
    elif isinstance(n, OpBin):
        return f"({n.op} {gera_string_ast(n.esq)} {gera_string_ast(n.dir)})"
    elif isinstance(n, OpUn):
        return f"({n.op} {gera_string_ast(n.expr)})"
    elif isinstance(n, Num):
        return f"{n.valor}"
    elif isinstance(n, Id):
        return f"{n.nome}"
    elif isinstance(n, Chamada):
        args_str = " ".join(gera_string_ast(a) for a in n.args)
        return f"({n.nome} {args_str})" if n.args else f"{n.nome}"
    elif isinstance(n, list):
        return " ".join(gera_string_ast(item) for item in n)
    elif isinstance(n, tuple):
        nome, *conteudo = n
        conteudo_str = " ".join(gera_string_ast(c) for c in conteudo)
        return f"({nome} {conteudo_str})" if conteudo else f"{nome}"
    else:
        return str(n) if n is not None else ""

# ============================================================================
# REGRAS GRAMATICAIS
# ============================================================================

# Precedência e associatividade dos operadores
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', '=', 'DIFERENTE', '<', 'MENOR_IGUAL', '>', 'MAIOR_IGUAL'),
    ('left', '+', '-'),
    ('left', '*', 'DIV'),
    ('right', 'NOT', 'UMINUS'),
)

# ==================== PROGRAMA ====================

def p_programa(p):
    '''programa : PROGRAM ID ';' bloco '.' '''
    p[0] = Programa(p[2], p[4])

# ==================== BLOCO ====================

def p_bloco(p):
    '''bloco : secao_declaracao_variaveis secao_declaracao_subrotinas comando_composto
             | secao_declaracao_variaveis comando_composto
             | secao_declaracao_subrotinas comando_composto
             | comando_composto'''
    if len(p) == 4:
        p[0] = ('bloco', p[1], p[2], p[3])
    elif len(p) == 3:
        p[0] = ('bloco', p[1], p[2])
    else:
        p[0] = ('bloco', p[1])

# ==================== DECLARAÇÃO DE VARIÁVEIS ====================

def p_secao_declaracao_variaveis(p):
    '''secao_declaracao_variaveis : VAR declaracao_variaveis_lista'''
    p[0] = ('var', p[2])

def p_declaracao_variaveis_lista(p):
    '''declaracao_variaveis_lista : declaracao_variaveis ';'
                                  | declaracao_variaveis_lista declaracao_variaveis ';' '''
    if len(p) == 3:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_declaracao_variaveis(p):
    '''declaracao_variaveis : lista_identificadores ':' tipo'''
    p[0] = ('decl', p[1], p[3])

def p_lista_identificadores(p):
    '''lista_identificadores : ID
                            | lista_identificadores ',' ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_tipo(p):
    '''tipo : BOOLEAN
            | INTEGER'''
    p[0] = p[1]

# ==================== DECLARAÇÃO DE SUBROTINAS ====================

def p_secao_declaracao_subrotinas(p):
    '''secao_declaracao_subrotinas : declaracao_subrotina_lista'''
    p[0] = ('subrotinas', p[1])

def p_declaracao_subrotina_lista(p):
    '''declaracao_subrotina_lista : declaracao_subrotina ';'
                                  | declaracao_subrotina_lista declaracao_subrotina ';' '''
    if len(p) == 3:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_declaracao_subrotina(p):
    '''declaracao_subrotina : declaracao_procedimento
                           | declaracao_funcao'''
    p[0] = p[1]

def p_declaracao_procedimento(p):
    '''declaracao_procedimento : PROCEDURE ID parametros_formais ';' bloco_subrot
                              | PROCEDURE ID ';' bloco_subrot'''
    if len(p) == 6:
        p[0] = ('procedure', p[2], p[3], p[5])
    else:
        p[0] = ('procedure', p[2], p[4])

def p_declaracao_funcao(p):
    '''declaracao_funcao : FUNCTION ID parametros_formais ':' tipo ';' bloco_subrot
                        | FUNCTION ID ':' tipo ';' bloco_subrot'''
    if len(p) == 8:
        p[0] = ('function', p[2], p[3], p[5], p[7])
    else:
        p[0] = ('function', p[2], p[4], p[6])

def p_bloco_subrot(p):
    '''bloco_subrot : secao_declaracao_variaveis comando_composto
                   | comando_composto'''
    if len(p) == 3:
        p[0] = ('bloco_subrot', p[1], p[2])
    else:
        p[0] = ('bloco_subrot', p[1])

def p_parametros_formais(p):
    '''parametros_formais : '(' declaracao_parametros_lista ')' '''
    p[0] = ('params', p[2])

def p_declaracao_parametros_lista(p):
    '''declaracao_parametros_lista : declaracao_parametros
                                   | declaracao_parametros_lista ';' declaracao_parametros'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_declaracao_parametros(p):
    '''declaracao_parametros : lista_identificadores ':' tipo'''
    p[0] = ('param', p[1], p[3])

# ==================== COMANDOS ====================

def p_comando_composto(p):
    '''comando_composto : BEGIN comando_lista END'''
    p[0] = ('begin', p[2])

def p_comando_lista(p):
    '''comando_lista : comando
                    | comando_lista ';' comando'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_comando(p):
    '''comando : atribuicao
              | chamada_procedimento
              | condicional
              | repeticao
              | leitura
              | escrita
              | comando_composto'''
    p[0] = p[1]

def p_atribuicao(p):
    '''atribuicao : ID ATRIB expressao'''
    p[0] = (':=', p[1], p[3])

def p_chamada_procedimento(p):
    '''chamada_procedimento : ID '(' lista_expressoes ')'
                           | ID'''
    if len(p) == 5:
        p[0] = Chamada(p[1], p[3])
    else:
        p[0] = Chamada(p[1], [])

def p_condicional(p):
    '''condicional : IF expressao THEN comando ELSE comando
                  | IF expressao THEN comando'''
    if len(p) == 7:
        p[0] = ('if', p[2], p[4], p[6])
    else:
        p[0] = ('if', p[2], p[4])

def p_repeticao(p):
    '''repeticao : WHILE expressao DO comando'''
    p[0] = ('while', p[2], p[4])

def p_leitura(p):
    '''leitura : READ '(' lista_identificadores ')' '''
    p[0] = ('read', p[3])

def p_escrita(p):
    '''escrita : WRITE '(' lista_expressoes ')' '''
    p[0] = ('write', p[3])

def p_lista_expressoes(p):
    '''lista_expressoes : expressao
                       | lista_expressoes ',' expressao'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# ==================== EXPRESSÕES ====================

def p_expressao(p):
    '''expressao : expressao_simples
                | expressao_simples relacao expressao_simples'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = OpBin(p[2], p[1], p[3])

def p_relacao(p):
    '''relacao : '='
              | DIFERENTE
              | '<'
              | MENOR_IGUAL
              | '>'
              | MAIOR_IGUAL'''
    p[0] = p[1]

def p_expressao_simples(p):
    '''expressao_simples : termo
                        | expressao_simples '+' termo
                        | expressao_simples '-' termo
                        | expressao_simples OR termo'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = OpBin(p[2], p[1], p[3])

def p_termo(p):
    '''termo : fator
            | termo '*' fator
            | termo DIV fator
            | termo AND fator'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = OpBin(p[2], p[1], p[3])

def p_fator(p):
    '''fator : variavel
            | numero
            | logico
            | chamada_funcao
            | '(' expressao ')'
            | NOT fator
            | '-' fator %prec UMINUS'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = OpUn(p[1], p[2])
    else:
        p[0] = p[2]

def p_variavel(p):
    '''variavel : ID'''
    p[0] = Id(p[1])

def p_numero(p):
    '''numero : NUM'''
    p[0] = Num(p[1])

def p_logico(p):
    '''logico : FALSE
             | TRUE'''
    p[0] = p[1]

def p_chamada_funcao(p):
    '''chamada_funcao : ID '(' lista_expressoes ')' '''
    p[0] = Chamada(p[1], p[3])

# ==================== TRATAMENTO DE ERROS ====================

def p_error(p):
    if p:
        print(f"Erro sintático no token '{p.value}' (tipo: {p.type}) na linha {p.lineno}")
    else:
        print("Erro sintático: final inesperado do arquivo")

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def make_parser():
    """Cria e retorna o parser"""
    return yacc.yacc()

def parse_file(filename):
    """Lê um arquivo e faz o parsing"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = f.read()
    
    lexer = make_lexer()
    parser = make_parser()
    
    try:
        result = parser.parse(data, lexer=lexer)
        return result
    except Exception as e:
        print(f"Erro durante o parsing: {e}")
        return None

# ============================================================================
# MAIN - Para testar o parser
# ============================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python parser.py <arquivo>")
        sys.exit(1)
    
    filename = sys.argv[1]
    ast = parse_file(filename)
    
    if ast:
        print("\n=== AST GERADA ===")
        print(gera_string_ast(ast))
        print("\n=== PARSING CONCLUÍDO COM SUCESSO ===")
    else:
        print("\n=== FALHA NO PARSING ===")
        sys.exit(1)