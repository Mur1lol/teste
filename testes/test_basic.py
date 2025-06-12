#!/usr/bin/env python3
"""
Teste rápido para verificar se o ChessAI Server está funcionando
"""

import sys
import os

# Adicionar o diretório atual ao path para importar o módulo
sys.path.append(os.path.dirname(__file__))

try:
    from raspberry_chessai import ChessAIServer
    print("✅ Importação do ChessAIServer: OK")
    
    # Testar criação da instância
    server = ChessAIServer(serial_port='/dev/ttyUSB0', baudrate=115200)
    print("✅ Criação da instância: OK")
    
    # Testar se o logger foi criado corretamente
    if hasattr(server, 'logger'):
        print("✅ Logger configurado: OK")
    else:
        print("❌ Logger não encontrado")
    
    # Testar se o Stockfish path foi encontrado
    if hasattr(server, 'stockfish_path') and server.stockfish_path:
        print(f"✅ Stockfish path: {server.stockfish_path}")
    else:
        print("⚠️  Stockfish path não encontrado (isso é normal se não estiver instalado)")
    
    # Testar métodos básicos
    print("✅ Testando método get_board_status...")
    status = server.get_board_status()
    print(f"   Status do tabuleiro: {status['turn']}, jogadas: {status['move_count']}")
    
    print("\n🎉 Todos os testes básicos passaram!")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Verifique se as dependências estão instaladas:")
    print("pip install python-chess pyserial")
    
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
