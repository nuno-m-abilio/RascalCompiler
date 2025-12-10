# Compilador Rascal

Compilador para a linguagem Rascal (Reduced Pascal) desenvolvido em Python, que realiza análise léxica, sintática, semântica e gera código intermediário para a máquina MEPA.

## Requisitos

- Python 3.7+
- PLY (Python Lex-Yacc)

## Instalação

Instale a biblioteca PLY:
```bash
pip install ply
```

## Uso

O compilador aceita diferentes flags para executar etapas específicas da compilação:
```bash
python rascal.py <flag> < arquivo_entrada
```

### Flags disponíveis

- `-l` : Executa apenas a análise léxica (scanner)
- `-p` : Executa análises léxica e sintática (parser)
- `-pp` : Executa análises léxica e sintática e imprime a AST
- `-s` : Executa análises léxica, sintática e semântica
- `-g` : Compilação completa (gera código MEPA)

### Exemplos
```bash
# Análise léxica apenas
python rascal.py -l < programa.ras

# Análise sintática
python rascal.py -p < programa.ras

# Visualizar AST
python rascal.py -pp < programa.ras

# Análise semântica
python rascal.py -s < programa.ras

# Gerar código MEPA
python rascal.py -g < programa.ras
```

## Estrutura do Projeto

- `rascal.py` - Programa principal
- `lexer_rascal.py` - Analisador léxico
- `parser_rascal.py` - Analisador sintático
- `ast_rascal.py` - Definição da AST
- `sem_rascal.py` - Analisador semântico
- `codegen_rascal.py` - Gerador de código MEPA
- `defs_rascal.py` - Definições auxiliares (tipos, símbolos, visitador)
- `printer_rascal.py` - Impressora da AST

## Autores

Desenvolvido como trabalho prático da disciplina de Compiladores.