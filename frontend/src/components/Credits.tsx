type CreditsProps = {
  onBack: () => void;
};

export default function Credits({ onBack }: CreditsProps) {
  return (
    <div className="center-wrapper dark-bg">
      <div className="dark-box">
        <h2>Créditos</h2>
        <p>Desenvolvido por:</p>
        <ul className="no-bullets">
          <li>Bruno César</li>
          <li>Daniel Guilherme</li>
          <li>Marcus Vinicius</li>
          <li>Paulo Carvalho</li>
        </ul>
        <p style={{ marginTop: "20px" }}>Professor: Edison</p>
        <button className="back-btn" onClick={onBack}>
          Voltar ao menu
        </button>
      </div>
    </div>
  );
}
