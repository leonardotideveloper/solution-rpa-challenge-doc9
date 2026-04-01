# 🤖 RPA Challenge Bot

Solução automatizada para os desafios de autenticação do RPA Challenge.

---

## 📋 Visão Geral

| Nível | Descrição | Tempo Médio |
|-------|-----------|-------------|
| **Easy** | Login simples com formulário | ~200ms |
| **Hard** | Certificado digital mTLS + challenge dinâmico via JavaScript | ~2s |
| **Extreme** | WebSocket + Proof-of-Work + AES-CBC decryption | ~3s |

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
# Executar todos os desafios (default)
python main.py

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

### Easy (~200ms)
1. POST `/api/easy/login` com username/password
2. Recebe token de autenticação

### Hard (~2s)
1. Lança browser headless (Playwright)
2. Extrai challenge values da página (`#challenge`, `#timestamp`, `#nonce`)
3. POST `/api/hard/login` com credentials + challenge
4. Recebe redirect URL para porta 3001
5. GET na redirect URL com certificado mTLS (client.pfx)
6. Extrai token e metadados do HTML de resposta

### Extreme (~3s)
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
python main.py
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
00:16:25 [INFO] src.controllers.easy_controller: [easy_controller] Starting...
00:16:25 [INFO] src.services.easy_service: [easy_service] Executing login...
00:16:25 [INFO] httpx: HTTP Request: POST https://localhost:3000/api/easy/login "HTTP/1.1 200 OK"
00:16:25 [INFO] src.services.easy_service: [easy_service] Login successful
00:16:25 [INFO] src.controllers.easy_controller: [easy_controller] Completed successfully

============================================================
  RESULT: SUCCESS
  Token: 5a37965fc6719f1375832cd2ef3f461436c2a8f9...
  Message: Autenticação bem-sucedida!
  Time: 160ms
============================================================



============================================================
  RPA Challenge - Hard Level
============================================================
00:16:25 [INFO] src.controllers.hard_controller: [hard_controller] Starting...
00:16:25 [INFO] src.services.hard_service: [hard_service] Step 1: Launching headless browser...
00:16:38 [INFO] src.services.hard_service: [hard_service] Step 2: Navigating to /hard/
00:16:39 [INFO] src.services.hard_service: [hard_service] Step 3: Extracting challenge values from page...
00:16:39 [INFO] src.services.hard_service: [hard_service] Challenge: 9fc7f637ddad4d686c34c53cc350c947...
00:16:39 [INFO] src.services.hard_service: [hard_service] Timestamp: 1775013399006
00:16:39 [INFO] src.services.hard_service: [hard_service] Nonce: 1xdh2uiwgpy
00:16:39 [INFO] src.services.hard_service: [hard_service] Step 4: Submitting credentials to /api/hard/login...
00:16:39 [INFO] httpx: HTTP Request: POST https://localhost:3000/api/hard/login "HTTP/1.1 200 OK"
00:16:39 [INFO] src.services.hard_service: [hard_service] Login successful, redirect: https://localhost:3001/verify?token=19918c711a482c61761e60f6584859e2016cb7cdbd16a53ea3681e1c9007d3b0
00:16:39 [INFO] src.services.hard_service: [hard_service] TTL: 30s
00:16:39 [INFO] src.services.hard_service: [hard_service] Step 5: Following redirect to port 3001 (mTLS)...
00:16:39 [INFO] src.services.hard_service: [hard_service] Step 6: Making mTLS request to port 3001...
00:16:39 [INFO] httpx: HTTP Request: GET https://localhost:3001/verify?token=19918c711a482c61761e60f6584859e2016cb7cdbd16a53ea3681e1c9007d3b0 "HTTP/1.1 200 OK"
00:16:39 [INFO] src.services.hard_service: [hard_service] Response status: 200
00:16:39 [INFO] src.services.hard_service: [hard_service] mTLS response: success=True certificate_cn='doc9-rpa-candidate' token='21aac3750dd41f93...' elapsed_ms=199 level='hard' message='Certificado digital validado com sucesso.'
00:16:39 [INFO] src.controllers.hard_controller: [hard_controller] Completed successfully

============================================================
  RESULT: SUCCESS
  Token: 21aac3750dd41f93......
  Message: Certificado digital validado com sucesso.
  Certificate CN: doc9-rpa-candidate
  Level: hard
  Server Time: 199ms
  Time: 199ms
============================================================



============================================================
  RPA Challenge - Extreme Level
============================================================
00:16:39 [INFO] src.controllers.extreme_controller: [extreme_controller] Starting...
00:16:39 [INFO] src.services.extreme_service: [extreme_service] Step 1: Initializing session...
00:16:39 [INFO] httpx: HTTP Request: POST https://localhost:3000/api/extreme/init "HTTP/1.1 200 OK"
00:16:39 [INFO] src.services.extreme_service: [extreme_service] Session ID: 07f46b90-3485-439d-8dfe-776af7e061a4
00:16:39 [INFO] src.services.extreme_service: [extreme_service] Step 2: Connecting to WebSocket...
00:16:39 [INFO] src.services.extreme_service: [extreme_service] Step 3: Receiving PoW challenge...
00:16:39 [INFO] src.services.extreme_service: [extreme_service] Challenge: 8b3a292855ccf258..., difficulty: 5
00:16:39 [INFO] src.services.extreme_service: [extreme_service] Step 4: Solving PoW...
00:16:39 [INFO] src.services.pow_service: [pow_service] Solving PoW with difficulty=5
00:16:42 [INFO] src.services.pow_service: [pow_service] Solution found: nonce=182664
00:16:42 [INFO] src.services.extreme_service: [extreme_service] Nonce: 182664, Hash: 000005ac68a71793427d8b27314fd17b...
00:16:42 [INFO] src.services.extreme_service: [extreme_service] Step 5: Sending PoW solution...
00:16:42 [INFO] src.services.extreme_service: [extreme_service] Step 6: Receiving intermediate_token...
00:16:42 [INFO] src.services.extreme_service: [extreme_service] intermediate_token: dbcbe9bbd27e33aba727883baad26a9d...
00:16:42 [INFO] src.services.extreme_service: [extreme_service] Step 7: Verifying token and getting encrypted payload...
00:16:42 [INFO] httpx: HTTP Request: POST https://localhost:3000/api/extreme/verify-token "HTTP/1.1 200 OK"
00:16:42 [INFO] src.services.extreme_service: [extreme_service] Encrypted payload: 0f8fbfcb18406537536b075c0b4079e1:ea144726952d04c20...
00:16:42 [INFO] src.services.extreme_service: [extreme_service] Step 8: Decrypting payload to get OTP...
00:16:42 [INFO] src.services.extreme_service: [extreme_service] OTP: 162568
00:16:42 [INFO] src.services.extreme_service: [extreme_service] Step 9: Submitting final authentication...
00:16:42 [INFO] httpx: HTTP Request: POST https://localhost:3000/api/extreme/complete "HTTP/1.1 200 OK"
00:16:42 [INFO] src.services.extreme_service: [extreme_service] Authentication completed successfully
00:16:42 [INFO] src.controllers.extreme_controller: [extreme_controller] Completed successfully

============================================================
  RESULT: SUCCESS
  Token: 4f143d537b2f5dc051e85c0eba64fbd02c3979cf...
  Proof Hash: f1af3ee4d38de4d339f3788a45666ea78022dd145ed7a7b3b030077f600f5413
  Time: 2611ms
============================================================

============================================================
  SUMMARY
============================================================
  [PASS] easy: 160ms
  [PASS] hard: 199ms
  [PASS] extreme: 2611ms
```
