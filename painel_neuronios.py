from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF

RAIO_NEURONIO = 30
RAIO_NEURONIO_ATIVO = 36
COR_NEURONIO_VAZIO = QColor(60, 60, 70)
COR_LINHA_REDE = QColor(180, 180, 200, 90)


class PainelNeuronios(QWidget):
    """Desenha ad 9 posições do tabuleiro como neurônios de uma rede.
    Cada neurônio acende com uma cor entre vermelho (jogada ruim para a IA)
    e verde (jogada boa para a IA) conforme o Minimax vai avaliando as 
    posições, imitando uma rede "pensando"."""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(320, 320)
        self.pontuacoes = {}
        self.posicao_atual = None
        self.posicao_escolhida = None

    def iniciar_analise(self):
        self.pontuacoes = {}
        self.posicao_atual = None
        self.posicao_escolhida = None
        self.update()

    def adicionar_avaliacao(self, posicao, pontuacao):
        self.pontuacoes[posicao] = pontuacao
        self.posicao_atual = posicao
        self.update()

    def mostrar_escolha(self, posicao, pontuacao):
        self.posicao_escolhida = posicao
        self.posicao_atual = None
        self.update()

    def Nova_partida(self):
        self.pontuacoes = {}
        self.posicao_atual = None
        self.posicao_escolhida = None
        self.update()

    def cor_para_pontuacao(self, pontuacao):
        intensidade = max(-1.0, min(1.0, pontuacao / 10)) 
        if intensidade >= 0:
            return QColor.fromRgbF(1 - intensidade, 1, 1 - intensidade)
        intensidade = -intensidade
        return QColor.fromRgbF(1, 1 - intensidade, 1 - intensidade)

    def centro_neuronio(self, posicao):
        linha, coluna = divmod(posicao, 3)
        espaco_x = self.width() / 4
        espaco_y = self.height() / 4
        return espaco_x * (coluna + 1), espaco_y * (linha + 1)  

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        centros = [self.centro_neuronio(i) for i in range(9)]

        painter.setPen(QPen(COR_LINHA_REDE, 1))
        for i in range(9):
            for j in range(i + 1, 9):
                painter.drawLine(int(centros[i][0]), int(centros[i][1]), int(centros[j][0]), int(centros[j][1]))

        fonte = QFont()
        fonte.setPointSize(10)
        fonte.setBold(True)
        painter.setFont(fonte)

        for i in range(9):
            x, y = centros[i]
            raio = RAIO_NEURONIO_ATIVO if i == self.posicao_atual else RAIO_NEURONIO

            if i in self.pontuacoes:
                cor = self.cor_para_pontuacao(self.pontuacoes[i])
            else:
                cor = COR_NEURONIO_VAZIO

            borda = QPen(QColor(255, 215, 0) if i == self.posicao_escolhida else QColor(255,255,255))
            borda.setWidth(4 if i == self.posicao_escolhida else 1)
            painter.setPen(borda)
            painter.setBrush(cor)
            painter.drawEllipse(QRectF(x - raio, y - raio, raio * 2, raio * 2))

            texto = str(self.pontuacoes[i]) if i in self.pontuacoes else "?"
            painter.setPen(QColor(20,20,20) if cor.lightnessF() > 0.5 else QColor(255, 255, 255))
            painter.drawText(QRectF(x-raio, y-raio, raio * 2, raio * 2), Qt.AlignmentFlag.AlignCenter, texto)