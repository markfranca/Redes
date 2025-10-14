import { useEffect, useState } from "react";

type Player = {
  name: string;
  score: number;
};

type Question = {
  text: string;
  options: string[];
};

type GameStatus = {
  quiz_started: boolean;
  players: Player[];
  current_question?: Question;
  time_left?: number;
  quiz_finished?: boolean;
};

const API_BASE = "http://localhost:8080/api";

type GameProps = {
  onExit: () => void;
};

export default function Game({ onExit }: GameProps) {
  const [name, setName] = useState("");
  const [joined, setJoined] = useState(false);
  const [status, setStatus] = useState<GameStatus>({
    quiz_started: false,
    players: [],
  });
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string>("");

  useEffect(() => {
    let lastQuestionText = "";

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/status`);
        if (res.ok) {
          const data = await res.json();

          const newQuestionText = data.current_question?.text ?? "";
          if (newQuestionText !== lastQuestionText) {
            setSelectedAnswer(null);
            setFeedback("");
            lastQuestionText = newQuestionText;
          }

          setStatus(data);

          if (data.quiz_finished) {
            setFeedback("🏆 Quiz finalizado!");
          }
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const joinGame = async () => {
    if (!name.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/join`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      if (res.ok) {
        setJoined(true);
      }
    } catch (err) {
      console.error("Join error:", err);
    }
  };

  const sendAnswer = async (answer: string) => {
    setSelectedAnswer(answer);
    try {
      const res = await fetch(`${API_BASE}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, answer }),
      });
      if (res.ok) {
        const data = await res.json();
        setFeedback(data.correct ? "✅ Resposta certa!" : "❌ Resposta errada");
      }
    } catch (err) {
      console.error("Answer error:", err);
    }
  };

  if (!joined) {
    return (
      <div className="center-wrapper dark-bg">
        <div className="login-container">
          <h2>Entrar no Quiz</h2>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Seu nome"
          />
          <button className="menu-btn" onClick={joinGame}>
            Entrar
          </button>
          <button className="back-btn" onClick={onExit}>
            Voltar ao menu
          </button>
        </div>
      </div>
    );
  }

  if (!status.quiz_started) {
    return (
      <div className="center-wrapper dark-bg">
        <div className="dark-box">
          <h2>Sala de espera ({status.players.length}/2)</h2>
          <div className="players-list">
            <h3>Jogadores</h3>
            <ul className="no-bullets">
              {status.players.map((p) => (
                <li key={p.name}>{p.name}</li>
              ))}
            </ul>
          </div>
          <button className="back-btn" onClick={onExit}>
            Sair
          </button>
        </div>
      </div>
    );
  }

  if (status.quiz_finished) {
    return (
      <div className="center-wrapper dark-bg">
        <div className="dark-box">
          <h2>🏁 Fim do Quiz</h2>
          <div className="scoreboard">
            <h3>Placar final</h3>
            <ul>
              {status.players.map((p) => (
                <li key={p.name}>
                  {p.name}: {p.score} ponto(s)
                </li>
              ))}
            </ul>
          </div>
          <button className="back-btn" onClick={onExit}>
            Voltar ao menu
          </button>
        </div>
      </div>
    );
  }

  const q = status.current_question;

  return (
    <div className="center-wrapper dark-bg">
      <div className="quiz-box">
        <div className="timer-section">
          <h3>⏱ Tempo restante: {status.time_left}s</h3>
        </div>

        {q ? (
          <>
            <h2 className="question-title">{q.text}</h2>
            <div className="alternatives-row">
              {q.options.map((opt) => (
                <button
                  key={opt}
                  className={`alt-btn ${
                    selectedAnswer === opt ? "selected" : ""
                  }`}
                  onClick={() => sendAnswer(opt)}
                  disabled={!!selectedAnswer}
                >
                  {opt}
                </button>
              ))}
            </div>
            {feedback && <p className="feedback">{feedback}</p>}
          </>
        ) : (
          <p className="feedback">Aguardando próxima pergunta...</p>
        )}

        <div className="scoreboard">
          <h3>Placar</h3>
          <ul>
            {status.players.map((p) => (
              <li key={p.name}>
                {p.name}: {p.score}
              </li>
            ))}
          </ul>
        </div>

        <button className="back-btn" onClick={onExit}>
          Sair
        </button>
      </div>
    </div>
  );
}
