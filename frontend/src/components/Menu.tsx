type MenuProps = {
  onNavigate: (screen: "menu" | "game" | "instructions" | "credits") => void;
};

export default function Menu({ onNavigate }: MenuProps) {
  return (
    <div className="center-wrapper dark-bg">
      <div className="menu-box">
        <h1 className="title">🎮 Quiz Multiplayer</h1>
        <button className="menu-btn" onClick={() => onNavigate("game")}>
          Jogar
        </button>
        <button className="menu-btn" onClick={() => onNavigate("instructions")}>
          Instruções
        </button>
        <button className="menu-btn" onClick={() => onNavigate("credits")}>
          Créditos
        </button>
        <button className="back-btn" onClick={() => window.close()}>
          Sair
        </button>
      </div>
    </div>
  );
}
