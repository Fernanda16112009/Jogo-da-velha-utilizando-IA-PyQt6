import math

COMBINACOES_VITORIA = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]


def verificar_vencedor(tabuleiro):
    for a, b, c in COMBINACOES_VITORIA:
        if tabuleiro[a] != "" and tabuleiro[a] == tabuleiro[b] == tabuleiro[c]:
            return tabuleiro[a]
    return None


def tabuleiro_cheio(tabuleiro):
    return "" not in tabuleiro


def minimax(tabuleiro, profundidade, maximizando, jogador_ia, jogador_humano):
    vencedor = verificar_vencedor(tabuleiro)
    if vencedor == jogador_ia:
        return 10 - profundidade
    if vencedor == jogador_humano:
        return profundidade - 10
    if tabuleiro_cheio(tabuleiro):
        return 0 

    if maximizando:
        melhor = -math.inf
        for i in range(9):
            if tabuleiro[i] == "":
                tabuleiro[i] = jogador_ia
                melhor = max(melhor, minimax(tabuleiro, profundidade + 1, False, jogador_ia, jogador_humano))
                tabuleiro[i] = ""
        return melhor
    else:
        pior = math.inf
        for i in range(9):
            if tabuleiro[i] == "":
                tabuleiro[i] = jogador_humano
                pior = min(pior, minimax(tabuleiro, profundidade + 1, True, jogador_ia, jogador_humano))
                tabuleiro[i] = ""
        return pior


def melhor_jogada(tabuleiro, jogador_ia, jogador_humano):
    """Avalie cada posiçao livre com o Minimax e retorna a melhor jogada 
    junto com a lista de avaliações (usada para exibir o "pensamento" da IA)."""
    avaliacoes = []
    melhor_pontuacao = -math.inf
    melhor_posicao = None

    for i in range(9):
        if tabuleiro[i] == "":
            tabuleiro[i] = jogador_ia
            pontuacao = minimax(tabuleiro, 0, False, jogador_ia, jogador_humano)
            tabuleiro[i] = ""
            avaliacoes.append((i, pontuacao))
            if pontuacao > melhor_pontuacao:
                melhor_pontuacao = pontuacao
                melhor_posicao = i

    return melhor_posicao, avaliacoes

