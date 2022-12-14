import os
from arquivo import lerEntrada
from linguagem.automato.automato import Automato
from linguagem.linguagem import Linguagem


def main():
    os.system('cls')
    linguagem = Linguagem()
    linguagem.setGramaticas(lerEntrada('../arquivos/entrada.txt'))
    print(linguagem, end="\n\n=============\n\n")
    linguagem.setGramaticas([linguagem.unificarGramaticas()])
    print(linguagem, end="\n\n=============\n\n")
    linguagem.gerarAutomato()
    print(linguagem.getAutomato(), end="\n\n=============\n\n")


if __name__ == '__main__':
    main()
