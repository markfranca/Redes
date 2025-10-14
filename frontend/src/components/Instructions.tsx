type InstructionsProps = {
  onBack: () => void;
};

export default function Instructions({ onBack }: InstructionsProps) {
  return (
    <div className="center-wrapper dark-bg">
      <div className="dark-box">
        <h2>🧠 Instruções do Jogo</h2>
        <ul>
          <li>Digite seu nome e entre no jogo.</li>
          <li>Espere os outros jogadores entrarem.</li>
          <li>3Quando o quiz começar, escolha a alternativa correta.</li>
          <li>4Cada acerto vale pontos!</li>
          <li>5Vença quem fizer mais pontos ao final 🎯</li>
        </ul>
        <button className="back-btn" onClick={onBack}>
          Voltar ao menu
        </button>
      </div>
    </div>
  );
}
