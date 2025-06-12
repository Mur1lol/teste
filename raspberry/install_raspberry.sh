#!/bin/bash
# ChessAI - Script de Instalação para Raspberry Pi
# Este script instala todas as dependências necessárias

echo "🚀 Iniciando instalação do ChessAI..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Verificar se está rodando como root para algumas operações
check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        log_warning "Algumas operações precisam de privilégios sudo."
        return 1
    fi
    return 0
}

# Atualizar sistema
log_info "Atualizando lista de pacotes..."
sudo apt-get update

log_info "Atualizando sistema..."
sudo apt-get upgrade -y

# Instalar Python3 e pip se não estiverem instalados
log_info "Verificando instalação do Python3..."
if ! command -v python3 &> /dev/null; then
    log_info "Instalando Python3..."
    sudo apt-get install -y python3 python3-pip
else
    log_info "Python3 já está instalado"
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_info "Versão do Python: $PYTHON_VERSION"

# Instalar pip se não estiver instalado
if ! command -v pip3 &> /dev/null; then
    log_info "Instalando pip3..."
    sudo apt-get install -y python3-pip
else
    log_info "pip3 já está instalado"
fi

# Instalar Stockfish
log_info "Verificando instalação do Stockfish..."
if ! command -v stockfish &> /dev/null; then
    log_info "Instalando Stockfish..."
    sudo apt-get install -y stockfish
else
    log_info "Stockfish já está instalado"
fi

# Verificar versão do Stockfish
STOCKFISH_VERSION=$(stockfish --version 2>/dev/null | head -n1 || echo "Versão não disponível")
log_info "Stockfish: $STOCKFISH_VERSION"

# Instalar dependências Python
log_info "Instalando dependências Python..."
pip3 install --user python-chess pyserial

# Verificar se as dependências foram instaladas corretamente
log_info "Verificando instalação das dependências..."

python3 -c "import chess; print('✅ python-chess: OK')" 2>/dev/null || log_error "❌ python-chess não foi instalado corretamente"
python3 -c "import serial; print('✅ pyserial: OK')" 2>/dev/null || log_error "❌ pyserial não foi instalado corretamente"
python3 -c "import json; print('✅ json: OK')" 2>/dev/null || log_error "❌ json não disponível"
python3 -c "import threading; print('✅ threading: OK')" 2>/dev/null || log_error "❌ threading não disponível"

# Configurar permissões para porta serial
log_info "Configurando permissões para porta serial..."
sudo usermod -a -G dialout $USER

# Criar diretório de logs se não existir
log_info "Criando diretório de logs..."
mkdir -p ~/chessai_logs

# Verificar portas seriais disponíveis
log_info "Portas seriais disponíveis:"
ls /dev/tty* | grep -E "(USB|ACM)" | head -5 || log_warning "Nenhuma porta serial USB encontrada"

# Criar script de execução
log_info "Criando script de execução..."
cat > ~/start_chessai.sh << 'EOF'
#!/bin/bash
# Script para iniciar o ChessAI Server
cd ~/ChessAI/novo
python3 raspberry_chessai.py --port /dev/ttyUSB0 --baudrate 115200
EOF

chmod +x ~/start_chessai.sh

# Criar arquivo de configuração
log_info "Criando arquivo de configuração..."
cat > ~/chessai_config.json << 'EOF'
{
    "serial_port": "/dev/ttyUSB0",
    "baudrate": 115200,
    "stockfish_depth": 10,
    "stockfish_time": 1.0,
    "log_level": "INFO",
    "auto_start": false
}
EOF

echo ""
log_info "🎉 Instalação concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Reinicie o sistema ou faça logout/login para aplicar as permissões de porta serial"
echo "2. Conecte a ESP32 via USB"
echo "3. Execute: ~/start_chessai.sh"
echo ""
echo "📂 Arquivos criados:"
echo "  - ~/start_chessai.sh (script de execução)"
echo "  - ~/chessai_config.json (configuração)"
echo "  - ~/chessai_logs/ (diretório de logs)"
echo ""
echo "🔧 Para testar a comunicação serial:"
echo "  ls /dev/tty* | grep -E '(USB|ACM)'"
echo ""
echo "🆘 Em caso de problemas:"
echo "  - Verifique se a ESP32 está conectada"
echo "  - Execute com --debug para mais informações"
echo "  - Consulte os logs em ~/chessai_logs/"
echo ""

log_warning "IMPORTANTE: Reinicie o sistema ou faça logout/login para aplicar as permissões!"
