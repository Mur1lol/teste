# ChessAI - Raspberry Pi

Esta pasta contém todos os arquivos necessários para executar o servidor ChessAI na Raspberry Pi.

## 📁 Arquivos

- `raspberry_chessai.py` - Servidor principal do ChessAI
- `chessai_utils.py` - Utilitários auxiliares e classes de apoio
- `config.json` - Arquivo de configuração
- `requirements.txt` - Dependências Python
- `install_raspberry.sh` - Script de instalação automática
- `run_server.py` - Script de execução simplificado

## 🚀 Instalação

### No Raspberry Pi (Linux):
```bash
# Dar permissão de execução ao script
chmod +x install_raspberry.sh

# Executar instalação
./install_raspberry.sh
```

### No Windows (para desenvolvimento/teste):
```powershell
# Instalar dependências
pip install -r requirements.txt

# Nota: Stockfish deve ser instalado separadamente
```

## ▶️ Execução

### Método 1 - Script simplificado:
```bash
# Linux/Raspberry Pi
python3 run_server.py

# Windows
py run_server.py
```

### Método 2 - Execução direta:
```bash
# Linux/Raspberry Pi
python3 raspberry_chessai.py --port /dev/ttyUSB0 --baudrate 115200

# Windows (para teste)
py raspberry_chessai.py --port COM3 --baudrate 115200
```

### Método 3 - Com debug:
```bash
# Linux/Raspberry Pi
python3 raspberry_chessai.py --debug

# Windows
py raspberry_chessai.py --debug
```

## ⚙️ Configuração

Edite o arquivo `config.json` para personalizar:

- **Porta serial**: `/dev/ttyUSB0` (Linux) ou `COM3` (Windows)
- **Baudrate**: `115200` (padrão)
- **Configurações do Stockfish**: tempo limite, profundidade
- **Nível de log**: `INFO`, `DEBUG`, `ERROR`

## 🔧 Resolução de Problemas

### Erro: "Permission denied" na porta serial
```bash
sudo chmod 666 /dev/ttyUSB0
# ou
sudo usermod -a -G dialout $USER
```

### Stockfish não encontrado
```bash
# Instalar Stockfish
sudo apt-get install stockfish

# Verificar instalação
which stockfish
```

### Problemas de dependências
```bash
# Reinstalar dependências
pip3 install --upgrade -r requirements.txt
```

## 📊 Logs

- Logs são salvos em `chessai.log`
- Para ver logs em tempo real: `tail -f chessai.log`
- Para limpar logs: `rm chessai.log`

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs em `chessai.log`
2. Execute com `--debug` para mais informações
3. Verifique se a ESP32 está conectada e funcionando
4. Teste a comunicação serial separadamente
