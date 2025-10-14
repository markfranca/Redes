import socket
import threading
import json
import time

# ============================================================
# CONFIGURAÇÕES GERAIS DO SERVIDOR
# ============================================================

HOST = '0.0.0.0'  # O servidor escuta em todas as interfaces (localhost + LAN)
PORT = 8080       # Porta onde o servidor HTTP será executado

# ============================================================
# CONFIGURAÇÕES DO QUIZ
# ============================================================

MIN_PLAYERS = 2        # Quantidade mínima de jogadores para iniciar o quiz
QUESTION_TIMEOUT = 15  # Tempo máximo (em segundos) para responder cada pergunta

# ============================================================
# VARIÁVEIS GLOBAIS DE ESTADO DO JOGO
# ============================================================

connected_players = []   # Lista com os nomes dos jogadores conectados
scores = {}              # Armazena a pontuação de cada jogador
quiz_started = False     # Indica se o quiz já começou
quiz_finished = False    # Indica se o quiz terminou
current_question_index = 0  # Índice da pergunta atual
question_start_time = None   # Hora em que a pergunta atual começou
player_answers = {}          # Respostas já enviadas pelos jogadores

# ============================================================
# BASE DE PERGUNTAS DO QUIZ
# ============================================================

questions = [
    {"text": "Qual a capital do Brasil?", "options": ["Rio", "Brasília", "SP"], "correct": "Brasília"},
    {"text": "2 + 2 = ?", "options": ["3", "4", "5"], "correct": "4"},
    {"text": "Cor do céu?", "options": ["Azul", "Verde", "Amarelo"], "correct": "Azul"},
]


# ============================================================
# FUNÇÕES DE CONTROLE DO JOGO
# ============================================================

def start_quiz():
    """
    Inicia o quiz:
    - Define que o jogo começou
    - Reinicia o índice da pergunta e as respostas
    - Marca o momento de início da primeira pergunta
    """
    global quiz_started, quiz_finished, question_start_time, current_question_index, player_answers
    quiz_started = True
    quiz_finished = False
    current_question_index = 0
    question_start_time = time.time()
    player_answers = {}
    print("[QUIZ] Iniciado")


def next_question():
    """
    Avança para a próxima pergunta ou finaliza o quiz caso acabe.
    """
    global current_question_index, question_start_time, player_answers, quiz_finished
    current_question_index += 1
    if current_question_index < len(questions):
        question_start_time = time.time()
        player_answers = {}
        print(f"[QUIZ] Indo para pergunta {current_question_index+1}")
    else:
        quiz_finished = True
        print("[QUIZ] Finalizado")


def check_timeout():
    """
    Thread paralela que verifica continuamente:
    - Se o tempo limite da pergunta acabou, ou
    - Se todos os jogadores já responderam.
    Quando qualquer uma das condições é atendida, a próxima pergunta é exibida.
    """
    global question_start_time
    while True:
        time.sleep(1)
        if quiz_started and not quiz_finished and question_start_time:
            elapsed = time.time() - question_start_time
            # Se o tempo expirou ou todos responderam
            if elapsed >= QUESTION_TIMEOUT or len(player_answers) == len(connected_players):
                next_question()


# ============================================================
# FUNÇÃO DE CONSTRUÇÃO DE RESPOSTA HTTP
# ============================================================

def build_response(status_code, body):
    """
    Monta uma resposta HTTP completa.
    Este servidor NÃO usa frameworks (como Flask), então criamos as respostas
    manualmente — isso demonstra o funcionamento real do protocolo HTTP.

    Uma resposta HTTP tem o seguinte formato:

        HTTP/1.1 200 OK
        Content-Type: application/json
        Content-Length: <tamanho>
        (outras headers)
        
        <corpo em JSON>

    Cada parte é separada por \r\n (caractere de quebra de linha no protocolo HTTP)
    """
    body_bytes = body.encode()

    headers = [
        f"HTTP/1.1 {status_code}",               # Linha de status: versão + código + mensagem
        "Content-Type: application/json",        # Tipo do conteúdo
        "Access-Control-Allow-Origin: *",        # Permite acesso CORS de qualquer origem (para o frontend)
        "Access-Control-Allow-Methods: GET, POST, OPTIONS",
        "Access-Control-Allow-Headers: Content-Type",
        f"Content-Length: {len(body_bytes)}",    # Tamanho do corpo em bytes
        "Connection: close",                     # Fecha a conexão após a resposta
        "",                                      # Linha em branco obrigatória
        ""
    ]
    # Retorna cabeçalho + corpo codificados em bytes
    return ("\r\n".join(headers)).encode() + body_bytes


# ============================================================
# FUNÇÃO PRINCIPAL DE TRATAMENTO DE REQUISIÇÕES
# ============================================================

def handle_request(conn):
    """
    Trata uma conexão TCP individual.

    Cada conexão representa uma requisição HTTP.
    Essa função faz:
      1. Leitura dos dados recebidos do cliente (request)
      2. Interpretação do método (GET, POST, OPTIONS)
      3. Seleção da rota (endpoint)
      4. Montagem e envio da resposta HTTP
    """
    global connected_players, quiz_started

    try:
        # ------------------------------------------------------------
        # Etapa 1: RECEBER A REQUISIÇÃO
        # ------------------------------------------------------------
        data = conn.recv(4096).decode()  # Recebe até 4KB de dados da conexão
        if not data:
            conn.close()
            return

        # A primeira linha do HTTP contém método e caminho:
        # Exemplo: "GET /api/status HTTP/1.1"
        method, path, *_ = data.split(' ', 2)

        # ------------------------------------------------------------
        # Etapa 2: SUPORTE AO CORS (pré-flight OPTIONS)
        # ------------------------------------------------------------
        # Navegadores enviam OPTIONS antes de POST/GET em domínios diferentes.
        if method == "OPTIONS":
            conn.send(build_response("204 No Content", "{}"))
            conn.close()
            return

        # ------------------------------------------------------------
        # Etapa 3: EXTRAÇÃO DO CORPO (body)
        # ------------------------------------------------------------
        body = ""
        if "\r\n\r\n" in data:
            # O corpo começa depois da primeira linha em branco
            body = data.split("\r\n\r\n", 1)[1]

        # ------------------------------------------------------------
        # Etapa 4: ROTAS DA API (Mini Roteador HTTP)
        # ------------------------------------------------------------

        # === /api/join ===
        if path == "/api/join" and method == "POST":
            """
            Adiciona um novo jogador ao jogo.
            Caso o número mínimo de jogadores seja atingido, o quiz começa.
            """
            try:
                payload = json.loads(body)
                name = payload.get("name")
                if name and name not in connected_players:
                    connected_players.append(name)
                    scores[name] = 0
                    print(f"[JOIN] Jogadores conectados: {connected_players}")

                    # Inicia automaticamente se há jogadores suficientes
                    if len(connected_players) >= MIN_PLAYERS and not quiz_started:
                        start_quiz()

                conn.send(build_response("200 OK", json.dumps({"ok": True})))
            except Exception as e:
                print("Erro join:", e)
                conn.send(build_response("400 Bad Request", "{}"))

        # === /api/status ===
        elif path == "/api/status" and method == "GET":
            """
            Retorna o estado atual do jogo.
            Essa rota é chamada pelo frontend a cada segundo (polling),
            simulando uma comunicação "tempo real".
            """
            state = {
                "quiz_started": quiz_started,
                "players": [{"name": p, "score": scores[p]} for p in connected_players],
                "quiz_finished": quiz_finished
            }

            # Se o jogo estiver em andamento, envia também a pergunta e o tempo restante
            if quiz_started and not quiz_finished and current_question_index < len(questions):
                q = questions[current_question_index]
                time_left = max(0, QUESTION_TIMEOUT - int(time.time() - question_start_time))
                state["current_question"] = {"text": q["text"], "options": q["options"]}
                state["time_left"] = time_left

            conn.send(build_response("200 OK", json.dumps(state)))

        # === /api/answer ===
        elif path == "/api/answer" and method == "POST":
            """
            Recebe a resposta de um jogador.
            Atualiza a pontuação se a resposta estiver correta e impede múltiplas respostas.
            """
            try:
                payload = json.loads(body)
                name = payload.get("name")
                answer = payload.get("answer")

                if name in connected_players and name not in player_answers and not quiz_finished:
                    player_answers[name] = answer
                    correct = questions[current_question_index]["correct"]

                    # Se a resposta for correta, incrementa o score
                    if answer == correct:
                        scores[name] += 1

                    conn.send(build_response("200 OK", json.dumps({"correct": answer == correct})))
                else:
                    conn.send(build_response("400 Bad Request", "{}"))
            except Exception as e:
                print("Erro answer:", e)
                conn.send(build_response("400 Bad Request", "{}"))

        # === Qualquer outro endpoint inválido ===
        else:
            conn.send(build_response("404 Not Found", "{}"))

    except Exception as e:
        print("[ERRO]", e)
    finally:
        # Fecha a conexão TCP (cada request abre uma nova)
        conn.close()


# ============================================================
# LOOP PRINCIPAL DO SERVIDOR (BACKBONE DE REDE)
# ============================================================

def server_loop():
    """
    Essa função é o núcleo da aplicação de rede.
    Ela cria um socket TCP e escuta continuamente novas conexões HTTP.
    Cada cliente (ex: navegador) é tratado em uma thread separada.
    """

    # Cria um socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # SO_REUSEADDR permite reiniciar o servidor rapidamente
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Associa o socket ao IP e porta definidos
        s.bind((HOST, PORT))

        # Coloca o socket no modo de escuta (listen backlog padrão)
        s.listen()
        print(f"[SERVIDOR] Rodando em http://{HOST}:{PORT}")

        # Loop infinito que aceita novas conexões
        while True:
            conn, addr = s.accept()  # Aceita uma nova conexão (bloqueante até alguém conectar)
            print(f"[NOVA CONEXÃO] {addr}")

            # Cria uma nova thread para tratar a requisição desse cliente
            threading.Thread(target=handle_request, args=(conn,)).start()


# ============================================================
# PONTO DE ENTRADA DO SERVIDOR
# ============================================================

if __name__ == "__main__":
    # Thread auxiliar que verifica tempo e controla a troca de perguntas
    threading.Thread(target=check_timeout, daemon=True).start()

    # Inicia o loop principal do servidor TCP
    server_loop()
