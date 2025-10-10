# Tokens do Compilador Rascal

## Descrição
Este arquivo define todos os tokens necessários para o compilador Rascal.
---

## Palavras Reservadas (Reserved Keywords)

| Token | Palavra | Descrição |
|-------|---------|-----------|
| PROGRAM | program | Declaração de programa |
| PROCEDURE | procedure | Declaração de procedimento |
| FUNCTION | function | Declaração de função |
| VAR | var | Declaração de variáveis |
| BEGIN | begin | Início de bloco de comandos |
| END | end | Fim de bloco de comandos |
| INTEGER | integer | Tipo inteiro |
| BOOLEAN | boolean | Tipo booleano |
| TRUE | true | Constante booleana verdadeira |
| FALSE | false | Constante booleana falsa |
| IF | if | Condicional |
| THEN | then | Parte then do if |
| ELSE | else | Parte else do if |
| WHILE | while | Laço while |
| DO | do | Corpo do while |
| READ | read | Leitura de entrada |
| WRITE | write | Escrita de saída |
| AND | and | Operador lógico AND |
| OR | or | Operador lógico OR |
| NOT | not | Operador lógico NOT |
| DIV | div | Divisão inteira |

---

## Símbolos Especiais (Special Symbols)

| Token | Símbolo | Descrição |
|-------|---------|-----------|
| LPAREN | ( | Parêntese esquerdo |
| RPAREN | ) | Parêntese direito |
| SEMICOLON | ; | Ponto e vírgula |
| EQ | = | Igualdade |
| NE | <> | Diferença |
| LT | < | Menor que |
| LE | <= | Menor ou igual |
| GT | > | Maior que |
| GE | >= | Maior ou igual |
| PLUS | + | Adição |
| MINUS | - | Subtração |
| TIMES | * | Multiplicação |
| ASSIGN | := | Atribuição |
| COLON | : | Dois pontos |
| COMMA | , | Vírgula |
| DOT | . | Ponto final |

---

## Tipos de Valor (Value Types)

| Token | Descrição | Exemplo |
|-------|-----------|---------|
| ID | Identificador (variável, função, procedimento) | myVar, count, x1 |
| NUMBER | Número inteiro na base decimal | 0, 42, 1000 |

---

## Notas Importantes para Implementação

### Scanner

1. **ID e NUMBER** devem ter precedência apropriada em relação às palavras reservadas
2. Identificadores começam com letra, podem conter letras, dígitos e underscore
3. Números contêm apenas dígitos (0-9)
4. Números negativos são tratados como operação `-` seguida de número
5. Operadores compostos (`<>`, `<=`, `>=`, `:=`) devem ser reconhecidos corretamente
6. Ignorar: espaços em branco, tabs, quebras de linha
7. Não há suporte a comentários em Rascal

### Parser

- Importar lista de tokens do lexer: `from lexer import tokens`
- Usar exatamente esses nomes de tokens nas regras gramaticais
- Considerar precedência de operadores ao definir regras

---

## Checklist de Implementação

### Lexer
- [ ] Todas as palavras reservadas reconhecidas
- [ ] Todos os símbolos especiais reconhecidos
- [ ] ID e NUMBER funcionando corretamente
- [ ] Teste com exemplos simples
- [ ] Arquivo pronto para importação em parser.py

### Parser
- [ ] Importação de tokens funcionando
- [ ] Definição de classes AST concluída
- [ ] Regras gramaticais implementadas
- [ ] Teste de integração com lexer