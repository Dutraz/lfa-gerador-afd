from src.debug import is_debug
from src.reconhecedor.jsmachines import get_tabela_lr
from src.reconhecedor.semantico import AnalisadorSemantico
from src.reconhecedor.tabela_analise.acao import Empilhamento, Reducao, Salto, Aceite


class AnalisadorSintatico:

    def __init__(self, linguagem, sintatico: list[dict], fita, recarregar_sintatico: bool):
        self.linguagem = linguagem
        self.sintatico = sintatico
        self.tabela_analise = get_tabela_lr(
            '\n'.join([f'{e["simbolo"]} -> {e["producao"]}' for e in sintatico]),
            recarregar_sintatico,
        )
        self.fita = fita

    def get_tabela_analise(self):
        return self.tabela_analise

    def verificar(self):
        # Instancia o analisador semantico
        semantico = AnalisadorSemantico(self.fita)

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
                acoes_semanticas = producao.get('acoes')

                if acoes_semanticas:
                    semantico.realizar_acoes(acoes_semanticas)

                # Desempilha o dobro do tamanho da produção
                for _ in range(producao['tamanho'] * 2):
                    pilha.pop()

                # Pega o número do estado do topo da pilha
                num_estado = int(pilha[-1])

                # Insere o nome da regra no topo da pilha
                pilha.append(producao['simbolo'])

                # Pega a ação resultante dos últimos dois itens da pilha
                acao = tabela.get_estado(
                    num_estado
                ).get_acao(
                    f'{producao["simbolo"]}'
                )

                # Insere a ação resultante dos últimos dois itens da pilha
                pilha.append(acao.get_estado())

            elif isinstance(acao, Salto):
                return {
                    'sucesso': False,
                    'mensagem': 'Operação de salto não resolvida.'
                }

            elif isinstance(acao, Aceite):
                return {
                    'sucesso': True
                }

            else:
                return {
                    'sucesso': False,
                    'mensagem': f'*** Erro sintático encontrado na linha {token.get_linha()}, token não esperado: "{token.get_valor_lexico()}".',
                    'detalhe': self.get_detalhe_erro(fita, token)
                }

        if is_debug():
            self.imprime_reconhecimento(pilha, fita, index_fita, acao)

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
        espacamento = 30 - len(
            ' '.join([str(c) for c in pilha])
        ) + len(
            ' '.join([f.get_valor_lexico() for f in fita[:index_fita]])
        )

        if index_fita >= len(fita) or index_fita == 0:
            espacamento = espacamento - 1

        print(
            '$',
            ' '.join([str(c) for c in pilha]),
            ''.join([' ' for _ in range(espacamento)]),
            ' '.join([f.get_valor_lexico() for f in fita[index_fita:]]),
            '$',
            f'({acao})'
        )
