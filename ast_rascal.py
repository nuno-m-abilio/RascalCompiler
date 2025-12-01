from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union

# Classes Bases

class No:
    '''
    Classe base para todos os nós da AST.
    '''
    pass

class Declaracao(No):
    '''
    Classe base para declarações (variáveis, funções, procedimentos).
    '''
    pass

class Comando(No):
    '''
    Classe base para comandos (instruções que não retornam valor).
    '''
    pass

class Expressao(No):
    '''
    Classe base para expressões (geram valor e possuem tipo).
    '''
    # Atributo para armazenar o tipo inferido durante a análise semântica
    tipo_inferido: Optional[str] = None 

# Estrutura do programa e blocos

@dataclass
class Programa(No):
    '''
    Representa o programa inteiro.
    Gramática: program <id>; <bloco>.
    '''
    id: str
    bloco: Bloco

@dataclass
class Bloco(No):
    '''
    Representa o bloco principal do programa.
    Gramática: [vars] [subrotinas] <comando_composto>
    '''
    decl_vars: List[DeclVariaveis]
    decl_subrotinas: List[DeclSubrotina]
    comando_composto: ComandoComposto

@dataclass
class BlocoSubrotina(No):
    '''
    Representa o bloco interno de uma função ou procedimento.
    Diferença: Não permite declarar novas subrotinas dentro dele (conforme gramática).
    Gramática: [vars] <comando_composto>
    '''
    decl_vars: List[DeclVariaveis]
    comando_composto: ComandoComposto

# Declarações

@dataclass
class DeclVariaveis(Declaracao):
    '''
    Declaração de uma lista de variáveis de um mesmo tipo.
    Ex: x, y, z : integer;
    '''
    ids: List[str]
    tipo: str

@dataclass
class Parametro(Declaracao):
    '''
    Representa um grupo de parâmetros formais: (a, b: integer)
    '''
    ids: List[str]
    tipo: str
    # Rascal é pass-by-value por padrão, mas se houvesse 'var', marcaríamos aqui.

class DeclSubrotina(Declaracao):
    '''
    Classe pai para Funções e Procedimentos.
    '''
    pass

@dataclass
class DeclProcedimento(DeclSubrotina):
    '''
    Ex: procedure Soma(a: integer); ...
    '''
    id: str
    parametros: List[Parametro]
    bloco: BlocoSubrotina

@dataclass
class DeclFuncao(DeclSubrotina):
    '''
    Ex: function Soma(a: integer): integer; ...
    '''
    id: str
    parametros: List[Parametro]
    tipo_retorno: str
    bloco: BlocoSubrotina

# Comandos

@dataclass
class ComandoComposto(Comando):
    '''
    begin ... end
    '''
    comandos: List[Comando]

@dataclass
class CmdAtribuicao(Comando):
    '''
    id := expressao
    Obs: Em Pascal/Rascal, atribuição é um comando, não expressão.
    '''
    id: str
    expressao: Expressao

@dataclass
class CmdChamadaProcedimento(Comando):
    '''
    Ex: LerDados(x);
    Diferente de função, este não retorna valor e é usado isoladamente.
    '''
    id: str
    argumentos: List[Expressao]

@dataclass
class CmdIf(Comando):
    '''
    if <cond> then <cmd> [else <cmd>]
    '''
    condicao: Expressao
    cmd_then: Comando
    cmd_else: Optional[Comando] # Pode ser None se não houver else

@dataclass
class CmdWhile(Comando):
    '''
    while <cond> do <cmd>
    '''
    condicao: Expressao
    cmd_do: Comando

@dataclass
class CmdRead(Comando):
    '''
    read(x, y) - Recebe lista de Identificadores (strings)
    '''
    ids: List[str] 

@dataclass
class CmdWrite(Comando):
    '''
    write(x+1, y) - Recebe lista de Expressões
    '''
    expressoes: List[Expressao]

# Expressões

@dataclass
class ExpBinaria(Expressao):
    '''
    Operações com dois operandos.
    Ops: +, -, *, div, and, or, =, <>, <, >, <=, >=
    '''
    esq: Expressao
    op: str
    dir: Expressao

@dataclass
class ExpUnaria(Expressao):
    '''
    Operações com um operando.
    Ops: - (menos unário), not
    '''
    op: str
    expressao: Expressao

@dataclass
class ExpVariavel(Expressao):
    '''
    Uso de uma variável numa expressão: x + 1
    '''
    id: str

@dataclass
class ExpChamadaFuncao(Expressao):
    '''
    Uso de função numa expressão: y := Soma(1, 2) + 5;
    Retorna um valor.
    '''
    id: str
    argumentos: List[Expressao]

@dataclass
class ExpNumero(Expressao):
    '''
    Valor literal inteiro: 42
    '''
    valor: int

@dataclass
class ExpBooleano(Expressao):
    '''
    Valor literal booleano: true, false
    '''
    valor: bool