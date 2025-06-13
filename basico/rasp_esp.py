#!/usr/bin/env python3
"""
Teste básico de comunicação Raspberry Pi <-> ESP32

Recebe mensagens da ESP32 via Serial USB e envia respostas simples
Para testar a comunicação básica entre as duas placas
"""

import serial
import time
import sys

def main():
    # Configurações da conexão serial
    # No Windows, geralmente será algo como 'COM3', 'COM4', etc.
    # No Linux/Raspberry Pi será algo como '/dev/ttyUSB0', '/dev/ttyACM0', etc.
    serial_ports = [
        'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8',  # Windows
        '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1'  # Linux/Raspberry Pi
    ]
    
    serial_connection = None
    
    # Tentar conectar em diferentes portas
    for port in serial_ports:
        try:
            print(f"Tentando conectar na porta: {port}")
            serial_connection = serial.Serial(
                port=port,
                baudrate=115200,
                timeout=1
            )
            time.sleep(2)  # Aguardar inicialização
            print(f"✅ Conectado com sucesso na porta: {port}")
            break
        except serial.SerialException:
            print(f"❌ Falha ao conectar na porta: {port}")
            continue
    
    if not serial_connection:
        print("❌ Erro: Não foi possível conectar em nenhuma porta serial")
        print("Verifique se a ESP32 está conectada e se os drivers estão instalados")
        return
    
    print("\n🚀 Teste de comunicação ESP32 <-> Raspberry Pi iniciado")
    print("📡 Aguardando mensagens da ESP32...")
    print("Press Ctrl+C para parar\n")
    
    contador_respostas = 0
    
    try:
        while True:
            # Verificar se há dados disponíveis
            if serial_connection.in_waiting > 0:
                # Ler linha da ESP32
                linha = serial_connection.readline().decode('utf-8').strip()
                
                if linha:
                    print(f"📥 RECEBIDO: {linha}")
                    
                    # Se for uma mensagem da ESP32, enviar resposta
                    if linha.startswith("ESP32_MSG:"):
                        contador_respostas += 1
                        resposta = f"RASP_RESPOSTA:{contador_respostas}:Ola da Raspberry Pi!"
                        
                        # Enviar resposta
                        serial_connection.write((resposta + '\n').encode('utf-8'))
                        print(f"📤 ENVIADO: {resposta}")
                        print("-" * 50)
            
            time.sleep(0.1)  # Pequena pausa para não sobrecarregar o CPU
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante comunicação: {e}")
    finally:
        if serial_connection and serial_connection.is_open:
            serial_connection.close()
            print("🔌 Conexão serial fechada")

if __name__ == "__main__":
    main()
