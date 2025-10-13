import asyncio
import json
import random


        # Create a list of tasks to send the message to all clients concurrently.

# Quiz TCP Server

# Quiz HTTP Server


import socket
import random
import urllib.parse
import time
import threading

# Perguntas com alternativas
QUESTIONS = [
    {
        "question": "Qual é a capital da França?",
        "alternatives": ["Paris", "Londres", "Berlim", "Roma"],
        "answer": "Paris"
    },
    {
        "question": "Qual planeta é conhecido como o Planeta Vermelho?",
        "alternatives": ["Terra", "Marte", "Júpiter", "Saturno"],
        "answer": "Marte"
    },
    {
        "question": "Qual é o resultado de 5 + 7?",
        "alternatives": ["10", "12", "13", "14"],
        "answer": "12"
    },
    {
        "question": "Quem escreveu 'Dom Quixote'?",
        "alternatives": ["Machado de Assis", "Miguel de Cervantes", "José Saramago", "Fernando Pessoa"],
        "answer": "Miguel de Cervantes"
    },
]



scores = {}
current_question_idx = 0
players_answers = {}
current_question = None
question_start_time = None
QUESTION_TIMEOUT = 15  # segundos
MIN_PLAYERS = 2
connected_players = set()
quiz_started = False

def build_html(name, question, scores, msg="", time_left=QUESTION_TIMEOUT, show_timeout=False, waiting=False):
    scoreboard = "<ul>" + "".join(f"<li>{n}: {s}</li>" for n, s in scores.items()) + "</ul>"
    timeout_msg = "<p style='color:red'>Tempo acabou!</p>" if show_timeout else ""
    if waiting:
        return f"""
        <html>
        <head><title>Quiz HTTP</title></head>
        <body>
            <h1>Quiz HTTP</h1>
            <form method='POST'>
                <label>Seu nome: <input name='name' value='{name}' required></label><br><br>
                <button type='submit'>Entrar</button>
            </form>
            <h2>Sala de espera</h2>
            <p>Aguardando outros jogadores... ({len(connected_players)}/{MIN_PLAYERS})</p>
            <h2>Placar</h2>
            {scoreboard}
            <script>
            setTimeout(function() {{ location.reload(); }}, 2000);
            </script>
        </body>
        </html>
        """
    # Quiz rodando
    return f"""
    <html>
    <head><title>Quiz HTTP</title></head>
    <body>
        <h1>Quiz HTTP</h1>
        <form method='POST'>
            <label>Seu nome: <input name='name' value='{name}' required></label><br><br>
            <b>Pergunta:</b> {question}<br>
            <input name='answer' placeholder='Sua resposta' required>
            <button type='submit'>Enviar</button>
        </form>
        <h2>Placar</h2>
        {scoreboard}
        <p style='color:green'>{msg}</p>
        {timeout_msg}
        <h3>Tempo restante: <span id='timer'>{int(time_left)}</span> segundos</h3>
        <script>
        let t = {int(time_left)};
        let timer = document.getElementById('timer');
        let reloading = false;
        setInterval(function() {{
            if (t > 0) {{ t--; timer.textContent = t; }}
            if (t === 0 && !reloading) {{
                reloading = true;
                setTimeout(function() {{ location.reload(); }}, 1500);
            }}
        }}, 1000);
        </script>
    </body>
    </html>
    """

def get_question_json():
    q = QUESTIONS[current_question_idx]
    return json.dumps({
        "question": q["question"],
        "alternatives": q["alternatives"]
    })

def handle_answer(params):
    global scores, players_answers, current_question_idx
    name = params.get('name', [''])[0]
    answer = params.get('answer', [''])[0]
    if not name:
        return json.dumps({"error": "Nome obrigatório"})
    if name not in scores:
        scores[name] = 0
    if name in players_answers:
        return json.dumps({"error": "Já respondeu esta pergunta"})
    players_answers[name] = answer
    correct = answer == QUESTIONS[current_question_idx]["answer"]
    if correct:
        scores[name] += 1
    return json.dumps({"correct": correct, "score": scores[name]})

def next_question():
    global current_question_idx, players_answers
    current_question_idx = (current_question_idx + 1) % len(QUESTIONS)
    players_answers = {}

def handle_request(request):
    lines = request.split('\r\n')
    method, path, *_ = lines[0].split()
    name = ""
    msg = ""
    now = time.time()
    time_left = QUESTION_TIMEOUT if question_start_time is None else max(0, QUESTION_TIMEOUT - (now - question_start_time))
    show_timeout = False
    waiting = False

    # Adiciona jogador à lista de conectados
    if method == "POST":
        body = lines[-1]
        params = urllib.parse.parse_qs(body)
        name = params.get('name', [''])[0]
        answer = params.get('answer', [''])[0]
        if name:
            connected_players.add(name)
            if quiz_started:
                if name not in scores:
                    scores[name] = 0
                # Só registra resposta se ainda não respondeu nesta rodada e entrou antes da rodada
                if name not in players_answers and (question_start_time is not None and (now - question_start_time) < QUESTION_TIMEOUT):
                    players_answers[name] = answer
                    if answer.lower() == current_question["answer"].lower():
                        scores[name] += 1
                        msg = "Resposta correta!"
                    else:
                        msg = "Resposta incorreta!"
                elif name in players_answers:
                    msg = "Você já respondeu esta pergunta! Aguarde a próxima."
                else:
                    msg = "Você entrou após o início da rodada. Aguarde a próxima pergunta."

    # Se não atingiu número mínimo de jogadores, mostra sala de espera
    if not quiz_started or len(connected_players) < MIN_PLAYERS:
        waiting = True
        if len(connected_players) >= MIN_PLAYERS and not quiz_started:
            # Inicia quiz
            quiz_started = True
            scores = {name: 0 for name in connected_players}
            current_question = random.choice(QUESTIONS)
            question_start_time = time.time()
            players_answers = {}
        html = build_html(name, current_question if current_question else "", scores, msg, time_left, show_timeout, waiting)
        resp = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(html.encode())}\r\n\r\n{html}"
        return resp.encode()

    # Verifica se todos responderam ou tempo acabou
    if time_left == 0 or (scores and len(players_answers) >= len(scores)):
        show_timeout = time_left == 0
        # Avança para próxima pergunta
        current_question = random.choice(QUESTIONS)
        question_start_time = time.time()
        players_answers = {}
        msg = "Nova pergunta!"
        time_left = QUESTION_TIMEOUT

    html = build_html(name, current_question["question"], scores, msg, time_left, show_timeout, waiting)
    resp = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(html.encode())}\r\n\r\n{html}"
    return resp.encode()
    # API REST
    if path.startswith('/api/question'):
        resp = get_question_json()
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(resp.encode())}\r\n\r\n{resp}".encode()
    if path.startswith('/api/answer'):
        body = lines[-1]
        params = urllib.parse.parse_qs(body)
        resp = handle_answer(params)
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(resp.encode())}\r\n\r\n{resp}".encode()
    if path.startswith('/api/next'):
        next_question()
        resp = get_question_json()
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(resp.encode())}\r\n\r\n{resp}".encode()
    # Página HTML padrão
    html = "<html><body><h1>Quiz TCP API</h1><p>Use o frontend React para jogar.</p></body></html>"
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(html.encode())}\r\n\r\n{html}".encode()


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 8080))
    s.listen(5)
    print("Quiz TCP API rodando na porta 8080")
    try:
        while True:
            conn, addr = s.accept()
            data = conn.recv(4096).decode(errors='ignore')
            if not data:
                conn.close()
                continue
            resp = handle_request(data)
            conn.sendall(resp)
            conn.close()
    except KeyboardInterrupt:
        print("Servidor encerrado pelo usuário.")
    s.close()

if __name__ == "__main__":
    main()

