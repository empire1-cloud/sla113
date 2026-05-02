import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const AVAILABLE_ENGINES = [
  { id: "strategy_engine", name: "Strategy Engine", icon: "🎯", desc: "Generate high-level strategies" },
  { id: "plan_builder_engine", name: "Plan Builder", icon: "📋", desc: "Convert goals to execution plans" },
  { id: "analysis_engine", name: "Analysis Engine", icon: "🔍", desc: "Deep SWOT analysis" },
  { id: "opportunity_mapper_engine", name: "Opportunity Mapper", icon: "💡", desc: "Identify opportunities" },
  { id: "evaluator_engine", name: "Evaluator Engine", icon: "⚖️", desc: "Score and evaluate" },
  { id: "pricing_engine", name: "Pricing Engine", icon: "💰", desc: "Generate pricing structures" },
  { id: "blueprint_engine", name: "Blueprint Engine", icon: "🏗️", desc: "System architecture" },
  { id: "persona_engine", name: "Persona Engine", icon: "👤", desc: "User personas" },
  { id: "anime_character_engine", name: "Anime Character", icon: "🎨", desc: "Create anime characters" },
  { id: "anime_lore_engine", name: "Anime Lore", icon: "📚", desc: "World-building" },
  { id: "anime_story_engine", name: "Anime Story", icon: "📖", desc: "Story arcs" },
  { id: "art_direction_engine", name: "Art Direction", icon: "🖼️", desc: "Visual direction" },
  { id: "money_pipeline_engine", name: "Money Pipeline", icon: "💵", desc: "Full monetization" }
];

const PRESET_PIPELINES = {
  "business_plan": {
    name: "Full Business Plan",
    description: "Strategy → Analysis → Opportunities → Plan → Pricing",
    steps: [
      { engine: "strategy_engine", input_key: "goal", output_key: "strategy" },
      { engine: "analysis_engine", input_key: "strategy.summary", output_key: "analysis" },
      { engine: "opportunity_mapper_engine", input_key: "analysis", output_key: "opportunities" },
      { engine: "plan_builder_engine", input_key: "strategy", output_key: "plan" },
      { engine: "pricing_engine", input_key: "strategy.summary", output_key: "pricing" }
    ]
  },
  "startup_validation": {
    name: "Startup Validation",
    description: "Analysis → Persona → Opportunities → Evaluation",
    steps: [
      { engine: "analysis_engine", input_key: "business_idea", output_key: "market_analysis" },
      { engine: "persona_engine", input_key: "target_customer", output_key: "icp" },
      { engine: "opportunity_mapper_engine", input_key: "market", output_key: "opportunities" },
      { engine: "evaluator_engine", input_key: "business_idea", output_key: "viability" }
    ]
  },
  "idea_to_money": {
    name: "Idea to Money",
    description: "Money Pipeline → Persona → Blueprint → Evaluation",
    steps: [
      { engine: "money_pipeline_engine", input_key: "idea", output_key: "pipeline" },
      { engine: "persona_engine", input_key: "pipeline.market_analysis", output_key: "personas" },
      { engine: "blueprint_engine", input_key: "pipeline.product_blueprint", output_key: "architecture" },
      { engine: "evaluator_engine", input_key: "pipeline", output_key: "assessment" }
    ]
  },
  "anime_concept": {
    name: "Anime Full Concept",
    description: "Lore → Story → Character → Art Direction",
    steps: [
      { engine: "anime_lore_engine", input_key: "world_concept", output_key: "lore" },
      { engine: "anime_story_engine", input_key: "lore", output_key: "story" },
      { engine: "anime_character_engine", input_key: "story.premise", output_key: "protagonist" },
      { engine: "art_direction_engine", input_key: "story,lore", output_key: "art_direction" }
    ]
  },
  "product_launch": {
    name: "Product Launch",
    description: "Persona → Strategy → Pricing → Plan",
    steps: [
      { engine: "persona_engine", input_key: "audience", output_key: "personas" },
      { engine: "strategy_engine", input_key: "product_goal", output_key: "strategy" },
      { engine: "pricing_engine", input_key: "product", output_key: "pricing" },
      { engine: "plan_builder_engine", input_key: "strategy", output_key: "launch_plan" }
    ]
  }
};

const PipelineComposerPage = () => {
  const [steps, setSteps] = useState([]);
  const [initialInput, setInitialInput] = useState("");
  const [executing, setExecuting] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [results, setResults] = useState([]);
  const [savedPipelines, setSavedPipelines] = useState({});
  const [pipelineName, setPipelineName] = useState("");
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showLoadModal, setShowLoadModal] = useState(false);

  // Load saved pipelines from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("savedPipelines");
    if (saved) {
      setSavedPipelines(JSON.parse(saved));
    }
  }, []);

  const addStep = (engine) => {
    const engineInfo = AVAILABLE_ENGINES.find(e => e.id === engine);
    setSteps([...steps, {
      id: Date.now(),
      engine,
      name: engineInfo?.name || engine,
      icon: engineInfo?.icon || "⚙️",
      input_key: steps.length === 0 ? "input" : `step_${steps.length}`,
      output_key: `step_${steps.length + 1}`
    }]);
  };

  const removeStep = (index) => {
    setSteps(steps.filter((_, i) => i !== index));
  };

  const moveStep = (index, direction) => {
    const newSteps = [...steps];
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= steps.length) return;
    [newSteps[index], newSteps[newIndex]] = [newSteps[newIndex], newSteps[index]];
    setSteps(newSteps);
  };

  const loadPreset = (presetKey) => {
    const preset = PRESET_PIPELINES[presetKey];
    if (!preset) return;
    
    const loadedSteps = preset.steps.map((step, i) => {
      const engineInfo = AVAILABLE_ENGINES.find(e => e.id === step.engine);
      return {
        id: Date.now() + i,
        engine: step.engine,
        name: engineInfo?.name || step.engine,
        icon: engineInfo?.icon || "⚙️",
        input_key: step.input_key,
        output_key: step.output_key
      };
    });
    setSteps(loadedSteps);
    setShowLoadModal(false);
  };

  const loadSavedPipeline = (key) => {
    const pipeline = savedPipelines[key];
    if (!pipeline) return;
    setSteps(pipeline.steps);
    setShowLoadModal(false);
  };

  const savePipeline = () => {
    if (!pipelineName.trim() || steps.length === 0) return;
    
    const newSaved = {
      ...savedPipelines,
      [pipelineName]: {
        name: pipelineName,
        steps: steps,
        createdAt: new Date().toISOString()
      }
    };
    setSavedPipelines(newSaved);
    localStorage.setItem("savedPipelines", JSON.stringify(newSaved));
    setPipelineName("");
    setShowSaveModal(false);
  };

  const deleteSavedPipeline = (key) => {
    const newSaved = { ...savedPipelines };
    delete newSaved[key];
    setSavedPipelines(newSaved);
    localStorage.setItem("savedPipelines", JSON.stringify(newSaved));
  };

  const getEnginePayload = (engine, input, previousResults) => {
    // Build payload based on engine type and available context
    const basePayload = { model: "gemini-3-flash" };
    
    switch (engine) {
      case "strategy_engine":
        return { ...basePayload, goal: input, context: JSON.stringify(previousResults).slice(0, 500) };
      case "plan_builder_engine":
        return { ...basePayload, goal: input, strategy: previousResults[previousResults.length - 1]?.output };
      case "analysis_engine":
        return { ...basePayload, subject: input, context: JSON.stringify(previousResults).slice(0, 500) };
      case "opportunity_mapper_engine":
        return { ...basePayload, situation: input, context: JSON.stringify(previousResults).slice(0, 500) };
      case "evaluator_engine":
        return { ...basePayload, subject: "Pipeline Output", content: input, criteria_preset: "idea" };
      case "pricing_engine":
        return { ...basePayload, product: input, target_market: "General market" };
      case "blueprint_engine":
        return { ...basePayload, system_description: input };
      case "persona_engine":
        return { ...basePayload, audience: input, context: JSON.stringify(previousResults).slice(0, 500) };
      case "anime_character_engine":
        return { ...basePayload, concept: input, genre: "fantasy" };
      case "anime_lore_engine":
        return { ...basePayload, world_concept: input };
      case "anime_story_engine":
        return { ...basePayload, concept: input, episode_count: 12 };
      case "art_direction_engine":
        return { ...basePayload, project: input, genre: "anime" };
      case "money_pipeline_engine":
        return { ...basePayload, idea: input };
      default:
        return { ...basePayload, input };
    }
  };

  const getEngineEndpoint = (engine) => {
    const endpoints = {
      strategy_engine: "/strategy",
      plan_builder_engine: "/plan",
      analysis_engine: "/analyze",
      opportunity_mapper_engine: "/opportunities",
      evaluator_engine: "/evaluate",
      pricing_engine: "/pricing",
      blueprint_engine: "/blueprint",
      persona_engine: "/persona",
      anime_character_engine: "/anime/character",
      anime_lore_engine: "/anime/lore",
      anime_story_engine: "/anime/story",
      art_direction_engine: "/art-direction",
      money_pipeline_engine: "/money-pipeline"
    };
    return endpoints[engine] || `/${engine}`;
  };

  const executePipeline = async () => {
    if (steps.length === 0 || !initialInput.trim()) return;
    
    setExecuting(true);
    setResults([]);
    setCurrentStep(0);
    
    const pipelineResults = [];
    let currentInput = initialInput;
    
    for (let i = 0; i < steps.length; i++) {
      setCurrentStep(i);
      const step = steps[i];
      
      const stepResult = {
        step: i + 1,
        engine: step.engine,
        name: step.name,
        icon: step.icon,
        input: currentInput,
        output: null,
        error: null,
        duration: 0,
        status: "running"
      };
      
      setResults([...pipelineResults, stepResult]);
      
      const startTime = Date.now();
      
      try {
        const endpoint = getEngineEndpoint(step.engine);
        const payload = getEnginePayload(step.engine, currentInput, pipelineResults);
        
        const response = await axios.post(`${API}${endpoint}`, payload, { timeout: 120000 });
        
        stepResult.output = response.data;
        stepResult.status = "success";
        stepResult.duration = Date.now() - startTime;
        
        // Use summary or first meaningful field as input for next step
        currentInput = response.data.summary || 
                      response.data.objective ||
                      response.data.core_offer ||
                      response.data.name ||
                      JSON.stringify(response.data).slice(0, 500);
        
      } catch (e) {
        stepResult.error = e.response?.data?.detail || e.message;
        stepResult.status = "error";
        stepResult.duration = Date.now() - startTime;
      }
      
      pipelineResults.push(stepResult);
      setResults([...pipelineResults]);
      
      // Stop on error
      if (stepResult.status === "error") {
        break;
      }
    }
    
    setCurrentStep(-1);
    setExecuting(false);
  };

  const clearPipeline = () => {
    setSteps([]);
    setResults([]);
    setInitialInput("");
  };

  return (
    <div className="page-container" data-testid="pipeline-composer-page">
      <header className="page-header">
        <Link to="/" className="back-link">← Home</Link>
        <h1>🔗 Pipeline Composer</h1>
        <p className="subtitle">Chain multiple engines together for complex workflows</p>
      </header>

      <div className="composer-layout">
        {/* Left Panel - Engine Selector */}
        <aside className="composer-sidebar">
          <div className="sidebar-section">
            <h3>Available Engines</h3>
            <p className="sidebar-hint">Click to add to pipeline</p>
            <div className="engine-selector" data-testid="engine-selector">
              {AVAILABLE_ENGINES.map(engine => (
                <button
                  key={engine.id}
                  className="engine-select-btn"
                  onClick={() => addStep(engine.id)}
                  disabled={executing}
                  data-testid={`add-engine-${engine.id}`}
                >
                  <span className="engine-select-icon">{engine.icon}</span>
                  <span className="engine-select-name">{engine.name}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="sidebar-section">
            <h3>Presets & Saved</h3>
            <div className="preset-buttons">
              <button className="preset-btn" onClick={() => setShowLoadModal(true)} data-testid="load-btn">
                📂 Load Pipeline
              </button>
              <button 
                className="preset-btn" 
                onClick={() => setShowSaveModal(true)} 
                disabled={steps.length === 0}
                data-testid="save-btn"
              >
                💾 Save Pipeline
              </button>
            </div>
          </div>
        </aside>

        {/* Main Panel */}
        <main className="composer-main">
          {/* Pipeline Builder */}
          <section className="pipeline-builder" data-testid="pipeline-builder">
            <div className="builder-header">
              <h3>Pipeline Steps ({steps.length})</h3>
              <button 
                className="clear-btn" 
                onClick={clearPipeline}
                disabled={executing || steps.length === 0}
              >
                Clear All
              </button>
            </div>

            {steps.length === 0 ? (
              <div className="empty-pipeline">
                <span>🔗</span>
                <p>Add engines from the left panel to build your pipeline</p>
              </div>
            ) : (
              <div className="pipeline-steps" data-testid="pipeline-steps">
                {steps.map((step, index) => (
                  <div key={step.id} className={`pipeline-step ${currentStep === index ? 'running' : ''}`}>
                    <div className="step-number">{index + 1}</div>
                    <div className="step-content">
                      <span className="step-icon">{step.icon}</span>
                      <span className="step-name">{step.name}</span>
                    </div>
                    <div className="step-actions">
                      <button 
                        onClick={() => moveStep(index, -1)} 
                        disabled={index === 0 || executing}
                        title="Move up"
                      >↑</button>
                      <button 
                        onClick={() => moveStep(index, 1)} 
                        disabled={index === steps.length - 1 || executing}
                        title="Move down"
                      >↓</button>
                      <button 
                        onClick={() => removeStep(index)} 
                        disabled={executing}
                        className="remove-btn"
                        title="Remove"
                      >×</button>
                    </div>
                    {index < steps.length - 1 && <div className="step-connector">→</div>}
                  </div>
                ))}
              </div>
            )}

            {/* Input & Execute */}
            <div className="pipeline-input-section">
              <label>Initial Input</label>
              <textarea
                value={initialInput}
                onChange={(e) => setInitialInput(e.target.value)}
                placeholder="Enter the starting input for your pipeline (e.g., 'Build an AI-powered fitness app')"
                rows={3}
                disabled={executing}
                data-testid="initial-input"
              />
              <button
                className="execute-btn"
                onClick={executePipeline}
                disabled={executing || steps.length === 0 || !initialInput.trim()}
                data-testid="execute-btn"
              >
                {executing ? (
                  <><span className="btn-spinner"></span> Executing Step {currentStep + 1}/{steps.length}...</>
                ) : (
                  <>▶ Execute Pipeline</>
                )}
              </button>
            </div>
          </section>

          {/* Results Timeline */}
          {results.length > 0 && (
            <section className="results-timeline" data-testid="results-timeline">
              <h3>Execution Timeline</h3>
              <div className="timeline">
                {results.map((result, index) => (
                  <div 
                    key={index} 
                    className={`timeline-item ${result.status}`}
                    data-testid={`timeline-item-${index}`}
                  >
                    <div className="timeline-marker">
                      {result.status === "running" ? (
                        <span className="marker-spinner"></span>
                      ) : result.status === "success" ? (
                        <span className="marker-success">✓</span>
                      ) : (
                        <span className="marker-error">✗</span>
                      )}
                    </div>
                    <div className="timeline-content">
                      <div className="timeline-header">
                        <span className="timeline-step">Step {result.step}</span>
                        <span className="timeline-engine">{result.icon} {result.name}</span>
                        {result.duration > 0 && (
                          <span className="timeline-duration">{(result.duration / 1000).toFixed(1)}s</span>
                        )}
                      </div>
                      
                      <div className="timeline-io">
                        <details className="io-section">
                          <summary>📥 Input</summary>
                          <pre>{typeof result.input === 'string' ? result.input : JSON.stringify(result.input, null, 2)}</pre>
                        </details>
                        
                        {result.output && (
                          <details className="io-section" open={index === results.length - 1}>
                            <summary>📤 Output</summary>
                            <pre>{JSON.stringify(result.output, null, 2)}</pre>
                          </details>
                        )}
                        
                        {result.error && (
                          <div className="io-error">
                            <strong>Error:</strong> {result.error}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </main>
      </div>

      {/* Save Modal */}
      {showSaveModal && (
        <div className="modal-overlay" onClick={() => setShowSaveModal(false)}>
          <div className="modal-content modal-small" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>💾 Save Pipeline</h2>
              <button className="modal-close" onClick={() => setShowSaveModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Pipeline Name</label>
                <input
                  type="text"
                  value={pipelineName}
                  onChange={(e) => setPipelineName(e.target.value)}
                  placeholder="My Custom Pipeline"
                  data-testid="pipeline-name-input"
                />
              </div>
              <div className="save-preview">
                <p><strong>Steps:</strong> {steps.map(s => s.name).join(" → ")}</p>
              </div>
              <button 
                className="btn-submit" 
                onClick={savePipeline}
                disabled={!pipelineName.trim()}
                data-testid="confirm-save-btn"
              >
                Save Pipeline
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Load Modal */}
      {showLoadModal && (
        <div className="modal-overlay" onClick={() => setShowLoadModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📂 Load Pipeline</h2>
              <button className="modal-close" onClick={() => setShowLoadModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <h4>Preset Pipelines</h4>
              <div className="preset-list">
                {Object.entries(PRESET_PIPELINES).map(([key, preset]) => (
                  <div key={key} className="preset-item" onClick={() => loadPreset(key)} data-testid={`preset-${key}`}>
                    <div className="preset-info">
                      <strong>{preset.name}</strong>
                      <p>{preset.description}</p>
                    </div>
                    <button className="btn-small btn-primary">Load</button>
                  </div>
                ))}
              </div>
              
              {Object.keys(savedPipelines).length > 0 && (
                <>
                  <h4>Saved Pipelines</h4>
                  <div className="preset-list">
                    {Object.entries(savedPipelines).map(([key, pipeline]) => (
                      <div key={key} className="preset-item">
                        <div className="preset-info">
                          <strong>{pipeline.name}</strong>
                          <p>{pipeline.steps.map(s => s.name).join(" → ")}</p>
                        </div>
                        <div className="preset-actions">
                          <button 
                            className="btn-small btn-primary" 
                            onClick={() => loadSavedPipeline(key)}
                          >
                            Load
                          </button>
                          <button 
                            className="btn-small btn-danger" 
                            onClick={() => deleteSavedPipeline(key)}
                          >
                            🗑
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PipelineComposerPage;
