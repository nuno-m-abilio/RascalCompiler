# lexer.py
import sys
import ply.lex as lex

# Palavras reservadas
reserved = {
    'iniciar':   'INICIAR',
    'finalizar': 'FINALIZAR',
    'calculadin':'CALCULADIN',
    'input':     'INPUT',
    'output':    'OUTPUT',
}

# Tokens nomeados
tokens = (
    'NUM',
    'ID',
    'PONTO',   # .
) + tuple(reserved.values())

# Tokens literais
literals = ['=', '+', '-', '*', '/', '(', ')', ':', ';']

# Regras simples
t_PONTO = r'\.'

# Números inteiros e reais
def t_NUM(t):
    r'\d+(?:\.\d+)?'
    t.value = float(t.value)
    return t

# Identificadores válidos + palavras reservadas
def t_ID(t):
    r'[a-z][a-z0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Espaços e tabulações
t_ignore = ' \t'

# Quebra de linha e contagem de linhas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Comentários de linha (// até o fim da linha)
def t_COMMENT(t):
    r'//[^\n]*'
    pass

# Erros léxicos
def t_error(t):
    print(f"ERRO LÉXICO na linha {t.lineno}: símbolo ilegal {t.value[0]!r}")
    t.lexer.skip(1)

# Instancia o lexer
def make_lexer():
    return lex.lex()
    

# Para testar o lexer sozinho: python3 lexer.py <exemplo.calc
if __name__ == '__main__':
    data = sys.stdin.read()
    lexer = make_lexer()
    lexer.input(data)
    for tok in lexer:
        print(f'<{tok.type}, {tok.value!r}> na linha: {tok.lineno}')
