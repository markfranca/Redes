import { useState } from "react";
import Menu from "./components/Menu";
import Game from "./components/Game";
import Instructions from "./components/Instructions";
import Credits from "./components/Credits";
import "./App.css";

type Screen = "menu" | "game" | "instructions" | "credits";

function App() {
  const [screen, setScreen] = useState<Screen>("menu");

  switch (screen) {
    case "menu":
      return <Menu onNavigate={setScreen} />;
    case "game":
      return <Game onExit={() => setScreen("menu")} />;
    case "instructions":
      return <Instructions onBack={() => setScreen("menu")} />;
    case "credits":
      return <Credits onBack={() => setScreen("menu")} />;
    default:
      return null;
  }
}

export default App;
