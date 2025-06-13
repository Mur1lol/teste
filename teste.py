import serial
import time

# Chave usada para criptografar (deve ser igual à da ESP32)
CHAVE = ord('K')

# Função para codificar/decodificar usando XOR
def codificar(msg):
    return bytes([c ^ CHAVE for c in msg.encode('utf-8')])

def decodificar(data):
    return ''.join([chr(b ^ CHAVE) for b in data])

# Abre a comunicação serial com a ESP32
ser = serial.Serial("/dev/serial0", 115200, timeout=1)
time.sleep(2)  # Tempo para a ESP32 resetar

# Envia mensagem codificada
mensagem = "start"
ser.write(codificar(mensagem + '\n'))
print(f"Enviado (codificado): {mensagem}")

# Aguarda resposta da ESP32
time.sleep(1)
resposta = ser.read_all()

if resposta:
    decodificada = decodificar(resposta)
    print(f"Recebido da ESP32 (decodificado): {decodificada}")
else:
    print("Nenhuma resposta recebida.")
