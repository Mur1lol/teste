# Teste Básico de Comunicação ESP32 <-> Raspberry Pi

Este é um teste simples para verificar a comunicação serial entre ESP32 e Raspberry Pi via cabo USB.

## Arquivos

- `esp_rasp.ino` - Código para carregar na ESP32
- `rasp_esp.py` - Código para executar na Raspberry Pi (ou computador)

## Como usar

### 1. Carregar código na ESP32
1. Abra o Arduino IDE
2. Abra o arquivo `esp_rasp.ino`
3. Selecione a placa ESP32 Dev Module
4. Selecione a porta COM correta
5. Carregue o código na ESP32

### 2. Executar código na Raspberry Pi
1. Conecte a ESP32 na Raspberry Pi via cabo USB
2. Execute o comando:
   ```bash
   python3 rasp_esp.py
   ```

### 3. O que deve acontecer
- A ESP32 enviará mensagens numeradas a cada 3 segundos
- A Raspberry Pi receberá as mensagens e enviará respostas
- Você verá a comunicação bidirecional funcionando

### Exemplo de saída esperada:
```
📥 RECEBIDO: ESP32_MSG:1:Ola da ESP32 - Contador 1
📤 ENVIADO: RASP_RESPOSTA:1:Ola da Raspberry Pi!
--------------------------------------------------
📥 RECEBIDO: ESP32_RECEBIDO:RASP_RESPOSTA:1:Ola da Raspberry Pi!
📥 RECEBIDO: ESP32_MSG:2:Ola da ESP32 - Contador 2
📤 ENVIADO: RASP_RESPOSTA:2:Ola da Raspberry Pi!
```

## Solução de problemas

- **Erro de porta serial**: Verifique se a ESP32 está conectada e se os drivers estão instalados
- **No Windows**: As portas geralmente são COM3, COM4, etc.
- **No Linux/Raspberry Pi**: As portas geralmente são /dev/ttyUSB0, /dev/ttyACM0, etc.
- **Instalar pyserial**: `pip install pyserial` se necessário
