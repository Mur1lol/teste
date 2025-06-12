#!/usr/bin/env python3
"""
ChessAI - Script de Execução Simplificado
Facilita a execução do servidor ChessAI na Raspberry Pi
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

def main():
    print("🚀 ChessAI - Servidor Raspberry Pi")
    print("=" * 50)
    
    # Adicionar diretório atual ao Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Verificar se os arquivos necessários existem
    required_files = [
        'raspberry_chessai.py',
        'chessai_utils.py',
        'config.json'
    ]
    
    missing_files = []
    for file in required_files:
        if not (current_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Arquivos necessários não encontrados: {missing_files}")
        print("Verifique se todos os arquivos estão na pasta correta.")
        return 1
    
    # Verificar dependências
    try:
        import chess
        import serial
        print("✅ Dependências Python encontradas")
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("Execute: pip install -r requirements.txt")
        return 1
    
    # Verificar Stockfish
    stockfish_found = False
    stockfish_paths = [
        '/usr/games/stockfish',
        '/usr/local/bin/stockfish',
        '/usr/bin/stockfish'
    ]
    
    for path in stockfish_paths:
        if Path(path).exists():
            print(f"✅ Stockfish encontrado: {path}")
            stockfish_found = True
            break
    
    if not stockfish_found:
        try:
            subprocess.run(['stockfish', '--version'], 
                         capture_output=True, timeout=2)
            print("✅ Stockfish encontrado no PATH")
            stockfish_found = True
        except:
            pass
    
    if not stockfish_found:
        print("⚠️  Stockfish não encontrado. Instale com: sudo apt-get install stockfish")
    
    # Detectar portas seriais disponíveis
    print("\n🔍 Procurando portas seriais...")
    available_ports = []
    
    # Linux/Raspberry Pi
    for port_pattern in ['/dev/ttyUSB*', '/dev/ttyACM*']:
        import glob
        ports = glob.glob(port_pattern)
        available_ports.extend(ports)
    
    # Windows
    if sys.platform == 'win32':
        for i in range(1, 21):
            available_ports.append(f'COM{i}')
    
    if available_ports:
        print(f"📡 Portas seriais disponíveis: {available_ports[:5]}")
        default_port = available_ports[0]
    else:
        print("⚠️  Nenhuma porta serial detectada")
        default_port = '/dev/ttyUSB0' if sys.platform != 'win32' else 'COM3'
    
    # Configurar argumentos
    parser = argparse.ArgumentParser(description='ChessAI Server - Execução Simplificada')
    parser.add_argument('--port', default=default_port, 
                       help=f'Porta serial (padrão: {default_port})')
    parser.add_argument('--baudrate', type=int, default=115200,
                       help='Taxa de transmissão (padrão: 115200)')
    parser.add_argument('--debug', action='store_true',
                       help='Ativar modo debug')
    parser.add_argument('--test', action='store_true',
                       help='Executar em modo teste (sem hardware)')
    
    args = parser.parse_args()
    
    print(f"\n⚙️  Configuração:")
    print(f"   Porta: {args.port}")
    print(f"   Baudrate: {args.baudrate}")
    print(f"   Debug: {'Ativado' if args.debug else 'Desativado'}")
    print(f"   Modo teste: {'Ativado' if args.test else 'Desativado'}")
    
    print(f"\n🎮 Iniciando ChessAI Server...")
    print("   Pressione Ctrl+C para parar")
    print("-" * 50)
    
    # Executar servidor
    try:
        from raspberry_chessai import ChessAIServer
        
        # Configurar nível de log
        if args.debug:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Criar e iniciar servidor
        server = ChessAIServer(serial_port=args.port, baudrate=args.baudrate)
        server.start_server()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor interrompido pelo usuário")
    except ImportError as e:
        print(f"\n❌ Erro de importação: {e}")
        print("Verifique se todos os arquivos estão presentes")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    print("👋 ChessAI Server encerrado")
    return 0

if __name__ == "__main__":
    sys.exit(main())
