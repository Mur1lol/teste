#!/usr/bin/env python3
"""
ChessAI - Test Communication
Simulador de comunicação entre ESP32 e Raspberry Pi
Para testes sem hardware físico
"""

import json
import time
import threading
import queue
from typing import Dict, Any
from chessai_utils import (
    CommunicationProtocol, 
    BoardStateManager, 
    LEDController, 
    TestUtilities,
    ChessNotationConverter
)

class ESP32Simulator:
    """Simulador da ESP32 para testes"""
    
    def __init__(self):
        self.message_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.led_controller = LEDController()
        self.board_matrix = None
        self.current_state = "WAITING_START"
        self.running = False
        
        print("ESP32 Simulator inicializado")
    
    def start(self):
        """Inicia o simulador"""
        self.running = True
        print("ESP32: Aguardando início do jogo...")
        print("Digite 'start' para iniciar o jogo")
    
    def stop(self):
        """Para o simulador"""
        self.running = False
    
    def send_game_start(self):
        """Simula pressionar botão de início"""
        message = CommunicationProtocol.create_message(
            CommunicationProtocol.MESSAGE_TYPES['GAME_START'],
            {}
        )
        self.response_queue.put(message)
        print("ESP32: Sinal de início enviado")
        self.current_state = "INITIALIZING_BOARD"
    
    def receive_message(self, message: str):
        """Recebe mensagem da Raspberry Pi"""
        data = CommunicationProtocol.parse_message(message)
        if not data:
            print("ESP32: Erro ao processar mensagem")
            return
        
        msg_type = data.get('type', '')
        print(f"ESP32: Recebida mensagem tipo '{msg_type}'")
        
        if msg_type == 'board_matrix':
            self.handle_board_matrix(data)
        elif msg_type == 'move_options':
            self.handle_move_options(data)
        elif msg_type == 'ai_move':
            self.handle_ai_move(data)
    
    def handle_board_matrix(self, data: Dict):
        """Processa matriz do tabuleiro"""
        matrix_flat = data.get('matrix', [])
        if len(matrix_flat) != 64:
            print("ESP32: Erro - matriz inválida")
            return
        
        # Converter para matriz 8x8
        self.board_matrix = []
        for i in range(8):
            row = matrix_flat[i*8:(i+1)*8]
            self.board_matrix.append(row)
        
        print("ESP32: Matriz do tabuleiro recebida")
        self.validate_board_setup()
    
    def validate_board_setup(self):
        """Simula validação física do tabuleiro"""
        print("ESP32: Validando configuração física do tabuleiro...")
        
        # Simular validação bem-sucedida
        time.sleep(1)
        print("ESP32: Tabuleiro validado! Animação de confirmação...")
        
        # Simular animação
        for i in range(8):
            for j in range(8):
                square = ChessNotationConverter.coordinates_to_square(i, j)
                print(f"LED {square} -> VERDE (animação)")
                time.sleep(0.05)
        
        print("ESP32: Pronto para receber jogadas!")
        self.current_state = "WAITING_PLAYER_MOVE"
    
    def simulate_player_move(self, from_square: str):
        """Simula jogador removendo uma peça"""
        if self.current_state != "WAITING_PLAYER_MOVE":
            print("ESP32: Não é possível mover agora")
            return
        
        print(f"ESP32: Peça removida de {from_square}")
        
        message = CommunicationProtocol.create_message(
            CommunicationProtocol.MESSAGE_TYPES['PLAYER_MOVE'],
            {'from': from_square}
        )
        self.response_queue.put(message)
        self.current_state = "PROCESSING_MOVE"
    
    def handle_move_options(self, data: Dict):
        """Processa opções de movimento"""
        best_move = data.get('best_move', '')
        alternatives = data.get('alternatives', [])
        
        print(f"ESP32: Melhor movimento: {best_move}")
        print(f"ESP32: Alternativas: {alternatives}")
        
        self.led_controller.show_move_options(best_move, alternatives)
        
        # Simular jogador escolhendo movimento
        if best_move and len(best_move) >= 4:
            to_square = best_move[2:4].upper()
            from_square = best_move[:2].upper()
            
            print(f"ESP32: Simulando jogador movendo para {to_square}")
            time.sleep(2)
            
            message = CommunicationProtocol.create_message(
                CommunicationProtocol.MESSAGE_TYPES['PLAYER_MOVE_COMPLETE'],
                {'from': from_square, 'to': to_square}
            )
            self.response_queue.put(message)
            self.current_state = "WAITING_AI_MOVE"
    
    def handle_ai_move(self, data: Dict):
        """Processa movimento da IA"""
        from_square = data.get('from', '')
        to_square = data.get('to', '')
        
        print(f"ESP32: IA quer mover de {from_square} para {to_square}")
        self.led_controller.show_ai_move(from_square, to_square)
        
        # Simular usuário executando movimento da IA
        print("ESP32: Simulando execução do movimento da IA...")
        time.sleep(3)
        
        message = CommunicationProtocol.create_message(
            CommunicationProtocol.MESSAGE_TYPES['AI_MOVE_CONFIRMED'],
            {'status': 'OK'}
        )
        self.response_queue.put(message)
        self.current_state = "WAITING_PLAYER_MOVE"
        print("ESP32: Movimento da IA confirmado. Sua vez!")
    
    def get_response(self):
        """Obtém resposta da ESP32"""
        try:
            return self.response_queue.get_nowait()
        except queue.Empty:
            return None

class RaspberryPiSimulator:
    """Simulador da Raspberry Pi para testes"""
    
    def __init__(self):
        self.board_manager = BoardStateManager()
        self.game_started = False
        self.running = False
        
        print("Raspberry Pi Simulator inicializado")
    
    def start(self):
        """Inicia o simulador"""
        self.running = True
        print("Raspberry Pi: Servidor iniciado, aguardando ESP32...")
    
    def stop(self):
        """Para o simulador"""
        self.running = False
    
    def process_message(self, message: str) -> str:
        """Processa mensagem da ESP32 e retorna resposta"""
        data = CommunicationProtocol.parse_message(message)
        if not data:
            return ""
        
        msg_type = data.get('type', '')
        print(f"Raspberry Pi: Processando mensagem '{msg_type}'")
        
        if msg_type == 'game_start':
            return self.handle_game_start()
        elif msg_type == 'player_move':
            return self.handle_player_move(data)
        elif msg_type == 'player_move_complete':
            return self.handle_player_move_complete(data)
        elif msg_type == 'ai_move_confirmed':
            return self.handle_ai_move_confirmed()
        
        return ""
    
    def handle_game_start(self) -> str:
        """Inicia novo jogo"""
        print("Raspberry Pi: Iniciando nova partida")
        
        self.board_manager = BoardStateManager()
        self.game_started = True
        
        # Enviar matriz inicial
        matrix = self.board_manager.get_board_matrix()
        return CommunicationProtocol.create_board_matrix_message(matrix)
    
    def handle_player_move(self, data: Dict) -> str:
        """Processa origem do movimento do jogador"""
        from_square = data.get('from', '').lower()
        
        print(f"Raspberry Pi: Calculando movimentos possíveis de {from_square}")
        
        # Simular cálculo de movimentos possíveis
        possible_moves = ['e2e4', 'e2e3', 'd2d4', 'd2d3']  # Exemplo
        best_move = possible_moves[0]
        alternatives = possible_moves[1:3]
        
        return CommunicationProtocol.create_move_options_message(
            best_move.upper(), 
            [move.upper() for move in alternatives]
        )
    
    def handle_player_move_complete(self, data: Dict) -> str:
        """Processa movimento completo do jogador"""
        from_square = data.get('from', '').lower()
        to_square = data.get('to', '').lower()
        move_uci = from_square + to_square
        
        print(f"Raspberry Pi: Processando movimento {move_uci}")
        
        # Atualizar tabuleiro
        if self.board_manager.update_board(move_uci):
            print("Raspberry Pi: Movimento válido, calculando resposta da IA...")
            
            # Simular movimento da IA
            ai_moves = ['e7e5', 'b8c6', 'g8f6']  # Exemplos
            ai_move = ai_moves[0]
            
            # Executar movimento da IA no tabuleiro
            self.board_manager.update_board(ai_move)
            
            from_sq = ai_move[:2].upper()
            to_sq = ai_move[2:4].upper()
            
            return CommunicationProtocol.create_ai_move_message(from_sq, to_sq)
        else:
            print("Raspberry Pi: Movimento inválido!")
            return ""
    
    def handle_ai_move_confirmed(self) -> str:
        """Processa confirmação do movimento da IA"""
        print("Raspberry Pi: Movimento da IA confirmado")
        
        # Verificar se o jogo terminou
        if self.board_manager.current_state.is_game_over():
            result = self.board_manager.current_state.result()
            print(f"Raspberry Pi: Jogo finalizado! Resultado: {result}")
        
        return ""

class CommunicationTester:
    """Testador da comunicação entre simuladores"""
    
    def __init__(self):
        self.esp32 = ESP32Simulator()
        self.raspberry = RaspberryPiSimulator()
        self.running = False
    
    def start_test(self):
        """Inicia teste de comunicação"""
        print("=== TESTE DE COMUNICAÇÃO ChessAI ===")
        
        self.esp32.start()
        self.raspberry.start()
        self.running = True
        
        # Menu interativo
        self.show_menu()
        
        while self.running:
            try:
                choice = input("\nEscolha uma opção: ").strip()
                
                if choice == '1':
                    self.test_game_start()
                elif choice == '2':
                    square = input("Digite a casa de origem (ex: E2): ").strip().upper()
                    if square:
                        self.test_player_move(square)
                elif choice == '3':
                    self.show_board_status()
                elif choice == '4':
                    self.test_full_game_sequence()
                elif choice == '0':
                    self.stop_test()
                else:
                    print("Opção inválida!")
                    
            except KeyboardInterrupt:
                self.stop_test()
    
    def show_menu(self):
        """Mostra menu de opções"""
        print("\n=== MENU DE TESTES ===")
        print("1. Iniciar jogo")
        print("2. Simular movimento do jogador")
        print("3. Mostrar status do tabuleiro")
        print("4. Teste sequência completa")
        print("0. Sair")
    
    def test_game_start(self):
        """Testa início de jogo"""
        print("\n--- Testando início de jogo ---")
        
        # ESP32 envia sinal de início
        self.esp32.send_game_start()
        
        # Raspberry Pi responde
        esp_message = self.esp32.get_response()
        if esp_message:
            rasp_response = self.raspberry.process_message(esp_message)
            if rasp_response:
                self.esp32.receive_message(rasp_response)
    
    def test_player_move(self, from_square: str):
        """Testa movimento do jogador"""
        print(f"\n--- Testando movimento do jogador de {from_square} ---")
        
        # ESP32 detecta movimento
        self.esp32.simulate_player_move(from_square)
        
        # Processar comunicação
        self.process_communication_cycle()
    
    def test_full_game_sequence(self):
        """Testa sequência completa de jogo"""
        print("\n--- Testando sequência completa ---")
        
        # Iniciar jogo
        self.test_game_start()
        time.sleep(1)
        
        # Alguns movimentos de exemplo
        moves = ['E2', 'D2', 'G1']
        
        for move in moves:
            print(f"\n>>> Testando movimento: {move}")
            self.test_player_move(move)
            time.sleep(2)
    
    def process_communication_cycle(self):
        """Processa um ciclo completo de comunicação"""
        max_cycles = 5
        cycle = 0
        
        while cycle < max_cycles:
            # Verificar resposta da ESP32
            esp_message = self.esp32.get_response()
            if esp_message:
                # Raspberry processa mensagem
                rasp_response = self.raspberry.process_message(esp_message)
                if rasp_response:
                    # ESP32 recebe resposta
                    self.esp32.receive_message(rasp_response)
                    cycle += 1
                else:
                    break
            else:
                break
            
            time.sleep(0.5)
    
    def show_board_status(self):
        """Mostra status atual do tabuleiro"""
        print("\n--- Status do Tabuleiro ---")
        status = self.raspberry.board_manager.get_board_status()
        
        for key, value in status.items():
            print(f"{key}: {value}")
        
        print(f"Histórico de movimentos: {self.raspberry.board_manager.move_history}")
    
    def stop_test(self):
        """Para os testes"""
        print("\nEncerrando testes...")
        self.running = False
        self.esp32.stop()
        self.raspberry.stop()

def main():
    """Função principal"""
    print("ChessAI - Simulador de Comunicação")
    print("Testando comunicação entre ESP32 e Raspberry Pi")
    
    tester = CommunicationTester()
    
    try:
        tester.start_test()
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário")
    finally:
        tester.stop_test()

if __name__ == "__main__":
    main()
