from prettytable import PrettyTable


class Tabela:
    def __init__(self, simbolos=None):
        if simbolos is None:
            simbolos = []
        self.simbolos = simbolos

    def __str__(self):
        tabela = PrettyTable(list(['ESTADO', 'NOME', 'LINHA']))
        for s in self.simbolos:
            tabela.add_row([f'[{s.get_caracter_estado_final()}]', s.get_nome(), s.get_linha()])
        return str(tabela)

    def add_simbolo(self, simbolo):
        self.simbolos.append(simbolo)
        return self

    def get_simbolos(self):
        return self.simbolos