import random
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout,QPushButton,QLabel,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QButtonGroup
)
from PyQt6.QtCore import QTimer

from minimax import melhor_jogada, verificar_vencedor, tabuleiro_cheio
from painel_neuronios import PainelNeuronios

JOGADOR_HUMANO = "X"
JOGADOR_IA = "O"
ATRASO_ENTRE_ANALISES_MS = 300

#Probabilidade de a Ia ignorar a melhor jogada do minimax e escolher 
# outra posição livre aleatoriamente. Em "Minimax" ela nunca erra.
DIFICULDADES = {
    "Fácil": 0.75,
    "Mediano": 0.4,
    "Difícil": 0.15,
    "Minimax": 0.0,
}
DIFICULDADE_PADRAO = "Mediano"


class painelPensamentoIA(QWidget):
    """Mostra em tempo rela como uma rede de neurônios, as posições que a
    IA está avaliando com o Minimax e a pontuação de cada uma, antes de
    escolher a melhor jogada."""

    def __init__(self):
        super().__init__()
    
        layout = QVBoxLayout()

        self.label_titulo = QLabel("Aguardando sua jogada...")
        layout.addWidget(self.label_titulo)

        self.painel = PainelNeuronios()
        layout.addWidget(self.painel)

        self.setLayout(layout)
    
    def iniciar_analise(self):
        self.painel.iniciar_analise()
        self.label_titulo.setText("Analisando jogadas possíveis com Minimax")

    def adicionar_avaliacao(self, posicao, pontuacao):
        self.painel.adicionar_avaliacao(posicao, pontuacao)

    def mostrar_escolha(self, posicao, pontuacao):
        self.label_titulo.setText(f"Melhor jogada encontrada: posição {posicao} (pontuação {pontuacao})")
        self.painel.mostrar_escolha(posicao, pontuacao)

    def Nova_partida(self):
        self.painel.Nova_partida()
        self.label_titulo.setText("Aguardando sua jogada...")


class JanelaJogo(QWidget):    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jogo da velha atualizado")

        self.painel_ia = painelPensamentoIA()

        self.tabuleiro =[""] * 9
        self.botoes = []
        self.jogo_ativo = True
        self.dificuldade_atual = DIFICULDADE_PADRAO
        self.probabilidade_aleatoria = DIFICULDADES[DIFICULDADE_PADRAO]
        self.placarJogador = 0
        self.placarIa = 0
        self.placarEmpate = 0

        self.montar_interface()

    def montar_interface(self):
        layout_principal = QHBoxLayout()

        layout_jogo = QVBoxLayout()

        layout_jogo.addWidget(QLabel("Dificuldade da IA:"))

        layout_dificuldade = QHBoxLayout()
        self.grupo_dificuldade = QButtonGroup(self)
        self.grupo_dificuldade.setExclusive(True)
        for nome in DIFICULDADES:
            botao = QPushButton(nome)
            botao.setCheckable(True)
            botao.setChecked(nome == self.dificuldade_atual)
            botao.clicked.connect(lambda _, nome=nome: self.selecionar_dificuldade(nome))
            self.grupo_dificuldade.addButton(botao)
            layout_dificuldade.addWidget(botao)
        layout_jogo.addLayout(layout_dificuldade)

        self.label_placar = QLabel(f"Jogador: {self.placarJogador} | IA: {self.placarIa} | Empates: {self.placarEmpate}")
        layout_jogo.addWidget(self.label_placar)

        self.label_status = QLabel("Sua vez")
        layout_jogo.addWidget(self.label_status)
        grade = QGridLayout()
        for i in range(9):
            botao = QPushButton("")
            botao.setFixedSize(80, 80)
            botao.setStyleSheet("font-size: 24px;")
            botao.clicked.connect(lambda _, i=i: self.jogada_humano(i))
            self.botoes.append(botao)
            grade.addWidget(botao, i // 3, i % 3)

        layout_jogo.addLayout(grade)

        botao_Nova_partida = QPushButton("Nova partida")
        botao_Nova_partida.clicked.connect(self.Nova_partida)
        layout_jogo.addWidget(botao_Nova_partida)
        layout_jogo.addStretch()

        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.VLine)

        layout_principal.addLayout(layout_jogo)
        layout_principal.addWidget(separador)
        layout_principal.addWidget(self.painel_ia)

        self.setLayout(layout_principal)

    def jogada_humano(self, posicao):
        if not self.jogo_ativo or self.tabuleiro[posicao] != "":
            return

        self.tabuleiro[posicao] = JOGADOR_HUMANO
        self.botoes[posicao].setText(JOGADOR_HUMANO)

        if self.verificar_fim_de_jogo():
            return

        self.label_status.setText("Vez da IA")
        self.travar_tabuleiro(True)
        QTimer.singleShot(300, self.turno_ia)

    def selecionar_dificuldade(self, nome):
        self.dificuldade_atual = nome
        self.probabilidade_aleatoria = DIFICULDADES[nome]

    def escolher_jogada(self, melhor_posicao, avaliacoes):
        if  random.random() < self.probabilidade_aleatoria:
            posicoes_piores = [pos for pos, _ in avaliacoes if pos !=melhor_posicao]
            if posicoes_piores:
                return random.choice(posicoes_piores)
        return melhor_posicao

    def turno_ia(self):
        melhor_posicao, avaliacoes = melhor_jogada(self.tabuleiro, JOGADOR_IA, JOGADOR_HUMANO)
        posicao_escolhida = self.escolher_jogada(melhor_posicao, avaliacoes)
        self.painel_ia.iniciar_analise()

        for indice, (pos, pontuacao) in enumerate(avaliacoes):
            atraso = ATRASO_ENTRE_ANALISES_MS * (indice + 1)
            QTimer.singleShot(
                atraso,
                lambda pos=pos, pontuacao=pontuacao: self.painel_ia.adicionar_avaliacao(pos, pontuacao),
            )

        atraso_final =ATRASO_ENTRE_ANALISES_MS * (len(avaliacoes)+1)
        QTimer.singleShot(atraso_final, lambda: self.executar_jogada_ia(posicao_escolhida, avaliacoes))

    def executar_jogada_ia(self, posicao, avaliacoes):
        pontuacao_escolhida = dict(avaliacoes)[posicao]
        self.painel_ia.mostrar_escolha(posicao, pontuacao_escolhida)

        self.tabuleiro[posicao] = JOGADOR_IA
        self.botoes[posicao].setText(JOGADOR_IA)

        if self.verificar_fim_de_jogo():
            return

        self.label_status.setText("Sua vez")
        self.travar_tabuleiro(False)

    def verificar_fim_de_jogo(self):
        vencedor = verificar_vencedor(self.tabuleiro)
        if vencedor == JOGADOR_HUMANO :
            self.jogo_ativo = False
            texto = "Você venceu!" 
            self.placarJogador = self.placarJogador + 1
            self.label_placar.setText(f"Jogador: {self.placarJogador} | IA: {self.placarIa} | Empates: {self.placarEmpate}")
            QMessageBox.information(self, "Fim de jogo", texto)
            return True

        if vencedor == JOGADOR_IA :
            self.jogo_ativo = False
            texto = "Ia venceu!" 
            self.placarIa = self.placarIa + 1
            self.label_placar.setText(f"Jogador: {self.placarJogador} | IA: {self.placarIa} | Empates: {self.placarEmpate}")
            QMessageBox.information(self, "Fim de jogo", texto)
            return True
        
        if tabuleiro_cheio(self.tabuleiro):
            self.jogo_ativo = False
            self.placarEmpate = self.placarEmpate + 1
            self.label_placar.setText(f"Jogador: {self.placarJogador} | IA: {self.placarIa} | Empates: {self.placarEmpate}")
            QMessageBox.information(self, "Fim de jogo", "Empate!")
            return True

        return False
          
    def travar_tabuleiro(self, travado):
        for i, botao in enumerate(self.botoes):
            if self.tabuleiro[i] == "":
                botao.setEnabled(not travado)

    def Nova_partida(self):
        self.tabuleiro = [""] * 9
        self.jogo_ativo = True
        self.label_status.setText("Sua vez")
        for botao in self.botoes:
            botao.setText("")
            botao.setEnabled(True)
        self.painel_ia.Nova_partida()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    janela = JanelaJogo()
    janela.show()

    sys.exit(app.exec())
