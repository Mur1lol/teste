/*
  Teste básico de comunicação ESP32 -> Raspberry Pi
  
  Envia mensagens simples via Serial USB para testar a comunicação
  A ESP32 enviará mensagens numeradas a cada 2 segundos
  E aguardará respostas da Raspberry Pi
*/

int contador = 0;

void setup() {
  // Inicializar comunicação serial
  Serial.begin(115200);
  
  // Aguardar a serial estar pronta
  while (!Serial) {
    delay(10);
  }
  
  Serial.println("ESP32 - Teste de comunicação iniciado");
  delay(1000);
}

void loop() {
  // Enviar mensagem para Raspberry Pi
  contador++;
  Serial.print("ESP32_MSG:");
  Serial.print(contador);
  Serial.print(":Ola da ESP32 - Contador ");
  Serial.println(contador);
  
  // Aguardar resposta por 2 segundos
  unsigned long startTime = millis();
  String resposta = "";
  
  while (millis() - startTime < 2000) {
    if (Serial.available()) {
      resposta = Serial.readStringUntil('\n');
      resposta.trim();
      
      if (resposta.length() > 0) {
        Serial.print("ESP32_RECEBIDO:");
        Serial.println(resposta);
        break;
      }
    }
    delay(10);
  }
  
  // Se não recebeu resposta
  if (resposta.length() == 0) {
    Serial.println("ESP32_TIMEOUT:Nenhuma resposta da Raspberry Pi");
  }
  
  delay(3000); // Aguardar 3 segundos antes da próxima mensagem
}
