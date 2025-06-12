#!/usr/bin/env python3
"""
ChessAI - Utilities
Utilitários auxiliares para o sistema ChessAI
"""

import json
import time
import chess
from typing import Dict, List, Tuple, Optional

class ChessNotationConverter:
    """Conversor entre diferentes notações de xadrez"""
    
    @staticmethod
    def square_to_coordinates(square_name: str) -> Tuple[int, int]:
        """
        Converte notação de casa (ex: A1) para coordenadas (row, col)
        
        Args:
            square_name: Nome da casa (ex: "A1", "H8")
            
        Returns:
            Tupla (row, col) onde row=0-7, col=0-7
        """
        col = ord(square_name[0].upper()) - ord('A')
        row = 8 - int(square_name[1])
        return (row, col)
    
    @staticmethod
    def coordinates_to_square(row: int, col: int) -> str:
        """
        Converte coordenadas para notação de casa
        
        Args:
            row: Linha (0-7)
            col: Coluna (0-7)
            
        Returns:
            Nome da casa (ex: "A1", "H8")
        """
        file = chr(ord('A') + col)
        rank = str(8 - row)
        return file + rank
    
    @staticmethod
    def uci_to_readable(uci_move: str) -> str:
        """
        Converte movimento UCI para formato legível
        
        Args:
            uci_move: Movimento em formato UCI (ex: "e2e4")
            
        Returns:
            Movimento legível (ex: "E2-E4")
        """
        if len(uci_move) >= 4:
            from_square = uci_move[:2].upper()
            to_square = uci_move[2:4].upper()
            return f"{from_square}-{to_square}"
        return uci_move.upper()

class BoardStateManager:
    """Gerenciador de estado do tabuleiro"""
    
    def __init__(self):
        self.current_state = chess.Board()
        self.move_history = []
    
    def update_board(self, move_uci: str) -> bool:
        """
        Atualiza o tabuleiro com um movimento
        
        Args:
            move_uci: Movimento em formato UCI
            
        Returns:
            True se o movimento foi válido e executado
        """
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.current_state.legal_moves:
                self.current_state.push(move)
                self.move_history.append(move_uci)
                return True
            return False
        except ValueError:
            return False
    
    def undo_last_move(self) -> bool:
        """
        Desfaz o último movimento
        
        Returns:
            True se foi possível desfazer
        """
        try:
            if self.move_history:
                self.current_state.pop()
                self.move_history.pop()
                return True
            return False
        except:
            return False
    
    def get_board_matrix(self) -> List[List[int]]:
        """
        Obtém matriz 8x8 do tabuleiro atual
        
        Returns:
            Matriz onde 1 = peça presente, 0 = casa vazia
        """
        matrix = []
        for rank in range(8, 0, -1):
            row = []
            for file in range(8):
                square = chess.square(file, rank - 1)
                piece = self.current_state.piece_at(square)
                row.append(1 if piece else 0)
            matrix.append(row)
        return matrix
    
    def get_piece_positions(self) -> Dict[str, List[str]]:
        """
        Obtém posições de todas as peças por cor
        
        Returns:
            Dicionário com listas de posições das peças brancas e pretas
        """
        white_pieces = []
        black_pieces = []
        
        for square in chess.SQUARES:
            piece = self.current_state.piece_at(square)
            if piece:
                square_name = chess.square_name(square).upper()
                if piece.color == chess.WHITE:
                    white_pieces.append(square_name)
                else:
                    black_pieces.append(square_name)
        
        return {
            "white": white_pieces,
            "black": black_pieces
        }

class CommunicationProtocol:
    """Protocolo de comunicação entre ESP32 e Raspberry Pi"""
    
    # Tipos de mensagem
    MESSAGE_TYPES = {
        'GAME_START': 'game_start',
        'BOARD_MATRIX': 'board_matrix',
        'PLAYER_MOVE': 'player_move',
        'PLAYER_MOVE_COMPLETE': 'player_move_complete',
        'MOVE_OPTIONS': 'move_options',
        'AI_MOVE': 'ai_move',
        'AI_MOVE_CONFIRMED': 'ai_move_confirmed',
        'ERROR': 'error',
        'STATUS': 'status'
    }
    
    @staticmethod
    def create_message(msg_type: str, data: Dict) -> str:
        """
        Cria mensagem JSON padronizada
        
        Args:
            msg_type: Tipo da mensagem
            data: Dados da mensagem
            
        Returns:
            String JSON formatada
        """
        message = {
            'type': msg_type,
            'timestamp': int(time.time()),
            **data
        }
        return json.dumps(message)
    
    @staticmethod
    def parse_message(json_str: str) -> Optional[Dict]:
        """
        Processa mensagem JSON recebida
        
        Args:
            json_str: String JSON
            
        Returns:
            Dicionário com dados da mensagem ou None se inválida
        """
        try:
            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def create_board_matrix_message(matrix: List[List[int]]) -> str:
        """Cria mensagem com matriz do tabuleiro"""
        flat_matrix = [cell for row in matrix for cell in row]
        return CommunicationProtocol.create_message(
            CommunicationProtocol.MESSAGE_TYPES['BOARD_MATRIX'],
            {'matrix': flat_matrix}
        )
    
    @staticmethod
    def create_move_options_message(best_move: str, alternatives: List[str]) -> str:
        """Cria mensagem com opções de movimento"""
        return CommunicationProtocol.create_message(
            CommunicationProtocol.MESSAGE_TYPES['MOVE_OPTIONS'],
            {
                'best_move': best_move,
                'alternatives': alternatives
            }
        )
    
    @staticmethod
    def create_ai_move_message(from_square: str, to_square: str) -> str:
        """Cria mensagem com movimento da IA"""
        return CommunicationProtocol.create_message(
            CommunicationProtocol.MESSAGE_TYPES['AI_MOVE'],
            {
                'from': from_square,
                'to': to_square
            }
        )

class LEDController:
    """Controlador virtual de LEDs para testes"""
    
    def __init__(self):
        self.led_states = {}
        for row in range(8):
            for col in range(8):
                self.led_states[(row, col)] = 'off'
    
    def set_led(self, row: int, col: int, color: str) -> None:
        """Define cor de um LED"""
        if 0 <= row < 8 and 0 <= col < 8:
            self.led_states[(row, col)] = color
            square = ChessNotationConverter.coordinates_to_square(row, col)
            print(f"LED {square} -> {color.upper()}")
    
    def clear_all(self) -> None:
        """Apaga todos os LEDs"""
        for row in range(8):
            for col in range(8):
                self.led_states[(row, col)] = 'off'
        print("Todos os LEDs apagados")
    
    def show_move_options(self, best_move: str, alternatives: List[str]) -> None:
        """Mostra opções de movimento nos LEDs"""
        self.clear_all()
        
        # Melhor movimento em verde
        if len(best_move) >= 4:
            to_square = best_move[2:4].upper()
            row, col = ChessNotationConverter.square_to_coordinates(to_square)
            self.set_led(row, col, 'green')
        
        # Alternativas em amarelo
        for alt_move in alternatives:
            if len(alt_move) >= 4:
                to_square = alt_move[2:4].upper()
                row, col = ChessNotationConverter.square_to_coordinates(to_square)
                self.set_led(row, col, 'yellow')
    
    def show_ai_move(self, from_square: str, to_square: str) -> None:
        """Mostra movimento da IA"""
        from_row, from_col = ChessNotationConverter.square_to_coordinates(from_square)
        to_row, to_col = ChessNotationConverter.square_to_coordinates(to_square)
        
        self.set_led(from_row, from_col, 'blue_solid')
        self.set_led(to_row, to_col, 'blue_blink')

class GameValidator:
    """Validador de regras e movimentos do jogo"""
    
    @staticmethod
    def is_valid_square(square_name: str) -> bool:
        """Verifica se uma notação de casa é válida"""
        if len(square_name) != 2:
            return False
        
        file = square_name[0].upper()
        rank = square_name[1]
        
        return 'A' <= file <= 'H' and '1' <= rank <= '8'
    
    @staticmethod
    def is_valid_move_format(move_str: str) -> bool:
        """Verifica se um movimento está no formato correto"""
        if len(move_str) < 4:
            return False
        
        from_square = move_str[:2]
        to_square = move_str[2:4]
        
        return (GameValidator.is_valid_square(from_square) and 
                GameValidator.is_valid_square(to_square))
    
    @staticmethod
    def validate_board_setup(matrix: List[List[int]]) -> Tuple[bool, str]:
        """
        Valida se a configuração do tabuleiro está correta
        
        Args:
            matrix: Matriz 8x8 do tabuleiro
            
        Returns:
            Tupla (válido, mensagem de erro)
        """
        if len(matrix) != 8:
            return False, "Tabuleiro deve ter 8 linhas"
        
        for i, row in enumerate(matrix):
            if len(row) != 8:
                return False, f"Linha {i+1} deve ter 8 colunas"
            
            for j, cell in enumerate(row):
                if cell not in [0, 1]:
                    return False, f"Célula ({i+1},{j+1}) deve ser 0 ou 1"
        
        # Verificar número de peças (deve ser 32 no início)
        total_pieces = sum(sum(row) for row in matrix)
        if total_pieces != 32:
            return False, f"Número incorreto de peças: {total_pieces} (esperado: 32)"
        
        return True, "Configuração válida"

class TestUtilities:
    """Utilitários para testes do sistema"""
    
    @staticmethod
    def create_test_board_matrix() -> List[List[int]]:
        """Cria matriz de teste do tabuleiro inicial"""
        matrix = []
        
        # Linhas com peças (linhas 1, 2, 7, 8 do tabuleiro)
        piece_rows = [
            [1, 1, 1, 1, 1, 1, 1, 1],  # Linha 8 (peças pretas)
            [1, 1, 1, 1, 1, 1, 1, 1],  # Linha 7 (peões pretos)
            [0, 0, 0, 0, 0, 0, 0, 0],  # Linha 6 (vazia)
            [0, 0, 0, 0, 0, 0, 0, 0],  # Linha 5 (vazia)
            [0, 0, 0, 0, 0, 0, 0, 0],  # Linha 4 (vazia)
            [0, 0, 0, 0, 0, 0, 0, 0],  # Linha 3 (vazia)
            [1, 1, 1, 1, 1, 1, 1, 1],  # Linha 2 (peões brancos)
            [1, 1, 1, 1, 1, 1, 1, 1]   # Linha 1 (peças brancas)
        ]
        
        return piece_rows
    
    @staticmethod
    def simulate_sensor_reading(matrix: List[List[int]], noise_level: float = 0.1) -> List[List[int]]:
        """
        Simula leitura de sensores com ruído
        
        Args:
            matrix: Matriz real do tabuleiro
            noise_level: Nível de ruído (0.0 a 1.0)
            
        Returns:
            Matriz com valores simulados de sensores
        """
        import random
        
        sensor_matrix = []
        for row in matrix:
            sensor_row = []
            for cell in row:
                # Simular valores de sensor (0-1023 para ADC de 10 bits)
                if cell == 1:  # Peça presente
                    base_value = 800
                    noise = random.randint(-int(noise_level * 200), int(noise_level * 200))
                    sensor_value = max(0, min(1023, base_value + noise))
                else:  # Casa vazia
                    base_value = 200
                    noise = random.randint(-int(noise_level * 100), int(noise_level * 100))
                    sensor_value = max(0, min(1023, base_value + noise))
                
                sensor_row.append(sensor_value)
            sensor_matrix.append(sensor_row)
        
        return sensor_matrix

# Exemplo de uso das utilitários
if __name__ == "__main__":
    print("=== ChessAI Utilities - Demonstração ===")
    
    # Testar conversor de notação
    converter = ChessNotationConverter()
    print(f"A1 -> coordenadas: {converter.square_to_coordinates('A1')}")
    print(f"Coordenadas (0,0) -> casa: {converter.coordinates_to_square(7, 7)}")
    print(f"UCI 'e2e4' -> legível: {converter.uci_to_readable('e2e4')}")
    
    # Testar gerenciador de estado
    board_manager = BoardStateManager()
    print(f"Movimento e2e4 válido: {board_manager.update_board('e2e4')}")
    print(f"Posições das peças: {board_manager.get_piece_positions()}")
    
    # Testar protocolo de comunicação
    protocol = CommunicationProtocol()
    msg = protocol.create_message('test', {'data': 'exemplo'})
    print(f"Mensagem criada: {msg}")
    
    # Testar controlador de LED
    led_controller = LEDController()
    led_controller.show_move_options('e2e4', ['e2e3', 'd2d5'])
    
    # Testar validador
    validator = GameValidator()
    test_matrix = TestUtilities.create_test_board_matrix()
    valid, msg = validator.validate_board_setup(test_matrix)
    print(f"Validação do tabuleiro: {valid} - {msg}")
    
    print("=== Demonstração concluída ===")
