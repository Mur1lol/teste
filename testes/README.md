# ChessAI - Testes

Esta pasta contém todos os scripts de teste para validar o funcionamento do sistema ChessAI.

## 📁 Arquivos

- `test_basic.py` - Teste básico de inicialização
- `test_communication.py` - Simulador de comunicação ESP32 ↔ Raspberry Pi  
- `test_final_integration.py` - Teste de integração completa
- `run_tests.py` - Script para executar todos os testes
- `README.md` - Esta documentação

## 🧪 Tipos de Teste

### 1. Teste Básico (`test_basic.py`)
Verifica se o servidor ChessAI pode ser inicializado corretamente.

**O que testa:**
- Importação de módulos
- Criação da instância do servidor
- Configuração do logger
- Detecção do Stockfish
- Métodos básicos do tabuleiro

**Execução:**
```bash
# Linux/Raspberry Pi
python3 test_basic.py

# Windows
py test_basic.py
```

### 2. Teste de Comunicação (`test_communication.py`)
Simula a comunicação entre ESP32 e Raspberry Pi sem hardware físico.

**O que testa:**
- Protocolo JSON de comunicação
- Fluxo completo de jogo
- Estados da máquina de estados
- Validação de movimentos
- Respostas da IA

**Execução:**
```bash
# Linux/Raspberry Pi
python3 test_communication.py

# Windows
py test_communication.py
```

**Menu interativo:**
```
=== MENU DE TESTES ===
1. Iniciar jogo
2. Simular movimento do jogador
3. Mostrar status do tabuleiro
4. Teste sequência completa
0. Sair
```

### 3. Teste de Integração (`test_final_integration.py`)
Teste completo que valida todo o sistema integrado.

**O que testa:**
- Inicialização completa
- Sequência de jogo real
- Múltiplos movimentos
- Tratamento de erros
- Performance

**Execução:**
```bash
# Linux/Raspberry Pi
python3 test_final_integration.py

# Windows
py test_final_integration.py
```

## 🚀 Execução Rápida

### Script Unificado:
```bash
# Executar todos os testes
# Linux/Raspberry Pi
python3 run_tests.py

# Windows
py run_tests.py
```

### Testes Individuais:
```bash
# Teste básico
py test_basic.py

# Teste de comunicação
py test_communication.py

# Teste de integração
py test_final_integration.py
```

## 📊 Interpretando Resultados

### ✅ Sucesso:
```
✅ Importação do ChessAIServer: OK
✅ Criação da instância: OK
✅ Logger configurado: OK
✅ Stockfish path: /usr/games/stockfish
🎉 Todos os testes básicos passaram!
```

### ❌ Erro de Dependência:
```
❌ Erro de importação: No module named 'chess'
Verifique se as dependências estão instaladas:
pip install python-chess pyserial
```

### ⚠️ Aviso:
```
⚠️ Stockfish path não encontrado (isso é normal se não estiver instalado)
```

## 🔧 Configuração dos Testes

### Variáveis de Ambiente:
```bash
# Definir porta serial para testes
export CHESSAI_TEST_PORT="/dev/ttyUSB0"

# Ativar modo verbose
export CHESSAI_DEBUG=true

# Simular hardware (sem ESP32 física)
export CHESSAI_SIMULATE=true
```

### Windows PowerShell:
```powershell
$env:CHESSAI_TEST_PORT="COM3"
$env:CHESSAI_DEBUG="true"
$env:CHESSAI_SIMULATE="true"
```

## 🐛 Solução de Problemas

### Erro: "Module not found"
```bash
# Instalar dependências
pip install -r ../raspberry/requirements.txt

# Verificar instalação
py -c "import chess, serial; print('OK')"
```

### Erro: "Permission denied" (Linux)
```bash
# Adicionar usuário ao grupo dialout
sudo usermod -a -G dialout $USER

# Ou dar permissão à porta
sudo chmod 666 /dev/ttyUSB0
```

### Stockfish não encontrado:
```bash
# Ubuntu/Raspberry Pi
sudo apt-get install stockfish

# Verificar
which stockfish
```

### Erro de timeout nos testes:
- Verificar se a ESP32 está conectada
- Verificar porta serial correta
- Executar em modo simulação

## 📝 Criando Novos Testes

### Template Básico:
```python
#!/usr/bin/env python3
"""
Novo Teste ChessAI
"""

import sys
import os
sys.path.append('../raspberry')

def test_minha_funcionalidade():
    """Testa uma funcionalidade específica"""
    try:
        # Seu código de teste aqui
        print("✅ Teste passou")
        return True
    except Exception as e:
        print(f"❌ Teste falhou: {e}")
        return False

if __name__ == "__main__":
    success = test_minha_funcionalidade()
    sys.exit(0 if success else 1)
```

## 📈 Relatórios de Teste

Os testes geram logs em:
- Console (saída padrão)
- Arquivo `test_results.log` (quando disponível)
- Relatório JSON `test_report.json` (teste de integração)

### Exemplo de Relatório:
```json
{
  "timestamp": "2025-06-11T23:30:00",
  "tests_run": 5,
  "tests_passed": 4,
  "tests_failed": 1,
  "duration": "12.34s",
  "details": {
    "test_basic": "PASS",
    "test_communication": "PASS", 
    "test_integration": "FAIL"
  }
}
```

## 🎯 Cobertura de Testes

### Funcionalidades Testadas:
- ✅ Inicialização do servidor
- ✅ Comunicação serial
- ✅ Protocolo JSON
- ✅ Movimentos de xadrez
- ✅ Integração com Stockfish
- ✅ Estados do jogo
- ✅ Tratamento de erros

### Ainda não testado:
- ⏳ Hardware físico (sensores/LEDs)
- ⏳ Performance sob carga
- ⏳ Recuperação de falhas
- ⏳ Múltiplas partidas consecutivas

## 🚀 Execução Automatizada

### CI/CD (exemplo):
```yaml
# .github/workflows/test.yml
name: ChessAI Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        sudo apt-get install stockfish
        pip install -r raspberry/requirements.txt
    - name: Run tests
      run: |
        cd testes
        python3 run_tests.py
```
