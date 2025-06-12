#!/usr/bin/env python3
"""
ChessAI - Executor de Testes Unificado
Executa todos os testes do sistema ChessAI
"""

import sys
import os
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime

class TestRunner:
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'duration': 0,
            'details': {}
        }
        
    def run_test(self, test_file: str, description: str) -> bool:
        """Executa um teste individual"""
        print(f"\n{'='*60}")
        print(f"🧪 {description}")
        print(f"📄 Arquivo: {test_file}")
        print(f"{'='*60}")
        
        test_path = self.test_dir / test_file
        
        if not test_path.exists():
            print(f"❌ Arquivo de teste não encontrado: {test_file}")
            return False
        
        try:
            # Determinar comando Python
            python_cmd = 'py' 
            
            start_time = time.time()
            
            # Executar teste
            result = subprocess.run(
                [python_cmd, str(test_path)],
                capture_output=True,
                text=True,
                timeout=120  # 2 minutos de timeout
            )
            
            duration = time.time() - start_time
            
            # Mostrar saída
            if result.stdout:
                print("📤 Saída:")
                print(result.stdout)
            
            if result.stderr:
                print("⚠️ Erros/Avisos:")
                print(result.stderr)
            
            # Verificar resultado
            success = result.returncode == 0
            
            print(f"\n⏱️ Tempo: {duration:.2f}s")
            print(f"🎯 Resultado: {'✅ PASSOU' if success else '❌ FALHOU'}")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout! Teste demorou mais que 2 minutos")
            return False
        except Exception as e:
            print(f"❌ Erro ao executar teste: {e}")
            return False
    
    def run_all_tests(self):
        """Executa todos os testes disponíveis"""
        print("🚀 ChessAI - Executor de Testes")
        print(f"📍 Diretório: {self.test_dir}")
        print(f"🕒 Iniciado em: {datetime.now().strftime('%H:%M:%S')}")
        
        start_time = time.time()
        
        # Lista de testes para executar
        tests = [
            ('test_basic.py', 'Teste Básico - Inicialização'),
            ('test_communication.py', 'Teste de Comunicação - Simulação'),
            ('test_final_integration.py', 'Teste de Integração Completa')
        ]
        
        # Executar cada teste
        for test_file, description in tests:
            self.results['tests_run'] += 1
            
            success = self.run_test(test_file, description)
            
            if success:
                self.results['tests_passed'] += 1
                self.results['details'][test_file.replace('.py', '')] = 'PASS'
            else:
                self.results['tests_failed'] += 1
                self.results['details'][test_file.replace('.py', '')] = 'FAIL'
        
        # Calcular tempo total
        total_time = time.time() - start_time
        self.results['duration'] = f"{total_time:.2f}s"
        
        # Mostrar resumo
        self.show_summary()
        
        # Salvar relatório
        self.save_report()
        
        # Retornar código de saída
        return 0 if self.results['tests_failed'] == 0 else 1
    
    def show_summary(self):
        """Mostra resumo dos resultados"""
        print(f"\n{'='*60}")
        print("📊 RESUMO DOS TESTES")
        print(f"{'='*60}")
        
        print(f"🏃 Testes executados: {self.results['tests_run']}")
        print(f"✅ Testes aprovados: {self.results['tests_passed']}")
        print(f"❌ Testes falharam: {self.results['tests_failed']}")
        print(f"⏱️ Tempo total: {self.results['duration']}")
        
        if self.results['tests_failed'] == 0:
            print(f"\n🎉 TODOS OS TESTES PASSARAM! 🎉")
        else:
            print(f"\n⚠️ {self.results['tests_failed']} teste(s) falharam")
        
        print(f"\n📋 Detalhes:")
        for test, result in self.results['details'].items():
            status = "✅" if result == "PASS" else "❌"
            print(f"   {status} {test}: {result}")
    
    def save_report(self):
        """Salva relatório em arquivo JSON"""
        try:
            report_file = self.test_dir / 'test_report.json'
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Relatório salvo: {report_file}")
            
        except Exception as e:
            print(f"⚠️ Não foi possível salvar relatório: {e}")

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    # Adicionar pasta raspberry ao path
    raspberry_dir = Path(__file__).parent.parent / 'raspberry'
    sys.path.insert(0, str(raspberry_dir))
    
    dependencies = ['chess', 'serial', 'json', 'threading']
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}: OK")
        except ImportError:
            print(f"❌ {dep}: NÃO ENCONTRADO")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️ Dependências não encontradas: {missing}")
        print("Execute: pip install -r ../raspberry/requirements.txt")
        return False
    
    print("✅ Todas as dependências estão instaladas")
    return True

def main():
    """Função principal"""
    print("🎯 ChessAI - Sistema de Testes Automatizado")
    print("=" * 60)
    
    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Falha na verificação de dependências")
        return 1
    
    # Executar testes
    runner = TestRunner()
    
    try:
        return runner.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️ Testes interrompidos pelo usuário")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\n👋 Execução finalizada com código: {exit_code}")
    sys.exit(exit_code)
