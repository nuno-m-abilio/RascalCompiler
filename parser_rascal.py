import sys
import ply.yacc as yacc
from lexer_rascal import tokens
import ast_rascal as ast

# Variável global para o parser
parser = None

# Precedência e Associatividade

# Define a prioridade dos operadores para evitar ambiguidade.
# A ordem é da menor para a maior precedência.
precedence = (
    ('nonassoc', '=', 'DIFERENTE', '<', 'MENOR_IGUAL', '>', 'MAIOR_IGUAL', 'ATRIB'), 
    ('left', '+', '-', 'OR'),                                      
    ('left', '*', 'DIV', 'AND'),                                   
    ('right', 'NOT', 'UMINUS'),                                    
    ('nonassoc', 'THEN'),                                          
    ('nonassoc', 'ELSE'),
)

# Regras do Programa e Blocos

def p_programa(p):
    '''
    programa : PROGRAM ID ';' bloco '.'
    '''
    p[0] = ast.Programa(id=p[2], bloco=p[4])

def p_bloco(p):
    '''
    bloco : secao_decl_vars secao_decl_subrotinas comando_composto
    '''
    # p[1] = lista de variáveis (ou vazio)
    # p[2] = lista de subrotinas (ou vazio)
    # p[3] = comando composto (obrigatório)
    p[0] = ast.Bloco(decl_vars=p[1], decl_subrotinas=p[2], comando_composto=p[3])

# Declaração de Váriaveis

def p_secao_decl_vars(p):
    '''
    secao_decl_vars : VAR lista_decl_vars
                    | empty
    '''
    if len(p) == 3:
        p[0] = p[2] # Retorna a lista de declarações
    else:
        p[0] = []   # Retorna lista vazia se não houver 'var'

def p_lista_decl_vars(p):
    '''
    lista_decl_vars : lista_decl_vars decl_var ';'
                    | decl_var ';'
    '''
    if len(p) == 4:
        p[1].append(p[2]) # Incrementa na lista caso ela já exista
        p[0] = p[1]
    else:
        p[0] = [p[1]] # Cria a lista de vars

def p_decl_var(p):
    '''
    decl_var : lista_ids ':' tipo
    '''
    p[0] = ast.DeclVariaveis(ids=p[1], tipo=p[3])

def p_lista_ids(p):
    '''
    lista_ids : lista_ids ',' ID
              | ID
    '''
    if len(p) == 4:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = [p[1]]

def p_tipo(p):
    '''
    tipo : INTEGER
         | BOOLEAN
    '''
    p[0] = p[1]

# Declaração de subrotinas

def p_secao_decl_subrotinas(p):
    '''
    secao_decl_subrotinas : secao_decl_subrotinas decl_procedimento ';'
                          | secao_decl_subrotinas decl_funcao ';'
                          | empty
    '''
    if len(p) == 4:
        p[1].append(p[2])
        p[0] = p[1]
    elif len(p) == 2:
        p[0] = [] # Inicializa lista vazia

# --- Procedimento ---
def p_decl_procedimento(p):
    '''
    decl_procedimento : PROCEDURE ID parametros ';' bloco_subrot
    '''
    p[0] = ast.DeclProcedimento(id=p[2], parametros=p[3], bloco=p[5])

# --- Função ---
def p_decl_funcao(p):
    '''
    decl_funcao : FUNCTION ID parametros ':' tipo ';' bloco_subrot
    '''
    p[0] = ast.DeclFuncao(id=p[2], parametros=p[3], tipo_retorno=p[5], bloco=p[7])

# Parâmetros Formais (na declaração)
def p_parametros(p):
    '''
    parametros : '(' lista_decl_params ')'
               | empty
    '''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = []

def p_lista_decl_params(p):
    '''
    lista_decl_params : lista_decl_params ';' decl_param
                      | decl_param
    '''
    if len(p) == 4:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = [p[1]]

def p_decl_param(p):
    '''
    decl_param : lista_ids ':' tipo
    '''
    p[0] = ast.Parametro(ids=p[1], tipo=p[3])

# Bloco interno de subrotinas (não permite novas subrotinas dentro)
def p_bloco_subrot(p):
    '''
    bloco_subrot : secao_decl_vars comando_composto
    '''
    p[0] = ast.BlocoSubrotina(decl_vars=p[1], comando_composto=p[2])

# Comandos

def p_comando_composto(p):
    '''
    comando_composto : BEGIN lista_comandos END
    '''
    p[0] = ast.ComandoComposto(comandos=p[2])

def p_lista_comandos(p):
    '''
    lista_comandos : lista_comandos ';' comando
                   | comando
    '''
    if len(p) == 4:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = [p[1]]

def p_comando(p):
    '''
    comando : atribuicao
            | chamada_procedimento
            | comando_composto
            | condicional
            | repeticao
            | leitura
            | escrita
    '''
    p[0] = p[1]

def p_atribuicao(p):
    '''
    atribuicao : ID ATRIB expressao
    '''
    p[0] = ast.CmdAtribuicao(id=p[1], expressao=p[3])

def p_chamada_procedimento(p):
    '''
    chamada_procedimento : ID '(' lista_exprs ')'
                         | ID
    ''' 
    # Pascal permite chamar sem parenteses se nao tiver args
    args = []
    if len(p) == 5:
        args = p[3]
    p[0] = ast.CmdChamadaProcedimento(id=p[1], argumentos=args)

def p_condicional(p):
    '''
    condicional : IF expressao THEN comando
                | IF expressao THEN comando ELSE comando
    '''
    if len(p) == 5:
        p[0] = ast.CmdIf(condicao=p[2], cmd_then=p[4], cmd_else=None)
    else:
        p[0] = ast.CmdIf(condicao=p[2], cmd_then=p[4], cmd_else=p[6])

def p_repeticao(p):
    '''
    repeticao : WHILE expressao DO comando
    '''
    p[0] = ast.CmdWhile(condicao=p[2], cmd_do=p[4])

def p_leitura(p):
    '''
    leitura : READ '(' lista_ids ')'
    '''
    p[0] = ast.CmdRead(ids=p[3])

def p_escrita(p):
    '''
    escrita : WRITE '(' lista_exprs ')'
    '''
    p[0] = ast.CmdWrite(expressoes=p[3])

# Expressões

def p_lista_exprs(p):
    '''
    lista_exprs : lista_exprs ',' expressao
                | expressao
    '''
    if len(p) == 4:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = [p[1]]

def p_expressao_binaria(p):
    '''
    expressao : expressao '+' expressao
              | expressao '-' expressao
              | expressao '*' expressao
              | expressao DIV expressao
              | expressao AND expressao
              | expressao OR expressao
              | expressao '=' expressao
              | expressao DIFERENTE expressao
              | expressao '<' expressao
              | expressao '>' expressao
              | expressao MENOR_IGUAL expressao
              | expressao MAIOR_IGUAL expressao
    '''
    p[0] = ast.ExpBinaria(esq=p[1], op=p[2], dir=p[3])

def p_expressao_unaria(p):
    '''
    expressao : NOT expressao
              | '-' expressao %prec UMINUS
    '''
    p[0] = ast.ExpUnaria(op=p[1], expressao=p[2])

def p_expressao_grupo(p):
    '''
    expressao : '(' expressao ')'
    '''
    p[0] = p[2]

def p_expressao_atomos(p):
    '''
    expressao : NUM
              | TRUE
              | FALSE
              | ID
              | chamada_funcao
    '''
    if isinstance(p[1], int):
        p[0] = ast.ExpNumero(valor=p[1])
    elif p[1] == 'true':
        p[0] = ast.ExpBooleano(valor=True)
    elif p[1] == 'false':
        p[0] = ast.ExpBooleano(valor=False)
    elif isinstance(p[1], ast.ExpChamadaFuncao):
        p[0] = p[1]
    else:
        # É um ID (variável simples)
        p[0] = ast.ExpVariavel(id=p[1])

def p_chamada_funcao(p):
    '''
    chamada_funcao : ID '(' lista_exprs ')'
    '''
    p[0] = ast.ExpChamadaFuncao(id=p[1], argumentos=p[3])

# Tratamento de Erros

def p_empty(p):
    '''
    empty :
    '''
    pass

def p_error(p):
    global parser
    if p:
        print(f"Erro sintático: Token inesperado '{p.value}' (tipo {p.type}) na linha {p.lineno}", file=sys.stderr)
    else:
        print("Erro sintático: Fim de arquivo (EOF) inesperado.", file=sys.stderr)
    parser.tem_erro = True

def make_parser():
    global parser
    parser = yacc.yacc()
    parser.tem_erro = False
    return parser