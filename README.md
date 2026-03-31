# 🤖 RPA Challenge Bot

Solução automatizada para os desafios de autenticação do RPA Challenge.

---

## 📋 Visão Geral

| Nível | Descrição | Tempo Médio |
|-------|-----------|-------------|
| **Easy** | Login simples com formulário | ~300ms |
| **Hard** | Certificado digital mTLS + challenge dinâmico via JavaScript | ~4s |
| **Extreme** | WebSocket + Proof-of-Work + AES-CBC decryption | ~6s |

---

## 🚀 Como Executar

### 1. Iniciar o Container Docker

```bash
docker pull doc9cloud/rpa-challenge:latest
docker run -d -p 3000:3000 -p 3001:3001 --name rpa-challenge doc9cloud/rpa-challenge:latest
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Executar os Bots

```bash
# Executar todos os desafios
python main.py all

# Executar individualmente
python main.py easy
python main.py hard
python main.py extreme
```

---

## 📁 Estrutura do Projeto

```
src/
├── config/                    # Configuração centralizada
│   ├── __init__.py
│   ├── log.py                 # Logging centralizado (get_logger, setup_logging)
│   └── settings.py            # Pydantic Settings + .env
├── controllers/               # Controllers (thin - orchestration)
│   ├── easy_controller.py
│   ├── hard_controller.py
│   └── extreme_controller.py
├── services/                  # Lógica de negócio
│   ├── easy_service.py        # Easy: POST /api/easy/login
│   ├── hard_service.py       # Hard: Playwright + mTLS + redirect
│   ├── extreme_service.py    # Extreme: WebSocket + PoW + AES
│   └── pow_service.py        # Proof-of-Work parallel solver
└── utils/                     # Helpers puros
    ├── crypto.py             # SHA256, AES-CBC, check_pow
    ├── http_client.py        # httpx wrapper (post)
    ├── websocket_client.py   # WebSocket connection
    ├── cert_utils.py         # PFX extraction, temp files
    └── exceptions.py         # Custom exceptions

.env                          # Configurações (credenciais, URLs)
main.py                   # Entry point
tests/
└── test_controllers.py       # Unit tests
```

---

## 🏗️ Arquitetura

### MVC Pattern

- **Controllers**: Thin - apenas orquestram, logam e medem tempo
- **Services**: TODA lógica de negócio (como resolver cada desafio)
- **Utils**: Helpers puros (crypto, HTTP, WebSocket, certificates)
- **Config**: Settings com Pydantic + .env

### Fluxo de Execução

```
main.py
    ↓
Controller (mede tempo, loga)
    ↓
Service (lógica de negócio)
    ↓
Utils (helpers: HTTP, crypto, websocket)
    ↓
Config (settings, logging)
```

---

## ⚙️ Configuração

### Arquivo `.env`

```env
# URLs
base_url=https://localhost:3000
hard_second_stage_url=https://localhost:3001

# Credenciais Easy
easy_username=easy_username
easy_password=easy_password

# Credenciais Hard
hard_username=hard_username
hard_password=hard_password

# Credenciais Extreme
extreme_username=extreme_username
extreme_password=extreme_password

# PoW Settings
pow_difficulty=5
pow_max_nonce=50000000
pow_chunk_size=50000
pow_num_workers=16

# Certificate
cert_password=test123
```

---

## 🔧 Como Funciona Cada Desafio

### Easy (~300ms)
1. POST `/api/easy/login` com username/password
2. Recebe token de autenticação

### Hard (~4s)
1. Lança browser headless (Playwright)
2. Extrai challenge values da página (`#challenge`, `#timestamp`, `#nonce`)
3. POST `/api/hard/login` com credentials + challenge
4. Recebe redirect URL para porta 3001
5. GET na redirect URL com certificado mTLS (client.pfx)
6. Recebe token final

### Extreme (~6s)
1. POST `/api/extreme/init` para iniciar sessão
2. Conecta ao WebSocket
3. Recebe PoW challenge (prefix + difficulty)
4. Resolve PoW usando multiprocessing Pool (16 workers)
5. Envia nonce via WebSocket
6. Recebe intermediate_token
7. POST `/api/extreme/verify-token` para obter payload criptografado
8. Decodifica AES-CBC para obter OTP
9. POST `/api/extreme/complete` com OTP
10. Recebe token final + proof_hash

---

## 📜 Certificados

O certificado `client.pfx` deve estar em `certs/client.pfx`. O caminho é configurado em `settings.py`.

```bash
# Extrair certificados do container
docker cp rpa-challenge:/app/certs/client.pfx ./certs/
docker cp rpa-challenge:/app/certs/ca.crt ./certs/
```

---

## ✅ Validação

```bash
# Rodar testes
python -m pytest tests/ -v

# Verificar lint
ruff check src/ tests/ main.py

# Executar todos os bots
python main.py all
```

---

## 🛠️ Desenvolvimento

### Custom Exceptions

```python
from src.utils import ApiError, BotError, PowError, CryptoError

raise ApiError("Mensagem", status_code=400)
raise BotError("Erro genérico")
raise PowError("PoW não encontrado")
raise CryptoError("Decryption failed")
```

### Logging

```python
from src.config import get_logger
logger = get_logger()
logger.info("Mensagem")
logger.error("Erro: %s", e)
```

---

## 📝 Output Exemplo

```
============================================================
  RPA Challenge - Easy Level
============================================================

============================================================
  RESULT: SUCCESS
  Token: a0bf26d72ab278553b3d753a15f114943d9b6923...
  Message: Autenticação bem-sucedida!
  Time: 316ms
============================================================
```
