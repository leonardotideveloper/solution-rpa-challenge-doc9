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
23:10:43 [INFO] src.controllers.easy_controller: [easy_controller] Starting...
23:10:43 [INFO] src.services.easy_service: [easy_service] Executing login...
23:10:43 [INFO] httpx: HTTP Request: POST https://localhost:3000/api/easy/login "HTTP/1.1 200 OK"
23:10:43 [INFO] src.services.easy_service: [easy_service] Login successful
23:10:43 [INFO] src.controllers.easy_controller: [easy_controller] Completed successfully

============================================================
  RESULT: SUCCESS
  Token: c108490b6e9ca638ce48b3fce33737089cc8d438...
  Message: Autenticação bem-sucedida!
  Time: 126ms
============================================================



============================================================
  RPA Challenge - Hard Level
============================================================
23:10:43 [INFO] src.controllers.hard_controller: [hard_controller] Starting...
23:10:43 [INFO] src.services.hard_service: [hard_service] Step 1: Launching headless browser...
23:10:44 [INFO] src.services.hard_service: [hard_service] Step 2: Navigating to /hard/
23:10:44 [INFO] src.services.hard_service: [hard_service] Step 3: Extracting challenge values from page...
23:10:44 [INFO] src.services.hard_service: [hard_service] Challenge: da0f1db68d432b77405f2ecb9777230c...
23:10:44 [INFO] src.services.hard_service: [hard_service] Timestamp: 1775009444494
23:10:44 [INFO] src.services.hard_service: [hard_service] Nonce: mqkn5rxztzl
23:10:44 [INFO] src.services.hard_service: [hard_service] Step 4: Submitting credentials to /api/hard/login...
23:10:44 [INFO] httpx: HTTP Request: POST https://localhost:3000/api/hard/login "HTTP/1.1 200 OK"
23:10:44 [INFO] src.services.hard_service: [hard_service] Login successful, redirect: https://localhost:3001/verify?token=60ed3508ced92187e1c8f9f775b45ac5e5414792f044d8f080d754b586e67be6
23:10:44 [INFO] src.services.hard_service: [hard_service] TTL: 30s
23:10:44 [INFO] src.services.hard_service: [hard_service] Step 5: Following redirect to port 3001 (mTLS)...
23:10:44 [INFO] src.services.hard_service: [hard_service] Step 6: Making mTLS request to port 3001...
23:10:44 [INFO] httpx: HTTP Request: GET https://localhost:3001/verify?token=60ed3508ced92187e1c8f9f775b45ac5e5414792f044d8f080d754b586e67be6 "HTTP/1.1 200 OK"
23:10:44 [INFO] src.services.hard_service: [hard_service] Response status: 200
23:10:44 [INFO] src.services.hard_service: [hard_service] mTLS authentication successful
23:10:44 [INFO] src.controllers.hard_controller: [hard_controller] Completed successfully

============================================================
  RESULT: SUCCESS
  Token: 60ed3508ced92187e1c8f9f775b45ac5e5414792...
  Message: Credenciais válidas! Agora apresente seu certificado digital.
  Time: 1480ms
============================================================



============================================================
  RPA Challenge - Extreme Level
============================================================
23:10:44 [INFO] src.controllers.extreme_controller: [extreme_controller] Starting...
23:10:44 [INFO] src.services.extreme_service: [extreme_service] Step 1: Initializing session...
23:10:45 [INFO] httpx: HTTP Request: POST https://localhost:3000/api/extreme/init "HTTP/1.1 200 OK"
23:10:45 [INFO] src.services.extreme_service: [extreme_service] Session ID: 9e09e0fe-d350-4144-be40-fb90e3993910
23:10:45 [INFO] src.services.extreme_service: [extreme_service] Step 2: Connecting to WebSocket...
23:10:45 [INFO] src.services.extreme_service: [extreme_service] Step 3: Receiving PoW challenge...
23:10:45 [INFO] src.services.extreme_service: [extreme_service] Challenge: d8bb68f8b5d1a303..., difficulty: 5
23:10:45 [INFO] src.services.extreme_service: [extreme_service] Step 4: Solving PoW...
23:10:45 [INFO] src.services.pow_service: [pow_service] Solving PoW with difficulty=5
23:10:47 [INFO] src.services.pow_service: [pow_service] Solution found: nonce=605452
23:10:47 [INFO] src.services.extreme_service: [extreme_service] Nonce: 605452, Hash: 00000270bd1766bdfb027d873244d35b...
23:10:47 [INFO] src.services.extreme_service: [extreme_service] Step 5: Sending PoW solution...
23:10:47 [INFO] src.services.extreme_service: [extreme_service] Step 6: Receiving intermediate_token...
23:10:47 [INFO] src.services.extreme_service: [extreme_service] intermediate_token: 41a24f8eb3c546c7f9ae07f1d2ff9443...
23:10:47 [INFO] src.services.extreme_service: [extreme_service] Step 7: Verifying token and getting encrypted payload...
23:10:47 [INFO] httpx: HTTP Request: POST https://localhost:3000/api/extreme/verify-token "HTTP/1.1 200 OK"
23:10:47 [INFO] src.services.extreme_service: [extreme_service] Encrypted payload: 4726bfa0c33962162a7b91f4a082ca46:6e82effab062f3701...
23:10:47 [INFO] src.services.extreme_service: [extreme_service] Step 8: Decrypting payload to get OTP...
23:10:47 [INFO] src.services.extreme_service: [extreme_service] OTP: 982744
23:10:47 [INFO] src.services.extreme_service: [extreme_service] Step 9: Submitting final authentication...
23:10:47 [INFO] httpx: HTTP Request: POST https://localhost:3000/api/extreme/complete "HTTP/1.1 200 OK"
23:10:47 [INFO] src.services.extreme_service: [extreme_service] Authentication completed successfully
23:10:47 [INFO] src.controllers.extreme_controller: [extreme_controller] Completed successfully

============================================================
  RESULT: SUCCESS
  Token: f59424068abfaa8f27e3ee795b853fd27f728f1f...
  Proof Hash: 3ab3dc4010f476292bd4e860200f825c590f381da3d6116b87315d7727281e28
  Time: 3033ms
============================================================



============================================================
  SUMMARY
============================================================
  [PASS] easy: 126ms
  [PASS] hard: 1480ms
  [PASS] extreme: 3033ms
```
