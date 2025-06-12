#include <ArduinoJson.h>
#include <WiFi.h>
#include <HardwareSerial.h>

// Configurações do hardware
#define BOARD_SIZE 8
#define NUM_LEDS 64
#define START_BUTTON_PIN 2
#define SERIAL_BAUDRATE 115200

// Pinos dos LEDs (assumindo matriz de LEDs addressáveis)
#define LED_DATA_PIN 5
#define LED_CLOCK_PIN 18

// Pinos dos sensores de efeito Hall (usando multiplexadores)
#define MUX_A0 12
#define MUX_A1 13
#define MUX_A2 14
#define MUX_A3 15
#define MUX_EN1 16
#define MUX_EN2 17
#define MUX_SIG 34

// Configurações dos sensores
#define SENSOR_THRESHOLD 2000  // Threshold para detecção de ímã (sensores Hall)
#define DEBOUNCE_TIME 100      // Tempo de debounce em ms

// Estados do jogo
enum GameState {
  WAITING_START,
  INITIALIZING_BOARD,
  WAITING_PLAYER_MOVE,
  PROCESSING_MOVE,
  WAITING_AI_MOVE,
  VALIDATING_AI_MOVE
};

// Estrutura para representar uma casa do tabuleiro
struct BoardPosition {
  int row;
  int col;
  String notation; // Ex: A1, B2, etc.
};

// Variáveis globais
GameState currentState = WAITING_START;
int boardMatrix[BOARD_SIZE][BOARD_SIZE];
int sensorReadings[BOARD_SIZE][BOARD_SIZE];
BoardPosition selectedPosition = {-1, -1, ""};
String pendingFromMove = "";
String pendingToMove = "";
bool buttonPressed = false;

// Array para rastrear quais LEDs estão acesos (para validação de movimento)
bool activeLEDs[BOARD_SIZE][BOARD_SIZE];

// Protótipos das funções
void setupHardware();
void setupSerial();
void handleGameLogic();
void readAllSensors();
void sendJsonMessage(String type, String data);
void receiveSerialData();
void processReceivedJson(String jsonData);
void initializeBoardValidation();
void handlePlayerMove();
void handleAIMove();
void displayMoveOptions(String bestMove, String alternatives);
void animateBoardConfirmation();
void blinkErrorLED(int row, int col);
void setLEDColor(int row, int col, String color);
void clearAllLEDs();
String positionToNotation(int row, int col);
BoardPosition notationToPosition(String notation);
int readSensorValue(int row, int col);
void selectMuxChannel(int channel);
bool isButtonPressed();
void debounceButton();
bool isLEDPosition(int row, int col);
void setActiveLED(int row, int col, bool active);
void clearActiveLEDs();

void setup() {
  setupSerial();
  setupHardware();
  
  Serial.println("ESP32 ChessAI iniciado!");
  Serial.println("Pressione o botão para iniciar o jogo...");
  
  clearAllLEDs();
  currentState = WAITING_START;
}

void loop() {
  receiveSerialData();
  handleGameLogic();
  debounceButton();
  delay(50); // Pequeno delay para estabilidade
}

void setupSerial() {
  Serial.begin(SERIAL_BAUDRATE);
  while (!Serial) {
    delay(10);
  }
}

void setupHardware() {
  // Configurar pino do botão
  pinMode(START_BUTTON_PIN, INPUT_PULLUP);
  
  // Configurar pinos do multiplexador
  pinMode(MUX_A0, OUTPUT);
  pinMode(MUX_A1, OUTPUT);
  pinMode(MUX_A2, OUTPUT);
  pinMode(MUX_A3, OUTPUT);
  pinMode(MUX_EN1, OUTPUT);
  pinMode(MUX_EN2, OUTPUT);
  pinMode(MUX_SIG, INPUT);
  
  // Configurar pinos dos LEDs
  pinMode(LED_DATA_PIN, OUTPUT);
  pinMode(LED_CLOCK_PIN, OUTPUT);
  
  // Desabilitar multiplexadores inicialmente
  digitalWrite(MUX_EN1, HIGH);
  digitalWrite(MUX_EN2, HIGH);
}

void handleGameLogic() {
  switch (currentState) {
    case WAITING_START:
      if (isButtonPressed()) {
        sendJsonMessage("game_start", "");
        currentState = INITIALIZING_BOARD;
        Serial.println("Jogo iniciado! Aguardando configuração inicial...");
      }
      break;
      
    case INITIALIZING_BOARD:
      // Aguarda receber a matriz inicial da Raspberry
      break;
      
    case WAITING_PLAYER_MOVE:
      handlePlayerMove();
      break;
      
    case PROCESSING_MOVE:
      // Aguarda resposta da Raspberry com opções de movimento
      break;
      
    case WAITING_AI_MOVE:
      // Aguarda movimento da IA
      break;
      
    case VALIDATING_AI_MOVE:
      handleAIMove();
      break;
  }
}

void handlePlayerMove() {
  readAllSensors();
  
  // Detectar se uma peça foi removida (ímã não detectado mais)
  for (int row = 0; row < BOARD_SIZE; row++) {
    for (int col = 0; col < BOARD_SIZE; col++) {
      int currentReading = readSensorValue(row, col);
      
      // Se havia uma peça (ímã) e agora não há mais (sensor não ativado)
      if (boardMatrix[row][col] == 1 && currentReading < SENSOR_THRESHOLD) {
        String fromPosition = positionToNotation(row, col);
        
        // Enviar posição de origem para a Raspberry
        DynamicJsonDocument doc(200);
        doc["type"] = "player_move";
        doc["from"] = fromPosition;
        
        String jsonString;
        serializeJson(doc, jsonString);
        Serial.println(jsonString);
        
        pendingFromMove = fromPosition;
        currentState = PROCESSING_MOVE;
        
        Serial.println("Peça (ímã) removida de: " + fromPosition);
        return;
      }
    }
  }
}

void handleAIMove() {
  readAllSensors();
  
  // Verificar se o movimento da IA foi executado corretamente
  BoardPosition fromPos = notationToPosition(pendingFromMove);
  BoardPosition toPos = notationToPosition(pendingToMove);
  
  int fromSensor = readSensorValue(fromPos.row, fromPos.col);
  int toSensor = readSensorValue(toPos.row, toPos.col);
  
  // Se a peça (ímã) foi removida da origem e colocada no destino
  if (fromSensor < SENSOR_THRESHOLD && toSensor >= SENSOR_THRESHOLD) {
    // Movimento correto
    Serial.println("Movimento da IA executado corretamente!");
    setLEDColor(toPos.row, toPos.col, "green");
    delay(1000);
    clearAllLEDs();
    
    // Confirmar movimento para a Raspberry
    sendJsonMessage("ai_move_confirmed", "OK");
    
    // Atualizar matriz local
    boardMatrix[fromPos.row][fromPos.col] = 0;
    boardMatrix[toPos.row][toPos.col] = 1;
    
    currentState = WAITING_PLAYER_MOVE;
    pendingFromMove = "";
    pendingToMove = "";
    
    Serial.println("Sua vez! Remova uma peça para fazer sua jogada.");
  } else {
    // Movimento incorreto - verificar onde está o problema
    if (fromSensor >= SENSOR_THRESHOLD) {
      Serial.println("ERRO: Peça ainda não foi removida da origem!");
      blinkErrorLED(fromPos.row, fromPos.col);
    }
    if (toSensor < SENSOR_THRESHOLD) {
      Serial.println("ERRO: Peça não foi colocada no destino correto!");
      blinkErrorLED(toPos.row, toPos.col);
    }
    delay(1000);
  }
}

void receiveSerialData() {
  if (Serial.available()) {
    String receivedData = Serial.readStringUntil('\n');
    receivedData.trim();
    
    if (receivedData.length() > 0) {
      processReceivedJson(receivedData);
    }
  }
}

void processReceivedJson(String jsonData) {
  DynamicJsonDocument doc(1024);
  DeserializationError error = deserializeJson(doc, jsonData);
  
  if (error) {
    Serial.println("Erro ao processar JSON: " + String(error.c_str()));
    return;
  }
  
  String type = doc["type"];
  
  if (type == "board_matrix") {
    // Receber matriz inicial do tabuleiro
    JsonArray matrix = doc["matrix"];
    
    for (int row = 0; row < BOARD_SIZE; row++) {
      for (int col = 0; col < BOARD_SIZE; col++) {
        boardMatrix[row][col] = matrix[row * BOARD_SIZE + col];
      }
    }
    
    initializeBoardValidation();
    
  } else if (type == "move_options") {
    // Receber opções de movimento
    String bestMove = doc["best_move"];
    String alternatives = doc["alternatives"];
    
    displayMoveOptions(bestMove, alternatives);
    
  } else if (type == "ai_move") {
    // Receber movimento da IA
    String fromPos = doc["from"];
    String toPos = doc["to"];
    
    pendingFromMove = fromPos;
    pendingToMove = toPos;
    
    // Acender LEDs para indicar movimento da IA
    BoardPosition from = notationToPosition(fromPos);
    BoardPosition to = notationToPosition(toPos);
    
    setLEDColor(from.row, from.col, "blue_solid");
    setLEDColor(to.row, to.col, "blue_blink");
    
    currentState = VALIDATING_AI_MOVE;
    
    Serial.println("IA quer mover de " + fromPos + " para " + toPos);
  }
}

void initializeBoardValidation() {
  readAllSensors();
  
  bool validationPassed = true;
  
  // Comparar estado físico com matriz esperada
  for (int row = 0; row < BOARD_SIZE; row++) {
    for (int col = 0; col < BOARD_SIZE; col++) {
      int sensorValue = readSensorValue(row, col);
      bool hasPiece = (sensorValue >= SENSOR_THRESHOLD); // Ímã detectado pelo sensor Hall
      
      if ((boardMatrix[row][col] == 1 && !hasPiece) || 
          (boardMatrix[row][col] == 0 && hasPiece)) {
        // Erro detectado - piscar LED vermelho na casa com problema
        blinkErrorLED(row, col);
        validationPassed = false;
        String pos = positionToNotation(row, col);
        if (boardMatrix[row][col] == 1 && !hasPiece) {
          Serial.println("ERRO: Falta ímã (peça) na posição " + pos);
        } else {
          Serial.println("ERRO: Ímã (peça) extra na posição " + pos);
        }
      }
    }
  }
  
  if (validationPassed) {
    Serial.println("Tabuleiro validado! Iniciando animação de confirmação...");
    animateBoardConfirmation();
    currentState = WAITING_PLAYER_MOVE;
    Serial.println("Tabuleiro pronto! Faça sua jogada removendo uma peça...");
  } else {
    Serial.println("Erro na configuração do tabuleiro! Corrija as peças e pressione o botão novamente.");
    currentState = WAITING_START;
  }
}

void displayMoveOptions(String bestMove, String alternatives) {
  clearAllLEDs();
  clearActiveLEDs();
  
  Serial.println("Opções de movimento recebidas:");
  Serial.println("Melhor movimento: " + bestMove);
  Serial.println("Alternativas: " + alternatives);
  
  // Extrair posição de destino do melhor movimento
  String bestDestination = bestMove.substring(2); // Ex: D2D4 -> D4
  BoardPosition bestPos = notationToPosition(bestDestination);
  setLEDColor(bestPos.row, bestPos.col, "green");
  setActiveLED(bestPos.row, bestPos.col, true);
  
  // Processar alternativas (formato: ["D2D3", "D2D5"])
  // Simplificação: assumir que alternatives é uma string com movimentos separados por vírgula
  int startIdx = 0;
  while (startIdx < alternatives.length()) {
    int endIdx = alternatives.indexOf(',', startIdx);
    if (endIdx == -1) endIdx = alternatives.length();
    
    String move = alternatives.substring(startIdx, endIdx);
    move.trim();
    move.replace("\"", "");
    move.replace("[", "");
    move.replace("]", "");
    
    if (move.length() >= 4) {
      String destination = move.substring(2);
      BoardPosition pos = notationToPosition(destination);
      if (!(pos.row == bestPos.row && pos.col == bestPos.col)) {
        setLEDColor(pos.row, pos.col, "yellow");
        setActiveLED(pos.row, pos.col, true);
      }
    }
    
    startIdx = endIdx + 1;
  }
  
  Serial.println("LEDs acesos nas posições válidas. Coloque sua peça em uma das casas indicadas.");
  
  // Aguardar movimento do jogador para uma das posições indicadas
  waitForPlayerDestination();
}

void waitForPlayerDestination() {
  unsigned long startTime = millis();
  const unsigned long timeout = 60000; // 60 segundos de timeout
  
  while (millis() - startTime < timeout) {
    readAllSensors();
    
    for (int row = 0; row < BOARD_SIZE; row++) {
      for (int col = 0; col < BOARD_SIZE; col++) {
        int currentReading = readSensorValue(row, col);
        
        // Se uma peça (ímã) foi colocada em uma posição que estava vazia
        if (boardMatrix[row][col] == 0 && currentReading >= SENSOR_THRESHOLD) {
          String toPosition = positionToNotation(row, col);
          
          // Verificar se é uma posição válida (LED estava aceso)
          // Verificar se a posição tem LED aceso (verde ou amarelo)
          bool isValidPosition = isLEDPosition(row, col);
          
          if (isValidPosition) {
            // Posição válida - aceitar movimento
            DynamicJsonDocument doc(200);
            doc["type"] = "player_move_complete";
            doc["from"] = pendingFromMove;
            doc["to"] = toPosition;
            
            String jsonString;
            serializeJson(doc, jsonString);
            Serial.println(jsonString);
            
            // Atualizar matriz local
            int fromPos_row = notationToPosition(pendingFromMove).row;
            int fromPos_col = notationToPosition(pendingFromMove).col;
            boardMatrix[fromPos_row][fromPos_col] = 0;
            boardMatrix[row][col] = 1;
            
            clearAllLEDs();
            currentState = WAITING_AI_MOVE;
            
            Serial.println("Movimento válido realizado: " + pendingFromMove + " -> " + toPosition);
            return;
          } else {
            // Posição inválida - piscar vermelho e continuar esperando
            Serial.println("Posição inválida! Coloque a peça em uma casa com LED aceso.");
            blinkErrorLED(row, col);
            delay(500);
          }
        }
      }
    }
    
    delay(100);
  }
  
  // Timeout - voltar ao estado anterior
  Serial.println("Timeout! Tente novamente fazendo uma nova jogada.");
  clearAllLEDs();
  currentState = WAITING_PLAYER_MOVE;
}

void animateBoardConfirmation() {
  // Animação de confirmação - LEDs verdes percorrendo o tabuleiro
  for (int row = 0; row < BOARD_SIZE; row++) {
    for (int col = 0; col < BOARD_SIZE; col++) {
      setLEDColor(row, col, "green");
      delay(50);
      setLEDColor(row, col, "off");
    }
  }
  
  delay(500);
  clearAllLEDs();
}

void blinkErrorLED(int row, int col) {
  for (int i = 0; i < 5; i++) {
    setLEDColor(row, col, "red");
    delay(200);
    setLEDColor(row, col, "off");
    delay(200);
  }
}

void setLEDColor(int row, int col, String color) {
  // Implementação simplificada para controle de LEDs
  // Aqui você implementaria o controle específico do seu hardware de LEDs
  
  int ledIndex = row * BOARD_SIZE + col;
  
  if (color == "green") {
    // Acender LED verde
    Serial.println("LED " + String(ledIndex) + " -> Verde");
  } else if (color == "red") {
    // Acender LED vermelho
    Serial.println("LED " + String(ledIndex) + " -> Vermelho");
  } else if (color == "yellow") {
    // Acender LED amarelo
    Serial.println("LED " + String(ledIndex) + " -> Amarelo");
  } else if (color == "blue_solid") {
    // Acender LED azul fixo
    Serial.println("LED " + String(ledIndex) + " -> Azul Fixo");
  } else if (color == "blue_blink") {
    // Acender LED azul piscante
    Serial.println("LED " + String(ledIndex) + " -> Azul Piscante");
  } else if (color == "off") {
    // Apagar LED
    Serial.println("LED " + String(ledIndex) + " -> Apagado");
  }
}

void clearAllLEDs() {
  for (int row = 0; row < BOARD_SIZE; row++) {
    for (int col = 0; col < BOARD_SIZE; col++) {
      setLEDColor(row, col, "off");
    }
  }
  clearActiveLEDs();
}

String positionToNotation(int row, int col) {
  String notation = "";
  notation += (char)('A' + col);
  notation += String(8 - row);
  return notation;
}

BoardPosition notationToPosition(String notation) {
  BoardPosition pos;
  pos.notation = notation;
  pos.col = notation.charAt(0) - 'A';
  pos.row = 8 - notation.substring(1).toInt();
  return pos;
}

int readSensorValue(int row, int col) {
  int channel = row * BOARD_SIZE + col;
  selectMuxChannel(channel);
  delay(10); // Tempo para estabilizar
  return analogRead(MUX_SIG);
}

void selectMuxChannel(int channel) {
  // Controlar multiplexadores para selecionar o canal correto
  // Implementação depende do hardware específico usado
  
  if (channel < 32) {
    digitalWrite(MUX_EN1, LOW);  // Habilitar MUX1
    digitalWrite(MUX_EN2, HIGH); // Desabilitar MUX2
  } else {
    digitalWrite(MUX_EN1, HIGH); // Desabilitar MUX1
    digitalWrite(MUX_EN2, LOW);  // Habilitar MUX2
    channel -= 32;
  }
  
  digitalWrite(MUX_A0, (channel & 0x01) ? HIGH : LOW);
  digitalWrite(MUX_A1, (channel & 0x02) ? HIGH : LOW);
  digitalWrite(MUX_A2, (channel & 0x04) ? HIGH : LOW);
  digitalWrite(MUX_A3, (channel & 0x08) ? HIGH : LOW);
}

void readAllSensors() {
  for (int row = 0; row < BOARD_SIZE; row++) {
    for (int col = 0; col < BOARD_SIZE; col++) {
      sensorReadings[row][col] = readSensorValue(row, col);
    }
  }
}

bool isButtonPressed() {
  return digitalRead(START_BUTTON_PIN) == LOW;
}

void debounceButton() {
  static unsigned long lastButtonTime = 0;
  static bool lastButtonState = HIGH;
  
  bool currentState = digitalRead(START_BUTTON_PIN);
  
  if (currentState != lastButtonState && (millis() - lastButtonTime) > 50) {
    if (currentState == LOW) {
      buttonPressed = true;
    }
    lastButtonTime = millis();
  }
  
  lastButtonState = currentState;
}

void sendJsonMessage(String type, String data) {
  DynamicJsonDocument doc(200);
  doc["type"] = type;
  doc["data"] = data;
  
  String jsonString;
  serializeJson(doc, jsonString);
  Serial.println(jsonString);
}

bool isLEDPosition(int row, int col) {
  return activeLEDs[row][col];
}

void setActiveLED(int row, int col, bool active) {
  if (row >= 0 && row < BOARD_SIZE && col >= 0 && col < BOARD_SIZE) {
    activeLEDs[row][col] = active;
  }
}

void clearActiveLEDs() {
  for (int row = 0; row < BOARD_SIZE; row++) {
    for (int col = 0; col < BOARD_SIZE; col++) {
      activeLEDs[row][col] = false;
    }
  }
}
