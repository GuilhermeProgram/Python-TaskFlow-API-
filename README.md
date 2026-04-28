# TaskFlow API 🐍

API REST de gerenciamento de tarefas construída com **Python + Flask + SQLite**.

## Tecnologias
- Python 3.10+
- Flask 3.x
- SQLite (banco embutido, sem configuração)
- JWT autenticação (implementação própria, sem biblioteca externa)
- Hash de senha com SHA-256 + salt

## Instalação

```bash
pip install -r requirements.txt
python app.py
```

## Endpoints

### Auth
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/auth/register` | Registrar usuário |
| POST | `/api/auth/login` | Login → retorna token JWT |

### Tasks (requer `Authorization: Bearer <token>`)
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/tasks` | Listar tarefas (`?status=pending&priority=high`) |
| GET | `/api/tasks/:id` | Buscar tarefa |
| POST | `/api/tasks` | Criar tarefa |
| PUT | `/api/tasks/:id` | Atualizar tarefa |
| DELETE | `/api/tasks/:id` | Deletar tarefa |
| PATCH | `/api/tasks/:id/complete` | Marcar como concluída |
| GET | `/api/stats` | Estatísticas do usuário |

## Exemplo de uso

```bash
# Registrar
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "joao", "password": "senha123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "joao", "password": "senha123"}'

# Criar tarefa
curl -X POST http://localhost:5000/api/tasks \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Estudar Python", "priority": "high"}'
```

## Estrutura
```
projeto1_python/
├── app.py          # Rotas e configuração Flask
├── database.py     # Inicialização SQLite
├── models.py       # UserModel e TaskModel
├── auth.py         # JWT geração/verificação
└── requirements.txt
```

## Conceitos demonstrados
- Arquitetura em camadas (routes → models → database)
- Autenticação JWT sem biblioteca externa
- Hash seguro de senhas com salt
- Filtros dinâmicos via query params
- Decorators Python para proteção de rotas
- CRUD completo com SQLite
