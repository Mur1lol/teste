# ChessAI - Sistema de Xadrez Físico Interativo

Sistema de xadrez físico que conecta uma ESP32 a uma Raspberry Pi para criar um tabuleiro interativo com sensores LDR e LEDs.

## 📋 Componentes do Sistema

### Hardware Necessário
- **ESP32** - Microcontrolador principal
- **Raspberry Pi** - Servidor de processamento
- **64 Sensores LDR** - Detecção de peças (8x8)
- **64 LEDs RGB** - Indicação visual (8x8)
- **2 Multiplexadores 16:1** - Para leitura dos sensores
- **1 Botão** - Início do jogo
- **Conexão Serial** - Comunicação entre ESP32 e Raspberry Pi

### Software
- **Arduino IDE** - Para programar a ESP32
- **Python 3.7+** - Para Raspberry Pi
- **Stockfish** - Engine de xadrez
- **Bibliotecas Python**: python-chess, pyserial

## 🚀 Instalação

### ESP32
1. Abra o Arduino IDE
2. Instale as bibliotecas necessárias:
   - ArduinoJson
   - ESP32 Board Package
3. Carregue o arquivo `esp32_chessai.ino` na ESP32

### Raspberry Pi
```bash
# Atualizar sistema
sudo apt-get update
sudo apt-get upgrade

# Instalar Stockfish
sudo apt-get install stockfish

# Instalar Python e pip
sudo apt-get install python3 python3-pip

# Instalar dependências Python
cd /path/to/project/novo
pip3 install -r requirements.txt

# Verificar instalação
python3 -c "import chess; print('python-chess OK')"
stockfish --version
```

## 🔧 Configuração

### Conexões de Hardware

#### ESP32 - Pinos dos Componentes
```
Botão de Início: GPIO 2
Multiplexador 1:
  - A0: GPIO 12
  - A1: GPIO 13  
  - A2: GPIO 14
  - A3: GPIO 15
  - EN: GPIO 16
  - SIG: GPIO 34

Multiplexador 2:
  - EN: GPIO 17
  - SIG: GPIO 34 (compartilhado)

LEDs:
  - DATA: GPIO 5
  - CLOCK: GPIO 18
```

#### Comunicação Serial
- **Baudrate**: 115200
- **Formato**: 8N1
- **Protocolo**: JSON via UART

### Configuração da Raspberry Pi

1. **Identificar porta serial**:
```bash
ls /dev/tty*
# Normalmente: /dev/ttyUSB0 ou /dev/ttyACM0
```

2. **Dar permissões**:
```bash
sudo chmod 666 /dev/ttyUSB0
# ou adicionar usuário ao grupo dialout:
sudo usermod -a -G dialout $USER
```

## 🎮 Como Usar

### 1. Iniciar o Sistema

**Raspberry Pi**:
```bash
cd /path/to/project/novo
python3 raspberry_chessai.py --port /dev/ttyUSB0
```

**ESP32**:
- Conectar e aguardar mensagem "ESP32 ChessAI iniciado!"
- Pressionar o botão para iniciar o jogo

### 2. Fluxo do Jogo

#### Passo 1: Inicialização
1. Usuário pressiona botão na ESP32
2. ESP32 envia sinal para Raspberry Pi
3. Raspberry Pi envia matriz inicial do tabuleiro
4. ESP32 valida configuração física das peças
5. Se correto: animação verde confirma início
6. Se incorreto: LEDs vermelhos indicam erros

#### Passo 2: Jogada do Usuário
1. Usuário remove peça de uma casa
2. ESP32 detecta e envia posição para Raspberry Pi
3. Raspberry Pi calcula movimentos possíveis
4. ESP32 acende LEDs:
   - 🟢 Verde: Melhor jogada
   - 🟡 Amarelo: Outras opções
5. Usuário coloca peça em uma das casas indicadas
6. ESP32 valida e confirma movimento

#### Passo 3: Jogada da IA
1. Raspberry Pi calcula movimento da IA usando Stockfish
2. ESP32 recebe e mostra movimento:
   - 🔵 Azul fixo: Casa de origem
   - 🔵 Azul piscante: Casa de destino
3. Usuário executa movimento físico da IA
4. ESP32 valida e confirma
5. Ciclo reinicia

## 📁 Estrutura dos Arquivos

```
novo/
├── esp32_chessai.ino          # Código principal da ESP32
├── raspberry_chessai.py       # Servidor principal da Raspberry Pi  
├── chessai_utils.py          # Utilitários e classes auxiliares
├── test_communication.py     # Simulador para testes
├── requirements.txt          # Dependências Python
└── README.md                # Esta documentação
```

## 🧪 Testes

### Testar Comunicação
```bash
# Executar simulador
python3 test_communication.py

# Menu de opções:
# 1. Iniciar jogo
# 2. Simular movimento do jogador  
# 3. Mostrar status do tabuleiro
# 4. Teste sequência completa
# 0. Sair
```

### Testar Componentes Individuais
```bash
# Testar utilitários
python3 chessai_utils.py

# Verificar dependências
python3 -c "import chess, serial, json; print('Todas as dependências OK')"
```

## 📡 Protocolo de Comunicação

### Formato das Mensagens
Todas as mensagens são em formato JSON:

```json
{
  "type": "tipo_da_mensagem",
  "timestamp": 1234567890,
  // dados específicos da mensagem
}
```

### Tipos de Mensagem

#### ESP32 → Raspberry Pi
```json
// Início do jogo
{"type": "game_start"}

// Origem do movimento
{"type": "player_move", "from": "E2"}

// Movimento completo
{"type": "player_move_complete", "from": "E2", "to": "E4"}

// Confirmação movimento IA
{"type": "ai_move_confirmed", "status": "OK"}
```

#### Raspberry Pi → ESP32
```json
// Matriz do tabuleiro
{"type": "board_matrix", "matrix": [1,1,1,...]}

// Opções de movimento
{
  "type": "move_options",
  "best_move": "E2E4", 
  "alternatives": ["E2E3", "D2D4"]
}

// Movimento da IA
{"type": "ai_move", "from": "E7", "to": "E5"}
```

## 🎨 Códigos de Cores dos LEDs

- 🟢 **Verde**: Melhor movimento, confirmação, animação inicial
- 🟡 **Amarelo**: Movimentos alternativos  
- 🔴 **Vermelho**: Erro, movimento inválido
- 🔵 **Azul Fixo**: Casa de origem do movimento da IA
- 🔵 **Azul Piscante**: Casa de destino do movimento da IA
- ⚫ **Apagado**: Casa normal/inativa

## ⚠️ Solução de Problemas

### Problemas Comuns

#### ESP32 não conecta
```bash
# Verificar porta serial
ls /dev/tty*

# Verificar permissões
sudo chmod 666 /dev/ttyUSB0

# Testar conexão
python3 -c "import serial; s=serial.Serial('/dev/ttyUSB0',115200); print('OK')"
```

#### Stockfish não encontrado
```bash
# Instalar Stockfish
sudo apt-get install stockfish

# Verificar instalação
which stockfish
stockfish --version
```

#### Sensores com ruído
- Ajustar threshold no código da ESP32 (linha com `currentReading < 500`)
- Verificar conexões dos multiplexadores
- Adicionar capacitores para filtrar ruído

#### LEDs não funcionam
- Verificar conexões dos pinos DATA e CLOCK
- Verificar alimentação dos LEDs
- Testar função `setLEDColor()` individualmente

### Logs e Debug

#### Raspberry Pi
```bash
# Executar com debug
python3 raspberry_chessai.py --debug

# Ver logs
tail -f chessai.log
```

#### ESP32
- Abrir Serial Monitor no Arduino IDE (115200 baud)
- Mensagens de debug aparecem no console

## 📈 Melhorias Futuras

### Hardware
- [ ] Adicionar display LCD para status
- [ ] Implementar buzzer para feedback sonoro
- [ ] Adicionar sensor de presença do usuário
- [ ] WiFi para conectividade remota

### Software
- [ ] Interface web para monitoramento
- [ ] Diferentes níveis de dificuldade da IA
- [ ] Histórico de partidas
- [ ] Modo de análise de jogadas
- [ ] Suporte a diferentes variantes de xadrez

### Funcionalidades
- [ ] Reconhecimento automático de peças
- [ ] Modo treino com exercícios
- [ ] Conexão com plataformas online (Chess.com, Lichess)
- [ ] Replay de partidas famosas

## 👥 Contribuição

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para detalhes.

## 📞 Suporte

Para dúvidas e suporte:
- Abra uma issue no GitHub
- Envie email para: [seu-email@exemplo.com]

---

**ChessAI** - Desenvolvido com ❤️ para entusiastas de xadrez e tecnologia!
