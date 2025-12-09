import ply.lex as lex

# Dicionário de palavras reservadas mapeadas para o tipo de token
reserved = {
    'program': 'PROGRAM',
    'procedure': 'PROCEDURE',
    'function': 'FUNCTION',
    'var': 'VAR',
    'begin': 'BEGIN',
    'end': 'END',
    'integer': 'INTEGER',
    'boolean': 'BOOLEAN',
    'false': 'FALSE',
    'true': 'TRUE', 
    'while': 'WHILE',
    'do': 'DO',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'read': 'READ',
    'write': 'WRITE',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'div': 'DIV',
}

literals = ['(', ')', ';', '=', '+', '-', '*', ':', ',', '.', '<', '>']

# Lista de tokens (palavras reservadas + outros tokens)
tokens = [
    'ID',               # Identificador
    'NUM',              # Números inteiros
    'DIFERENTE',        # <>
    'MENOR_IGUAL',      # <=
    'MAIOR_IGUAL',      # >=
    'ATRIB',            # :=    
] + list(reserved.values())

# Regras para tokens que precisam de ordem específica
def t_DIFERENTE(t):
    r'<>'
    return t

def t_MENOR_IGUAL(t):
    r'<='
    return t

def t_MAIOR_IGUAL(t):
    r'>='
    return t

def t_ATRIB(t):
    r':='
    return t

# Identificadores válidos + palavras reservadas
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    # Verifica se a palavra é reservada
    t.type = reserved.get(t.value, 'ID')
    return t

# Números inteiros
def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Espaços e tabulações
t_ignore = ' \t'

# Quebra de linha e contagem de linhas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Erros léxicos
def t_error(t):
    print(f"Erro léxico: caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.tem_erro = True
    t.lexer.skip(1)

def make_lexer():
    lexer = lex.lex()
    lexer.tem_erro = False
    return lexer
