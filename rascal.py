import sys

# Importa o analisador léxico que você já tem
from lexer_rascal import make_lexer
from parser_rascal import make_parser
from printer_rascal import ImpressoraAST

# --- IMPORTAÇÕES FUTURAS (Descomente à medida que implementar) ---
# from sem_rascal import VerificadorSemantico 
# from codegen_rascal import GeradorCodigoMEPA

def imprimir_modo_uso():
    print("Modo de uso: python rascal.py <flag> < arquivo_entrada", file=sys.stderr)
    print("Exemplo: python rascal.py -l < testes/exemplo1.ras", file=sys.stderr)
    print("Flags disponíveis:", file=sys.stderr)
    print("  -l : Executa apenas a análise léxica (scanner).", file=sys.stderr)
    print("  -p : Executa as análises léxica e sintática (parser).", file=sys.stderr)
    print("  -pp: Executa as análises léxica e sintática e imprime a AST.", file=sys.stderr)
    print("  -s : Executa as análises léxica, sintática e semântica.", file=sys.stderr)
    print("  -g : Compilação completa (gera código MEPA).", file=sys.stderr)

def main():
    # Verifica se passou a flag
    if len(sys.argv) != 2:
        imprimir_modo_uso()
        sys.exit(1)
        
    flag = sys.argv[1]
    
    # Lê o código fonte da entrada padrão (pipe ou redirecionamento <)
    try:
        data = sys.stdin.read()
    except Exception as e:
        print(f"Erro ao ler entrada padrão: {e}", file=sys.stderr)
        sys.exit(1)

    # ============================================================
    # 1. ANÁLISE LÉXICA
    # ============================================================
    lexer = make_lexer()
    
    # Adicionamos um atributo para rastrear erros, caso o lexer não tenha nativamente
    if not hasattr(lexer, 'tem_erro'):
        lexer.tem_erro = False

    # Se a flag for -l, apenas imprime os tokens e para
    if flag == '-l':
        print(f"Iniciando análise léxica...")
        lexer.input(data)
        while True:
            tok = lexer.token()
            if not tok:
                break
            print(f"<{tok.type}, {tok.value}> Linha: {tok.lineno}")
        
        if lexer.tem_erro:
            print("ERRO: Erros léxicos encontrados.", file=sys.stderr)
            sys.exit(1)
        else:
            print("SUCESSO: Análise léxica concluída.")
        return 

    # ============================================================
    # 2. ANÁLISE SINTÁTICA (PARSER)
    # ============================================================
    
    print("Iniciando análise sintática...")
    parser = make_parser() 
    ast_root = parser.parse(data, lexer=lexer)

    if parser.tem_erro or lexer.tem_erro:
        print("ERRO: Erros léxicos ou sintáticos encontrados.", file=sys.stderr)
        sys.exit(1)
    
    # Se a flag for -p, para aqui
    if flag == '-p':
        print("SUCESSO: Análises léxica e sintática concluídas.")
        print("AST gerada com sucesso (em memória).")
        return 
    
    # ============================================================
    # 3. ANÁLISE SEMÂNTICA
    # ============================================================
    # TODO: Descomentar quando implementar a semântica
    
    # print("Iniciando análise semântica...")
    # verificador = VerificadorSemantico()
    # verificador.visita(ast_root) 
    
    # if verificador.tem_erro:
    #     print("ERRO: Erros semânticos encontrados:", file=sys.stderr)
    #     for erro in verificador.erros:
    #         print(f"- {erro}", file=sys.stderr)
    #     sys.exit(1)
    
    # Se a flag for -s, para aqui
    if flag == '-s':
        print("SUCESSO: Análises léxica, sintática e semântica concluídas.")
        return 

    # Se a flag for -sp, imprime a AST
    if flag == '-pp':
        print("SUCESSO: Análises até sintática concluídas.")
        print("\n--- Árvore Sintática Abstrata (AST) ---")
        impressora = ImpressoraAST()
        impressora.visita(ast_root)
        return 

    # ============================================================
    # 4. GERAÇÃO DE CÓDIGO
    # ============================================================
    # TODO: Descomentar quando implementar o gerador de código
    
    if flag == '-g':
        print("Iniciando geração de código...")
        # gerador = GeradorCodigoMEPA()
        # gerador.visita(ast_root)

        # if gerador.tem_erro:
        #     print("ERRO: Falha na geração de código.", file=sys.stderr)
        #     sys.exit(1)
    
        # O código gerado geralmente vai para um arquivo ou stdout
        # for instrucao in gerador.codigo:
        #     print(instrucao)
        return 

    # Flag não reconhecida
    print(f"ERRO: Flag '{flag}' desconhecida.", file=sys.stderr)
    imprimir_modo_uso()
    sys.exit(1)

if __name__ == "__main__":
    main()