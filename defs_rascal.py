import ast_rascal as ast

# Visitor genérico (Baseado no defs_cldin2.py)
class Visitador:
    def visita(self, no):
        if no is None:
            return
        
        # Se for uma lista (ex: lista de comandos), visita cada item
        if isinstance(no, list):
            for item in no:
                self.visita(item)
            return

        # Descobre o nome da classe do nó (ex: Programa, CmdIf)
        # e tenta chamar o método visita_NomeDaClasse
        nome_metodo = f'visita_{type(no).__name__}'
        visitor = getattr(self, nome_metodo, self.visita_padrao)
        return visitor(no)

    def visita_padrao(self, no):
        raise NotImplementedError(f"O método {type(no).__name__} não foi implementado no printer.")