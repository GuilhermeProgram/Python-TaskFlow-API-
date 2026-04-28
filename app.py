"""
TaskFlow API - Sistema de Gerenciamento de Tarefas
Tecnologias: Python, Flask, SQLite, JWT
"""

from flask import Flask, request, jsonify
from database import init_db, get_db
from models import TaskModel, UserModel
from auth import token_required, generate_token
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'taskflow-secret-2024'

init_db()


# ─────────────────────────────────────────
#  AUTH ROUTES
# ─────────────────────────────────────────

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registrar novo usuário."""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username e password são obrigatórios'}), 400

    db = get_db()
    user = UserModel(db)

    if user.find_by_username(data['username']):
        return jsonify({'error': 'Usuário já existe'}), 409

    user_id = user.create(data['username'], data['password'])
    return jsonify({'message': 'Usuário criado com sucesso', 'id': user_id}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login e geração de token JWT."""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Credenciais inválidas'}), 400

    db = get_db()
    user = UserModel(db)
    account = user.authenticate(data['username'], data['password'])

    if not account:
        return jsonify({'error': 'Usuário ou senha incorretos'}), 401

    token = generate_token(account['id'], app.config['SECRET_KEY'])
    return jsonify({'token': token, 'username': account['username']}), 200


# ─────────────────────────────────────────
#  TASK ROUTES (protegidas por JWT)
# ─────────────────────────────────────────

@app.route('/api/tasks', methods=['GET'])
@token_required(app.config['SECRET_KEY'])
def get_tasks(current_user_id):
    """Listar todas as tarefas do usuário autenticado."""
    db = get_db()
    task = TaskModel(db)

    status = request.args.get('status')
    priority = request.args.get('priority')
    tasks = task.get_all(current_user_id, status=status, priority=priority)

    return jsonify({'tasks': tasks, 'total': len(tasks)}), 200


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@token_required(app.config['SECRET_KEY'])
def get_task(current_user_id, task_id):
    """Buscar uma tarefa específica."""
    db = get_db()
    task = TaskModel(db)
    result = task.get_by_id(task_id, current_user_id)

    if not result:
        return jsonify({'error': 'Tarefa não encontrada'}), 404

    return jsonify(result), 200


@app.route('/api/tasks', methods=['POST'])
@token_required(app.config['SECRET_KEY'])
def create_task(current_user_id):
    """Criar nova tarefa."""
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'error': 'Título é obrigatório'}), 400

    db = get_db()
    task = TaskModel(db)
    task_id = task.create(
        user_id=current_user_id,
        title=data['title'],
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        due_date=data.get('due_date')
    )

    return jsonify({'message': 'Tarefa criada com sucesso', 'id': task_id}), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@token_required(app.config['SECRET_KEY'])
def update_task(current_user_id, task_id):
    """Atualizar tarefa existente."""
    data = request.get_json()
    db = get_db()
    task = TaskModel(db)

    if not task.get_by_id(task_id, current_user_id):
        return jsonify({'error': 'Tarefa não encontrada'}), 404

    task.update(task_id, current_user_id, data)
    return jsonify({'message': 'Tarefa atualizada com sucesso'}), 200


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@token_required(app.config['SECRET_KEY'])
def delete_task(current_user_id, task_id):
    """Deletar tarefa."""
    db = get_db()
    task = TaskModel(db)

    if not task.get_by_id(task_id, current_user_id):
        return jsonify({'error': 'Tarefa não encontrada'}), 404

    task.delete(task_id, current_user_id)
    return jsonify({'message': 'Tarefa removida com sucesso'}), 200


@app.route('/api/tasks/<int:task_id>/complete', methods=['PATCH'])
@token_required(app.config['SECRET_KEY'])
def complete_task(current_user_id, task_id):
    """Marcar tarefa como concluída."""
    db = get_db()
    task = TaskModel(db)

    if not task.get_by_id(task_id, current_user_id):
        return jsonify({'error': 'Tarefa não encontrada'}), 404

    task.update(task_id, current_user_id, {'status': 'done'})
    return jsonify({'message': 'Tarefa concluída!'}), 200


# ─────────────────────────────────────────
#  STATS ROUTE
# ─────────────────────────────────────────

@app.route('/api/stats', methods=['GET'])
@token_required(app.config['SECRET_KEY'])
def get_stats(current_user_id):
    """Resumo estatístico das tarefas do usuário."""
    db = get_db()
    task = TaskModel(db)
    stats = task.get_stats(current_user_id)
    return jsonify(stats), 200


# ─────────────────────────────────────────
#  HEALTH CHECK
# ─────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}), 200


if __name__ == '__main__':
    print("🚀 TaskFlow API rodando em http://localhost:5000")
    app.run(debug=True, port=5000)
