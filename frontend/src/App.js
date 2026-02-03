import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import EnginesPage from "./pages/EnginesPage";
import MoneyPipelinePage from "./pages/MoneyPipelinePage";
import PipelineComposerPage from "./pages/PipelineComposerPage";
import ExecutionHistoryPage from "./pages/ExecutionHistoryPage";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/engines" element={<EnginesPage />} />
          <Route path="/money-pipeline" element={<MoneyPipelinePage />} />
          <Route path="/pipeline-composer" element={<PipelineComposerPage />} />
          <Route path="/history" element={<ExecutionHistoryPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
