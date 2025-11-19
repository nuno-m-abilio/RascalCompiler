import sys
from lexer_cldin2 import make_lexer
from parser_cldin2 import make_parser
from sem_cldin import VerificadorSemantico
from printer_cldin2 import ImpressoraAST 
# from codegen_cldin2 import GeradorCodigoMEPA

def imprimir_modo_uso():
    print("Modo de uso: python calculadin2.py <flag> < arquivo_entrada", file=sys.stderr)
    print("Flags:", file=sys.stderr)
    print("  -l : Executa apenas a análise léxica.", file=sys.stderr)
    print("  -p : Executa as análises léxica e sintática.", file=sys.stderr)
    print("  -s : Executa as análises léxica, sintática e semântica.", file=sys.stderr)
    print("  -sp: Executa a análise semântica e imprime a AST (se não houver erros).", file=sys.stderr)
    print("  -g : Executa o pipeline completo e gera o código MEPA.", file=sys.stderr)

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

    # Analisador léxico
    lexer = make_lexer()
    
    # Execução para -l
    if flag == '-l':
        lexer.input(data)
        while True:
            tok = lexer.token()
            if not tok:
                break
        
        if lexer.tem_erro:
            print("ERRO: Erros léxicos encontrados.", file=sys.stderr)
            sys.exit(1)
        else:
            print("SUCESSO: Análise léxica concluída.")
        return 

    # Analisador sintático
    parser = make_parser() 
    ast_root = parser.parse(data, lexer=lexer)

    if parser.tem_erro or lexer.tem_erro:
        print("ERRO: Erros léxicos ou sintáticos encontrados.", file=sys.stderr)
        sys.exit(1)
    
    # Execução para -p
    if flag == '-p':
        print("SUCESSO: Análises léxica e sintática concluídas.")
        return 
    
    # Analisador semântico (ainda não existe)
    # verificador = VerificadorSemantico()
    # verificador.visita(ast_root) 
    
    # if verificador.tem_erro:
    #     print("ERRO: Erros semânticos encontrados:", file=sys.stderr)
    #     for erro in verificador.erros:
    #         print(f"- {erro}", file=sys.stderr)
    #     sys.exit(1)
    
    # Execução para -s
    # if flag == '-s':
    #     print("SUCESSO: Análises léxica, sintática e semântica concluídas.")
    #     return 

    # Execução para -sp (imprime a AST - ainda não existe)
    # if flag == '-sp':
    #     print("SUCESSO: Análises léxica, sintática e semântica concluídas.")
    #     print("\n--- AST Anotada ---")
    #     impressora = ImpressoraAST()
    #     impressora.visita(ast_root)
    #     return 

    # Execução para -g (gera código MEPA - ainda não existe) 
    # if flag == '-g':
    #     gerador = GeradorCodigoMEPA()
    #     gerador.visita(ast_root)

    #     if gerador.tem_erro:
    #         print("ERRO: Erros de geração encontrados:", file=sys.stderr)
    #         for erro in gerador.erros:
    #             print(f"- {erro}", file=sys.stderr)
    #         sys.exit(1)
    
    #     for instrucao in gerador.codigo:
    #         print(instrucao)
    #     return 

    # Flag inválida
    print(f"ERRO: Flag '{flag}' desconhecida.", file=sys.stderr)
    imprimir_modo_uso()
    sys.exit(1)

if __name__ == "__main__":
    main()