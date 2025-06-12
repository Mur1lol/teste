# ChessAI - ESP32

Esta pasta contém o código para programar a ESP32 que controla o tabuleiro físico.

## 📁 Arquivos

- `esp32_chessai.ino` - Código principal da ESP32
- `README.md` - Esta documentação

## 🔧 Hardware Necessário

### Componentes:
- **ESP32** (qualquer modelo com WiFi)
- **64 Sensores de Efeito Hall** (8x8 para o tabuleiro)
- **64 LEDs RGB** (WS2812B ou similar)
- **2 Multiplexadores 16:1** (CD74HC4067 ou similar)
- **1 Botão** (para iniciar o jogo)
- **Peças de xadrez com ímãs** (ou ímãs pequenos colados)

### Conexões:

#### Botão de Início:
- **GPIO 2** → Botão (com pull-up interno)

#### Multiplexadores (para 64 sensores):
```
Multiplexador 1 (sensores 0-31):
- A0 → GPIO 12
- A1 → GPIO 13  
- A2 → GPIO 14
- A3 → GPIO 15
- EN → GPIO 16
- SIG → GPIO 34 (ADC)

Multiplexador 2 (sensores 32-63):
- A0 → GPIO 12 (compartilhado)
- A1 → GPIO 13 (compartilhado)
- A2 → GPIO 14 (compartilhado)
- A3 → GPIO 15 (compartilhado)
- EN → GPIO 17
- SIG → GPIO 34 (compartilhado)
```

#### LEDs (WS2812B):
- **GPIO 5** → DATA (DIN dos LEDs)
- **GPIO 18** → CLOCK (opcional, dependendo do tipo)

#### Comunicação Serial:
- **TX/RX** → Conexão USB com Raspberry Pi

## 🚀 Instalação

### 1. Arduino IDE:
1. Instale o [Arduino IDE](https://www.arduino.cc/en/software)
2. Adicione suporte à ESP32:
   - File → Preferences
   - Additional Board Manager URLs: `https://dl.espressif.com/dl/package_esp32_index.json`
   - Tools → Board → Boards Manager → Procurar "ESP32" → Instalar

### 2. Bibliotecas Necessárias:
```
Tools → Manage Libraries → Instalar:
- ArduinoJson (by Benoit Blanchon)
- FastLED (para LEDs WS2812B) - opcional
```

### 3. Configuração da Placa:
```
Tools → Board → ESP32 Arduino → ESP32 Dev Module
Tools → Port → Selecionar porta COM da ESP32
Tools → Upload Speed → 115200
```

## ⚙️ Configuração do Hardware

### Sensores de Efeito Hall:
- **Tipo**: A3144, A3144E, ou similar
- **Alimentação**: 3.3V da ESP32
- **Saída**: Analógica (0-3.3V)
- **Threshold**: 2000 (configurável no código)

### Layout do Tabuleiro:
```
   A  B  C  D  E  F  G  H
8  0  1  2  3  4  5  6  7   ← Sensores 0-7
7  8  9  10 11 12 13 14 15  ← Sensores 8-15
6  16 17 18 19 20 21 22 23  ← Sensores 16-23
5  24 25 26 27 28 29 30 31  ← Sensores 24-31
4  32 33 34 35 36 37 38 39  ← Sensores 32-39
3  40 41 42 43 44 45 46 47  ← Sensores 40-47
2  48 49 50 51 52 53 54 55  ← Sensores 48-55
1  56 57 58 59 60 61 62 63  ← Sensores 56-63
```

### LEDs:
- **Verde**: Melhor movimento
- **Amarelo**: Movimentos alternativos
- **Azul Fixo**: Origem do movimento da IA
- **Azul Piscante**: Destino do movimento da IA
- **Vermelho**: Erro/posição inválida

## 📝 Programação

### 1. Carregar o Código:
1. Abra `esp32_chessai.ino` no Arduino IDE
2. Conecte a ESP32 via USB
3. Selecione a porta correta
4. Clique em Upload (→)

### 2. Monitor Serial:
- Tools → Serial Monitor
- Baudrate: 115200
- Acompanhe as mensagens de debug

## 🎮 Funcionamento

### Estados do Sistema:
1. **WAITING_START** - Aguardando botão ser pressionado
2. **INITIALIZING_BOARD** - Recebendo matriz inicial
3. **WAITING_PLAYER_MOVE** - Aguardando jogador remover peça
4. **PROCESSING_MOVE** - Processando movimento do jogador
5. **WAITING_AI_MOVE** - Aguardando movimento da IA
6. **VALIDATING_AI_MOVE** - Validando movimento da IA

### Fluxo de Operação:
1. Pressionar botão → Envia "game_start"
2. Recebe matriz → Valida sensores → Animação verde
3. Detecta peça removida → Envia posição
4. Recebe opções → Acende LEDs (verde/amarelo)
5. Detecta peça colocada → Envia movimento completo
6. Recebe movimento IA → Mostra LEDs azuis
7. Valida movimento IA → Confirma → Repete ciclo

## 🔧 Personalização

### Thresholds dos Sensores:
```cpp
#define SENSOR_THRESHOLD 2000  // Ajustar conforme necessário
```

### Tempos de Debounce:
```cpp
#define DEBOUNCE_TIME 100      // ms
```

### Timeouts:
```cpp
const unsigned long timeout = 60000; // 60 segundos
```

## 🐛 Resolução de Problemas

### Sensores não detectam ímãs:
- Verificar conexões dos multiplexadores
- Ajustar `SENSOR_THRESHOLD`
- Testar sensores individualmente

### LEDs não funcionam:
- Verificar pino DATA (GPIO 5)
- Verificar alimentação dos LEDs
- Testar com código de exemplo FastLED

### Comunicação serial falha:
- Verificar baudrate (115200)
- Verificar cabo USB
- Reiniciar ESP32

### Debug:
- Usar Serial Monitor para ver mensagens
- Verificar estado atual do sistema
- Acompanhar valores dos sensores

## 📊 Monitoramento

O código envia mensagens de debug via Serial:
- Estado atual do sistema
- Valores dos sensores
- Mensagens JSON enviadas/recebidas
- Erros e avisos

Exemplo de saída:
```
ESP32 ChessAI iniciado!
Pressione o botão para iniciar o jogo...
Jogo iniciado! Aguardando configuração inicial...
Tabuleiro validado! Iniciando animação de confirmação...
Peça (ímã) removida de: E2
LED 28 -> Verde
LED 36 -> Amarelo
```
