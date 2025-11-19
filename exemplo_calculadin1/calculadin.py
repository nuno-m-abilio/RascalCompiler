# tascal.py
import sys

# Importa os módulos de cada fase
from lexer import make_lexer
from parser import make_parser
from calculadin_ast import Impressora_AST


def imprimir_modo_uso():
    print("Modo de uso: python main.py <flag> < arquivo_entrada", file=sys.stderr)
    print("Flags:", file=sys.stderr)
    print("  -l : Executa apenas a análise léxica.", file=sys.stderr)
    print("  -p : Executa as análises léxica e sintática (constrói a AST).", file=sys.stderr)

def main():
    if len(sys.argv) != 2:
        imprimir_modo_uso()
        sys.exit(1)
        
    flag = sys.argv[1]
    
    try:
        data = sys.stdin.read()
    except Exception as e:
        print(f"Erro ao ler stdin: {e}", file=sys.stderr)
        sys.exit(1)

    lexer = make_lexer()
    
    if flag == '-l':
        lexer.input(data)
        while True:
            tok = lexer.token()
            if not tok:
                break
        return 

    parser = make_parser() 
    raiz_ast = parser.parse(data, lexer=lexer)
    if raiz_ast is None:
        print("ERRO: Falha na análise sintática. AST não foi construída.", file=sys.stderr)
        sys.exit(1)
    
    if flag == '-p':
        print("SUCESSO: Análises léxica e sintática concluídas (AST construída).")
        impressora = Impressora_AST()
        impressora.visita(raiz_ast)
        print()
        return 
    
    print(f"ERRO: Flag '{flag}' desconhecExprIda ou não implementada.", file=sys.stderr)
    imprimir_modo_uso()
    sys.exit(1)

if __name__ == "__main__":
    main()