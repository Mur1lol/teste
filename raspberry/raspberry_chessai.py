#!/usr/bin/env python3
"""
ChessAI - Raspberry Pi Server
Sistema de xadrez físico interativo com ESP32 e Raspberry Pi
Autor: Sistema ChessAI
Data: 2025
"""

import serial
import json
import time
import threading
import chess
import chess.engine
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

class ConfigManager:
    """Gerenciador de configurações do ChessAI"""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Carrega configurações do arquivo JSON"""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
        
        # Configuração padrão se o arquivo não existir
        return {
            "serial": {"port": "/dev/ttyUSB0", "baudrate": 115200},
            "stockfish": {"path": "auto", "time_limit": 1.0},
            "logging": {"level": "INFO"},
            "hardware": {"sensor_threshold": 500}
        }
    
    def get(self, section: str, key: str, default=None):
        """Obtém valor de configuração"""
        return self.config.get(section, {}).get(key, default)

class ChessAIServer:
    """Servidor principal do sistema ChessAI"""
      def __init__(self, serial_port: str = '/dev/ttyUSB0', baudrate: int = 115200):
        """
        Inicializa o servidor ChessAI
        
        Args:
            serial_port: Porta serial para comunicação com ESP32
            baudrate: Taxa de transmissão serial
        """
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.serial_connection = None
        
        # Estado do jogo
        self.board = chess.Board()
        self.engine = None
        self.game_started = False
        self.waiting_for_move = False
        self.current_player_move = None
        
        # Logging (deve ser configurado primeiro)
        self.setup_logging()
        
        # Configurações do Stockfish (após logging)
        self.stockfish_path = self.find_stockfish_path()
        
        # Threads
        self.serial_thread = None
        self.running = False
        
        self.logger.info("ChessAI Server inicializado")
    
    def setup_logging(self) -> None:
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('chessai.log'),
                logging.StreamHandler()
            ]        )
        self.logger = logging.getLogger('ChessAI')
    
    def find_stockfish_path(self) -> str:
        """
        Encontra o caminho do Stockfish no sistema
        
        Returns:
            Caminho para o executável do Stockfish
        """
        possible_paths = [
            '/usr/games/stockfish',
            '/usr/local/bin/stockfish',
            '/usr/bin/stockfish',
            'stockfish',
            './stockfish',
            # Caminhos para Windows (caso queira testar localmente)
            'C:/Program Files/Stockfish/stockfish.exe',
            'C:/Stockfish/stockfish.exe',
            './stockfish.exe'
        ]
        
        for path in possible_paths:
            if Path(path).exists() or self.is_command_available(path):
                if hasattr(self, 'logger'):
                    self.logger.info(f"Stockfish encontrado em: {path}")
                else:
                    print(f"Stockfish encontrado em: {path}")
                return path
        
        if hasattr(self, 'logger'):
            self.logger.error("Stockfish não encontrado! Instale com: sudo apt-get install stockfish")
        else:
            print("ERRO: Stockfish não encontrado! Instale com: sudo apt-get install stockfish")
        return 'stockfish'  # Fallback
    
    def is_command_available(self, command: str) -> bool:
        """Verifica se um comando está disponível no sistema"""
        import subprocess
        try:
            subprocess.run([command, '--version'], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def setup_serial_connection(self) -> bool:
        """
        Estabelece conexão serial com a ESP32
        
        Returns:
            True se a conexão foi estabelecida com sucesso
        """
        try:
            self.serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=self.baudrate,
                timeout=1
            )
            time.sleep(2)  # Aguardar inicialização
            self.logger.info(f"Conexão serial estabelecida: {self.serial_port}")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Erro ao conectar na porta serial: {e}")
            return False
    
    def setup_chess_engine(self) -> bool:
        """
        Inicializa o engine de xadrez (Stockfish)
        
        Returns:
            True se o engine foi inicializado com sucesso
        """
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            # Configurar parâmetros do engine
            self.engine.configure({"Threads": 2, "Hash": 256})
            self.logger.info("Engine Stockfish inicializado")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Stockfish: {e}")
            return False
    
    def start_server(self) -> None:
        """Inicia o servidor ChessAI"""
        self.logger.info("Iniciando servidor ChessAI...")
        
        if not self.setup_serial_connection():
            self.logger.error("Falha ao estabelecer conexão serial")
            return
        
        if not self.setup_chess_engine():
            self.logger.error("Falha ao inicializar engine de xadrez")
            return
        
        self.running = True
        self.serial_thread = threading.Thread(target=self.serial_listener)
        self.serial_thread.daemon = True
        self.serial_thread.start()
        
        self.logger.info("Servidor ChessAI iniciado com sucesso!")
        self.logger.info("Aguardando sinal de início do jogo da ESP32...")
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.logger.info("Interrupção do usuário - encerrando servidor")
            self.stop_server()
    
    def stop_server(self) -> None:
        """Para o servidor ChessAI"""
        self.running = False
        
        if self.engine:
            self.engine.quit()
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        
        self.logger.info("Servidor ChessAI encerrado")
    
    def serial_listener(self) -> None:
        """Thread para escutar mensagens da ESP32"""
        while self.running:
            try:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    if line:
                        self.process_received_message(line)
            except Exception as e:
                self.logger.error(f"Erro no listener serial: {e}")
                time.sleep(1)
    
    def process_received_message(self, message: str) -> None:
        """
        Processa mensagens recebidas da ESP32
        
        Args:
            message: Mensagem JSON recebida
        """
        try:
            data = json.loads(message)
            message_type = data.get('type', '')
            
            self.logger.info(f"Mensagem recebida: {message_type}")
            
            if message_type == 'game_start':
                self.handle_game_start()
            elif message_type == 'player_move':
                self.handle_player_move_origin(data)
            elif message_type == 'player_move_complete':
                self.handle_player_move_complete(data)
            elif message_type == 'ai_move_confirmed':
                self.handle_ai_move_confirmed()
            else:
                self.logger.warning(f"Tipo de mensagem desconhecido: {message_type}")
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON: {e}")
        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem: {e}")
    def handle_game_start(self) -> None:
        """Manipula o início do jogo"""
        self.logger.info("=== INICIANDO NOVA PARTIDA DE XADREZ ===")
        
        # Reiniciar tabuleiro para posição inicial
        self.board = chess.Board()
        self.game_started = True
        self.waiting_for_move = False
        
        self.logger.info("Tabuleiro reiniciado para posição inicial")
        self.logger.info(f"FEN: {self.board.fen()}")
        
        # Enviar matriz inicial do tabuleiro (8x8 com 1s onde há peças, 0s onde está vazio)
        board_matrix = self.get_initial_board_matrix()
        self.logger.info("Enviando matriz inicial do tabuleiro para ESP32...")
        
        # Log da matriz para debug
        self.logger.info("Matriz do tabuleiro:")
        for i, row in enumerate(board_matrix):
            self.logger.info(f"Linha {8-i}: {row}")
        
        self.send_board_matrix(board_matrix)
    def handle_player_move_origin(self, data: Dict) -> None:
        """
        Manipula quando o jogador remove uma peça (origem do movimento)
        
        Args:
            data: Dados da mensagem contendo a posição de origem
        """
        from_square = data.get('from', '')
        
        if not from_square:
            self.logger.error("Posição de origem não especificada")
            return
        
        self.logger.info(f"=== JOGADOR REMOVEU PEÇA DE: {from_square} ===")
        
        try:
            # Converter notação para formato chess
            square = chess.parse_square(from_square.lower())
            piece = self.board.piece_at(square)
            
            if not piece:
                self.logger.error(f"Nenhuma peça encontrada em {from_square}")
                return
            
            # Verificar se é a vez do jogador (assumindo que jogador é sempre branco)
            if piece.color != chess.WHITE:
                self.logger.error(f"Peça em {from_square} não é do jogador (deve ser branca)")
                return
            
            if self.board.turn != chess.WHITE:
                self.logger.error("Não é a vez das brancas")
                return
            
            # Calcular movimentos possíveis desta casa
            possible_moves = self.get_possible_moves_from_square(square)
            
            if not possible_moves:
                self.logger.warning(f"Nenhum movimento possível para a peça em {from_square}")
                return
            
            self.logger.info(f"Encontrados {len(possible_moves)} movimentos possíveis")
            
            # Obter melhor movimento (usando IA para sugerir)
            best_move = self.get_best_move_from_options(possible_moves)
            alternatives = [move for move in possible_moves if move != best_move][:3]  # Máximo 3 alternativas
            
            self.logger.info(f"Melhor movimento sugerido: {best_move}")
            self.logger.info(f"Alternativas: {[str(move) for move in alternatives]}")
            
            # Enviar opções para ESP32
            self.send_move_options(best_move, alternatives)
            
            self.current_player_move = from_square
            self.waiting_for_move = True
            
        except ValueError as e:
            self.logger.error(f"Erro ao processar posição {from_square}: {e}")
    def handle_player_move_complete(self, data: Dict) -> None:
        """
        Manipula quando o jogador completa um movimento
        
        Args:
            data: Dados contendo origem e destino do movimento
        """
        from_square = data.get('from', '')
        to_square = data.get('to', '')
        
        if not from_square or not to_square:
            self.logger.error("Movimento incompleto recebido")
            return
        
        self.logger.info(f"=== MOVIMENTO DO JOGADOR COMPLETO: {from_square} → {to_square} ===")
        
        try:
            # Validar e executar movimento
            move_uci = from_square.lower() + to_square.lower()
            move = chess.Move.from_uci(move_uci)
            
            if move in self.board.legal_moves:
                self.board.push(move)
                self.logger.info(f"Movimento executado com sucesso: {move}")
                self.logger.info(f"Nova posição FEN: {self.board.fen()}")
                
                # Verificar fim de jogo
                if self.board.is_game_over():
                    self.handle_game_over()
                    return
                
                # Calcular e enviar movimento da IA imediatamente
                self.logger.info("Calculando movimento da IA...")
                self.calculate_and_send_ai_move()
                
            else:
                self.logger.error(f"Movimento ilegal: {move_uci}")
                self.logger.error("Movimentos legais disponíveis:")
                for legal_move in self.board.legal_moves:
                    if legal_move.from_square == chess.parse_square(from_square.lower()):
                        self.logger.error(f"  {legal_move}")
                
        except ValueError as e:
            self.logger.error(f"Erro ao processar movimento: {e}")
        
        self.waiting_for_move = False
    def handle_ai_move_confirmed(self) -> None:
        """Manipula confirmação de movimento da IA"""
        self.logger.info("=== MOVIMENTO DA IA CONFIRMADO PELO JOGADOR ===")
        self.waiting_for_move = False
        
        # Verificar fim de jogo após movimento da IA
        if self.board.is_game_over():
            self.handle_game_over()
        else:
            self.logger.info("Aguardando próximo movimento do jogador...")
            self.logger.info(f"Vez de: {'Brancas' if self.board.turn == chess.WHITE else 'Pretas'}")
            
            # Log do estado atual
            pieces_count = len(self.board.piece_map())
            self.logger.info(f"Peças no tabuleiro: {pieces_count}")
            
            if self.board.is_check():
                self.logger.info("REI EM XEQUE!")
    
    def handle_game_over(self) -> None:
        """Manipula fim de jogo"""
        result = self.board.result()
        
        self.logger.info("=== JOGO FINALIZADO ===")
        
        if result == "1-0":
            self.logger.info("🏆 RESULTADO: Brancas vencem! (Jogador venceu)")
        elif result == "0-1":
            self.logger.info("🏆 RESULTADO: Pretas vencem! (IA venceu)")
        elif result == "1/2-1/2":
            self.logger.info("🤝 RESULTADO: Empate!")
        else:
            self.logger.info(f"🎯 RESULTADO: {result}")
        
        # Informações detalhadas do fim de jogo
        if self.board.is_checkmate():
            self.logger.info("Motivo: Xeque-mate")
        elif self.board.is_stalemate():
            self.logger.info("Motivo: Afogamento (rei sem jogadas legais)")
        elif self.board.is_insufficient_material():
            self.logger.info("Motivo: Material insuficiente para dar mate")
        elif self.board.is_seventyfive_moves():
            self.logger.info("Motivo: Regra dos 75 movimentos")
        elif self.board.is_fivefold_repetition():
            self.logger.info("Motivo: Repetição de posição (5x)")
        
        self.logger.info(f"Total de movimentos: {self.board.fullmove_number}")
        self.logger.info(f"FEN final: {self.board.fen()}")
        
        self.game_started = False
    
    def get_initial_board_matrix(self) -> List[List[int]]:
        """
        Gera matriz inicial do tabuleiro (8x8) com 1 para casas com peças
        
        Returns:
            Matriz 8x8 representando o estado inicial do tabuleiro
        """
        matrix = []
        
        for rank in range(8, 0, -1):  # 8 a 1 (de cima para baixo)
            row = []
            for file in range(8):  # a-h
                square = chess.square(file, rank - 1)
                piece = self.board.piece_at(square)
                row.append(1 if piece else 0)
            matrix.append(row)
        
        return matrix
    
    def get_possible_moves_from_square(self, square: int) -> List[chess.Move]:
        """
        Obtém todos os movimentos possíveis a partir de uma casa
        
        Args:
            square: Casa do tabuleiro
            
        Returns:
            Lista de movimentos possíveis
        """
        possible_moves = []
        
        for move in self.board.legal_moves:
            if move.from_square == square:
                possible_moves.append(move)
        
        return possible_moves
    
    def get_best_move_from_options(self, moves: List[chess.Move]) -> chess.Move:
        """
        Escolhe o melhor movimento dentre as opções usando a IA
        
        Args:
            moves: Lista de movimentos possíveis
            
        Returns:
            Melhor movimento
        """
        if not moves:
            return None
        
        try:
            # Avaliar cada movimento
            best_move = moves[0]
            best_score = float('-inf')
            
            for move in moves:
                # Fazer movimento temporário
                self.board.push(move)
                
                # Avaliar posição
                info = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))
                score = info['score'].relative.score(mate_score=10000)
                
                # Desfazer movimento
                self.board.pop()
                
                # Atualizar melhor movimento
                if score > best_score:
                    best_score = score
                    best_move = move
            
            return best_move
            
        except Exception as e:
            self.logger.error(f"Erro ao avaliar movimentos: {e}")
            return moves[0]  # Retornar primeiro movimento como fallback    def calculate_and_send_ai_move(self) -> None:
        """Calcula e envia movimento da IA"""
        try:
            self.logger.info("=== CALCULANDO MOVIMENTO DA IA ===")
            
            # Obter melhor movimento da IA (pretas)
            result = self.engine.play(self.board, chess.engine.Limit(time=2.0))
            ai_move = result.move
            
            self.logger.info(f"IA escolheu movimento: {ai_move}")
            
            # Executar movimento no tabuleiro
            self.board.push(ai_move)
            self.logger.info(f"Movimento da IA executado: {ai_move}")
            self.logger.info(f"Nova posição FEN: {self.board.fen()}")
            
            # Converter para notação
            from_square = chess.square_name(ai_move.from_square).upper()
            to_square = chess.square_name(ai_move.to_square).upper()
            
            self.logger.info(f"=== IA MOVE: {from_square} → {to_square} ===")
            
            # Enviar movimento para ESP32
            self.send_ai_move(from_square, to_square)
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular movimento da IA: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def send_board_matrix(self, matrix: List[List[int]]) -> None:
        """
        Envia matriz do tabuleiro para ESP32
        
        Args:
            matrix: Matriz 8x8 do tabuleiro
        """
        # Converter matriz 2D para array 1D
        flat_matrix = [cell for row in matrix for cell in row]
        
        message = {
            "type": "board_matrix",
            "matrix": flat_matrix
        }
        
        self.send_json_message(message)
    
    def send_move_options(self, best_move: chess.Move, alternatives: List[chess.Move]) -> None:
        """
        Envia opções de movimento para ESP32
        
        Args:
            best_move: Melhor movimento
            alternatives: Movimentos alternativos
        """
        best_move_str = best_move.uci().upper()
        alternatives_str = [move.uci().upper() for move in alternatives[:4]]  # Máximo 4 alternativas
        
        message = {
            "type": "move_options",
            "best_move": best_move_str,
            "alternatives": alternatives_str
        }
        
        self.send_json_message(message)
    
    def send_ai_move(self, from_square: str, to_square: str) -> None:
        """
        Envia movimento da IA para ESP32
        
        Args:
            from_square: Casa de origem
            to_square: Casa de destino
        """
        message = {
            "type": "ai_move",
            "from": from_square,
            "to": to_square
        }
        
        self.send_json_message(message)
    
    def send_json_message(self, message: Dict) -> None:
        """
        Envia mensagem JSON para ESP32
        
        Args:
            message: Dicionário com dados da mensagem
        """
        try:
            if self.serial_connection and self.serial_connection.is_open:
                json_str = json.dumps(message) + '\n'
                self.serial_connection.write(json_str.encode('utf-8'))
                self.logger.debug(f"Mensagem enviada: {message['type']}")
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem: {e}")
    
    def get_board_status(self) -> Dict:
        """
        Obtém status atual do tabuleiro
        
        Returns:
            Dicionário com informações do jogo
        """
        return {
            "fen": self.board.fen(),
            "turn": "white" if self.board.turn == chess.WHITE else "black",
            "move_count": self.board.fullmove_number,
            "is_check": self.board.is_check(),
            "is_checkmate": self.board.is_checkmate(),
            "is_stalemate": self.board.is_stalemate(),
            "game_over": self.board.is_game_over()
        }

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ChessAI Server - Raspberry Pi')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Porta serial')
    parser.add_argument('--baudrate', type=int, default=115200, help='Taxa de transmissão')
    parser.add_argument('--debug', action='store_true', help='Modo debug')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Criar e iniciar servidor
    server = ChessAIServer(serial_port=args.port, baudrate=args.baudrate)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
    finally:
        server.stop_server()

if __name__ == "__main__":
    main()
