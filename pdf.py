from fpdf import FPDF

def tratar_texto(texto):
    return texto.encode("latin-1", "replace").decode("latin-1")

texto = """
Estou desenvolvendo um projeto chamado ChessAI, que conecta uma ESP32 a uma Raspberry Pi (RASP) para criar um tabuleiro de xadrez físico interativo com sensores LDR e LEDs. Preciso que você implemente o lado da Raspberry Pi (servidor), que será responsável por processar as jogadas e interagir com a ESP32.

Abaixo está o fluxo completo de funcionamento:

1. Início da partida:
- O usuário pressiona um botão na ESP32 para iniciar o jogo.
- A ESP envia um sinal para a RASP indicando que o jogo começou.

2. Inicialização do tabuleiro:
- A RASP cria o estado inicial do tabuleiro (matriz 8x8 com 1 para posições com peças e 0 para casas vazias).
- Essa matriz é enviada em formato JSON para a ESP.

3. Verificação física:
- A ESP compara a matriz recebida com o estado real dos sensores LDR.
- Se houver erro (ex: peça ausente), o LED da casa com erro pisca em vermelho.
- Se estiver tudo certo, os LEDs percorrem o tabuleiro com cor verde como animação de confirmação.
- Ao final da animação, o tabuleiro apaga e o usuário pode fazer sua jogada.

4. Jogada do usuário:
- A ESP detecta que uma peça foi removida (mudança no LDR).
- A ESP envia à RASP um JSON com a casa de origem (ex: "from": "D2").

5. Processamento da jogada:
- A RASP calcula todas as jogadas possíveis a partir da casa informada.
- A melhor jogada é sempre a primeira da lista.
- A RASP envia à ESP um JSON com:
  "best_move": "D2D4"
  "alternatives": ["D2D3", "D2D5"]

6. Indicação das opções:
- A ESP acende LEDs nas casas de destino:
  - Melhor jogada → verde
  - Outras opções → amarelo
- O usuário deve mover a peça para uma das casas indicadas.

7. Validação da jogada do usuário:
- Se o usuário colocar a peça em casa errada:
  - A casa incorreta pisca em vermelho.
- Se colocar em uma casa válida:
  - A ESP informa a RASP com o movimento completo ("from": "D2", "to": "D4").
  - A RASP atualiza o estado do tabuleiro e calcula a jogada da IA (usando Stockfish).

8. Jogada da IA:
- A RASP envia para a ESP um JSON com:
  "from": "E7"
  "to": "E5"

9. Execução da jogada da IA:
- A ESP acende LED azul fixo na origem e azul piscante na casa de destino.
- O usuário realiza a jogada física.
- A ESP valida o movimento:
  - Se estiver incorreto, pisca vermelho na peça colocada errada.
  - Se correto, envia um OK para a RASP.

10. Novo ciclo:
- A RASP aguarda novo movimento do jogador e o ciclo se repete.

Observações:
- Toda a comunicação entre ESP e RASP será via comunicação Serial (UART), usando mensagens JSON.
- O controle das jogadas e regras do xadrez será feito usando a biblioteca python-chess + Stockfish no lado da Raspberry.

"""

pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_font("Arial", size=12)

for linha in tratar_texto(texto).split("\n"):
    pdf.multi_cell(0, 10, linha)

caminho_pdf = "./ChessAI_Fluxo_Projeto.pdf"
pdf.output(caminho_pdf)
caminho_pdf