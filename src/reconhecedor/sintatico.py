from src.arquivo_intermediario import salvarCodigoIntermediario
from src.debug import is_debug
from src.reconhecedor.jsmachines import get_tabela_lr
from src.reconhecedor.semantico import AnalisadorSemantico
from src.reconhecedor.tabela_analise.acao import Empilhamento, Reducao, Salto, Aceite
from src.reconhecedor.tabela_simbolos.simbolo import Simbolo
from src.util import gerador_de_temporarios


class AnalisadorSintatico:

    def __init__(self, linguagem, sintatico: list[Simbolo], tabela_simbolos: list[Simbolo], recarregar_sintatico: bool):
        self.linguagem = linguagem
        self.sintatico = sintatico
        self.tabela_analise = get_tabela_lr(
            '\n'.join([f'{e.get_valor_sintatico()} -> {e.get_producao()}' for e in sintatico]),
            recarregar_sintatico,
        )
        self.fita = tabela_simbolos.get_simbolos()
        self.tabela_simbolos = tabela_simbolos

    def get_tabela_analise(self):
        return self.tabela_analise

    def verificar(self):
        # Instancia o gerador de temporários
        gerador_temp = gerador_de_temporarios()

        # Inicializa o código intermediário
        codigo_intermediario = ''

        # Instancia o analisador semantico
        semantico = AnalisadorSemantico(self.tabela_simbolos)

        # Pega a tabela de análise
        tabela = self.tabela_analise

        # Faz uma cópia da fita do objeto
        fita = self.fita

        # Caso o arquivo esteja vazio, retorna
        if len(fita) == 0:
            return {
                'sucesso': True
            }

        # Inicia a pilha apenas com estado inicial
        pilha = [0]
        index_fita = 0
        acao = None

        # Reconhecimento por pilha vazia
        while pilha:

            # Pega o estado do topo da pilha
            num_estado = int(pilha[-1])

            # Enquanto houver fita
            if index_fita < len(fita):
                # Pega o estado do início da fita
                token = fita[index_fita]
                terminal = token.get_valor_sintatico()
            else:
                token = None
                terminal = '$'

            # Pega a ação com base no número do estado do topo da pilha
            acao = tabela.get_estado(num_estado).get_acao(terminal)

            if is_debug():
                self.imprime_reconhecimento(pilha, fita, index_fita, acao)

            if isinstance(acao, Empilhamento):
                pilha.append(token)
                pilha.append(acao.get_estado())
                index_fita += 1

            elif isinstance(acao, Reducao):
                # Pega a producao numerada pela reduçãp
                producao = self.sintatico[acao.get_estado()]

                # Pega as ações semânticas do arquivo
                acoes_semanticas = producao.get_acoes()

                desempilhados = []

                # Desempilha o dobro do tamanho da produção
                for _ in range(producao.get_tamanho() * 2):
                    desempilhado = pilha.pop()
                    if isinstance(desempilhado, Simbolo):
                        desempilhados.append(desempilhado)

                # Pega o número do estado do topo da pilha
                num_estado = int(pilha[-1])

                # Insere o nome da regra no topo da pilha
                pilha.append(producao)

                # Pega a ação resultante dos últimos dois itens da pilha
                acao = tabela.get_estado(
                    num_estado
                ).get_acao(
                    f'{producao.get_valor_sintatico()}'
                )

                # Insere a ação resultante dos últimos dois itens da pilha
                pilha.append(acao.get_estado())

                if acoes_semanticas:
                    retorno = semantico.realizar_acoes(acoes_semanticas, desempilhados, producao, gerador_temp)
                    if not retorno['sucesso']:
                        return {
                            'sucesso': False,
                            'mensagem': ''.join([
                                f'*** Erro semântico encontrado na linha {fita[index_fita-1].get_linha()}. ',
                                retorno['mensagem']
                            ]),
                            'detalhe': self.get_detalhe_erro(fita, fita[index_fita-1])
                        }

            elif isinstance(acao, Salto):
                return {
                    'sucesso': False,
                    'mensagem': 'Operação de salto não resolvida.'
                }

            elif isinstance(acao, Aceite):
                salvarCodigoIntermediario(pilha[-2].get_atributo('codigo'))
                return {
                    'sucesso': True
                }

            else:
                return {
                    'sucesso': False,
                    'mensagem': ''.join([
                        f'*** Erro sintático encontrado na linha {token.get_linha()},',
                        f' token não esperado: "{token.get_valor_lexico()}".'
                    ]),
                    'detalhe': self.get_detalhe_erro(fita, token)
                }

        if is_debug():
            self.imprime_reconhecimento(pilha, fita, index_fita, acao, acoes_semanticas)

    @staticmethod
    def get_detalhe_erro(fita, token):
        # Pega todos os tokens da linha do erro
        linha = [t for t in fita if t.get_linha() == token.get_linha()]

        # Descobre a posição do item na lista
        pos = linha.index(token)

        # Calcula qual a posição da seta que indica a posição do erro
        espacamento = len(" ".join([t.get_valor_lexico() for t in linha[:pos]]))

        return '\n'.join([
            '> [...]',
            '> ',
            f'> {" ".join([t.get_valor_lexico() for t in linha])}',
            f'> {"".join([" " for _ in range(espacamento + 1)])}^',
            '> [...]',
        ])

    @staticmethod
    def imprime_reconhecimento(pilha, fita, index_fita, acao):
        espacamento = 20 - len(
            ' '.join([c.get_valor_sintatico() if isinstance(c, Simbolo) else str(c) for c in pilha])
        ) + len(
            ' '.join([f.get_valor_sintatico() for f in fita[:index_fita]])
        )

        if index_fita >= len(fita) or index_fita == 0:
            espacamento = espacamento - 1

        print(
            '$',
            ' '.join([c.get_valor_sintatico() if isinstance(c, Simbolo) else str(c) for c in pilha]),
            ''.join([' ' for _ in range(espacamento)]),
            ' '.join([f.get_valor_sintatico() or '' for f in fita[index_fita:]]),
            '$',
            f'({acao})'
        )
