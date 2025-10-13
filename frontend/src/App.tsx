import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [screen, setScreen] = useState<'menu' | 'play' | 'credits' | 'howto'>('menu');
  const [playerName, setPlayerName] = useState('');
  const [pergunta, setPergunta] = useState('');
  const [alternativas, setAlternativas] = useState<string[]>([]);
  const [respostaSelecionada, setRespostaSelecionada] = useState<string | null>(null);
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);

  // Busca pergunta e alternativas ao entrar na tela de jogo
  useEffect(() => {
    if (screen === 'play') {
      setLoading(true);
      fetch('http://localhost:8080/api/question')
        .then(res => res.json())
        .then(data => {
          setPergunta(data.question);
          setAlternativas(data.alternatives);
          setRespostaSelecionada(null);
          setFeedback('');
        })
        .catch(err => console.error('Erro ao buscar pergunta:', err))
        .finally(() => setLoading(false));
    }
  }, [screen]);

  // Handlers de navegação
  const handlePlay = () => setScreen('play');
  const handleCredits = () => setScreen('credits');
  const handleHowTo = () => setScreen('howto');
  const handleBack = () => setScreen('menu');
  const handleExit = () => window.close();

  const handleEnter = () => {
    if (playerName.trim()) {
      window.location.href = `http://localhost:8080?name=${encodeURIComponent(playerName)}`;
    } else {
      alert('Por favor, insira um nome.');
    }
  };

  // Envia resposta ao backend
  const handleResposta = (alt: string) => {
    setRespostaSelecionada(alt);
    setLoading(true);
    fetch('http://localhost:8080/api/answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answer: alt }),
    })
      .then(res => res.json())
      .then(data => {
        setFeedback(data.correct ? '✅ Correto!' : '❌ Errado!');
      })
      .catch(err => console.error('Erro ao enviar resposta:', err))
      .finally(() => setLoading(false));
  };

  // ======= TELAS =======

  if (screen === 'menu') {
    return (
      <div className="dark-bg center-wrapper">
        <div className="menu-box">
          <h1 className="title">Quiz TCP</h1>
          <button className="menu-btn" onClick={handlePlay}>Jogar</button>
          <button className="menu-btn" onClick={handleHowTo}>Como Jogar</button>
          <button className="menu-btn" onClick={handleCredits}>Créditos</button>
          <button className="menu-btn" onClick={handleExit}>Sair</button>
        </div>
      </div>
    );
  }

  if (screen === 'play') {
    return (
      <div className="dark-bg center-wrapper">
        <div className="quiz-box">
          <h2 className="question-title">{loading ? 'Carregando...' : pergunta}</h2>
          <div className="alternatives-row">
            {alternativas.map((alt, idx) => (
              <button
                key={idx}
                className={`alt-btn${respostaSelecionada === alt ? ' selected' : ''}`}
                onClick={() => handleResposta(alt)}
                disabled={!!respostaSelecionada || loading}
              >
                {alt}
              </button>
            ))}
          </div>
          {feedback && <div className="feedback">{feedback}</div>}
          <button className="menu-btn" onClick={handleBack} style={{ marginTop: 24 }}>Voltar ao menu</button>
        </div>
      </div>
    );
  }

  if (screen === 'credits') {
    return (
      <div className="dark-bg center-wrapper">
        <div className="dark-box">
          <h2>Créditos</h2>
          <ul className="no-bullets">
            <li>Bruno Safado</li>
            <li>Daniel Guilherme</li>
            <li>Marcus Vinicius</li>
            <li>Paulo Carvalho</li>
          </ul>
          <button className="back-btn" onClick={handleBack}>Voltar</button>
        </div>
      </div>
    );
  }

  if (screen === 'howto') {
    return (
      <div className="dark-bg center-wrapper">
        <div className="dark-box">
          <h2>Como Jogar</h2>
          <ul className="no-bullets">
            <li>Digite seu nome e clique em Entrar.</li>
            <li>Responda às perguntas antes do tempo acabar.</li>
            <li>O placar é atualizado automaticamente.</li>
            <li>Se entrar após o início da rodada, aguarde a próxima pergunta.</li>
          </ul>
          <button className="back-btn" onClick={handleBack}>Voltar</button>
        </div>
      </div>
    );
  }

  return null;
}

export default App;
