import React, { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../redux';
import { setAiLogs } from '../../redux/projectSlice';
import { aiApi, extractErrorMessage } from '../../api/api';
import { 
  Sparkles, 
  Play, 
  Terminal, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  Eye,
  ArrowRight,
  Copy,
  Check
} from 'lucide-react';

const ControlCenter: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const dispatch = useAppDispatch();
  
  const { aiLogs } = useAppSelector((state) => state.projects);
  const [generating, setGenerating] = useState(false);
  const [pollingActive, setPollingActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const [viewJsonId, setViewJsonId] = useState<{ id: string; type: 'input' | 'output' } | null>(null);
  const pollIntervalRef = useRef<any>(null);

  const fetchLogs = () => {
    if (!projectId) return;
    aiApi.getLogs(projectId)
      .then((res) => {
        dispatch(setAiLogs(res.data));
        const isRunning = res.data.some((log: any) => log.status === 'Running');
        const isPending = res.data.some((log: any) => log.status === 'Pending');
        
        if (!isRunning && !isPending && res.data.length > 0) {
          setGenerating(false);
          setPollingActive(false);
        }
      })
      .catch((err) => {
        console.error('Failed fetching agent logs', err);
      });
  };

  const startPolling = () => {
    setPollingActive(true);
    fetchLogs();
    pollIntervalRef.current = setInterval(fetchLogs, 2500);
  };

  useEffect(() => {
    if (aiLogs && aiLogs.length > 0) {
      const isRunning = aiLogs.some((l) => l.status === 'Running' || l.status === 'Pending');
      if (isRunning) {
        startPolling();
      }
    } else {
      fetchLogs();
    }

    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, [projectId]);

  useEffect(() => {
    if (!pollingActive && pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }
  }, [pollingActive]);

  const triggerPlanner = async () => {
    if (!projectId) return;
    setGenerating(true);
    setErrorMessage(null);
    try {
      await aiApi.generateSprintPlan(projectId);
      startPolling();
    } catch (err: any) {
      const msg = extractErrorMessage(err, 'Failed to trigger sprint planner. Please ensure requirement documents are uploaded and team members are configured.');
      setErrorMessage(msg);
      setGenerating(false);
    }
  };

  const agentsConfig = [
    {
      name: "Requirement Analysis Agent",
      role: "Senior Business Analyst & Software Architect",
      goal: "Analyze the uploaded SRS text to extract core system modules, functional requirements, and module-level dependencies."
    },
    {
      name: "Task Breakdown Agent",
      role: "Senior Technical Lead",
      goal: "Deconstruct analyzed modules into concrete development tasks, estimating effort in hours and setting difficulty."
    },
    {
      name: "Skill Matching Agent",
      role: "Engineering Resource Manager",
      goal: "Map dev tasks to team members based on role alignment, skill requirements, and workload capacity balancing."
    },
    {
      name: "Sprint Planning Agent",
      role: "Agile Project Scrum Master",
      goal: "Group assigned tasks into structured logical sprints (Sprint 1, Sprint 2, Sprint 3) keeping dependency chains intact."
    },
    {
      name: "Risk Analysis Agent",
      role: "Solutions Risk Auditor",
      goal: "Audit the plan for bottlenecks, overloaded developers, skill gaps, or dependency conflicts, offering mitigations."
    }
  ];

  const getAgentLog = (agentName: string) => {
    return aiLogs.find((l) => l.agent_name === agentName);
  };

  const isPipelineComplete = aiLogs.length >= 5 && aiLogs.every((l) => l.status === 'Completed');

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-10">
      {/* Header Panel */}
      <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/40 p-6 md:p-8 shadow-2xl backdrop-blur-xl transition-all duration-300">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div>
            <h1 className="text-3xl font-black tracking-tight text-white flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600/10 text-indigo-400 ring-1 ring-indigo-500/25 shadow-inner">
                <Sparkles size={22} className="animate-pulse" />
              </span>
              <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                AI Control Center & Telemetry
              </span>
            </h1>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={triggerPlanner}
              disabled={generating || pollingActive}
              className={`relative overflow-hidden rounded-xl px-5 py-3 font-semibold text-sm transition-all duration-350 flex items-center justify-center gap-2 cursor-pointer ${
                generating || pollingActive
                  ? "bg-slate-800 text-slate-500 border border-slate-700/50 cursor-not-allowed"
                  : "bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 hover:from-indigo-600 hover:to-pink-600 text-white shadow-[0_4px_20px_rgba(99,102,241,0.3)] hover:shadow-[0_4px_30px_rgba(99,102,241,0.5)] hover:-translate-y-0.5"
              }`}
            >
              {generating || pollingActive ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-500 border-t-transparent" />
                  <span className="tracking-wide">Pipeline Executing...</span>
                </>
              ) : (
                <>
                  <Play size={16} fill="currentColor" />
                  <span className="tracking-wide">Execute AI Pipeline</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="rounded-xl bg-red-950/80 p-4 border border-red-800/60 text-sm text-red-200 flex items-start gap-2.5 animate-bounce">
          <AlertCircle size={18} className="shrink-0 mt-0.5 text-red-400 animate-pulse" />
          <span className="font-semibold">{errorMessage}</span>
        </div>
      )}

      {/* Visual Workflow Pipeline Progress Bar */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/20 p-5 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 font-mono">
          <span>Workflow Execution Progress</span>
          <span className="text-indigo-400 animate-pulse">
            {isPipelineComplete 
              ? "All Phases Completed" 
              : pollingActive 
                ? "Running Orchestrated Pipeline..." 
                : "System Idle"}
          </span>
        </div>
        <div className="w-full bg-slate-950 rounded-full h-3.5 border border-slate-800/60 overflow-hidden p-0.5 relative">
          <div 
            className="bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 h-full rounded-full transition-all duration-1000 ease-out shadow-[0_0_8px_rgba(99,102,241,0.5)]"
            style={{ 
              width: `${
                aiLogs.length === 0 
                  ? 0 
                  : (aiLogs.filter(l => l.status === 'Completed').length / 5) * 100
              }%` 
            }}
          />
        </div>
        <div className="grid grid-cols-5 text-center mt-3.5 text-[10px] font-bold text-slate-500 font-mono tracking-wider">
          <span className={aiLogs.find(l=>l.agent_name === agentsConfig[0].name)?.status === 'Completed' ? 'text-emerald-400 font-extrabold shadow-sm' : ''}>01. Analysis</span>
          <span className={aiLogs.find(l=>l.agent_name === agentsConfig[1].name)?.status === 'Completed' ? 'text-emerald-400 font-extrabold shadow-sm' : ''}>02. Breakdown</span>
          <span className={aiLogs.find(l=>l.agent_name === agentsConfig[2].name)?.status === 'Completed' ? 'text-emerald-400 font-extrabold shadow-sm' : ''}>03. Resource</span>
          <span className={aiLogs.find(l=>l.agent_name === agentsConfig[3].name)?.status === 'Completed' ? 'text-emerald-400 font-extrabold shadow-sm' : ''}>04. Sprint</span>
          <span className={aiLogs.find(l=>l.agent_name === agentsConfig[4].name)?.status === 'Completed' ? 'text-emerald-400 font-extrabold shadow-sm' : ''}>05. Risk Audit</span>
        </div>
      </div>

      {/* Visual Agent Workflow Stepper */}
      <div className="grid gap-6 lg:grid-cols-5 md:grid-cols-2 grid-cols-1">
        {agentsConfig.map((config, index) => {
          const log = getAgentLog(config.name);
          const stepNum = index + 1;
          
          let statusColor = "border-slate-800 bg-slate-900/30 hover:border-slate-700 shadow-xl hover:shadow-slate-900/50";
          let statusText = "Pending";
          let statusIcon = <div className="h-2.5 w-2.5 rounded-full bg-slate-700 shadow-[0_0_8px_rgba(100,116,139,0.5)]" />;
          let stateGlow = "hover:shadow-[0_8px_30px_rgba(255,255,255,0.01)]";

          if (log) {
            if (log.status === 'Running') {
              statusColor = "border-indigo-500 bg-indigo-950/20 shadow-[0_4px_30px_rgba(99,102,241,0.15)] animate-[pulse_3s_infinite]";
              statusText = "Running";
              statusIcon = <div className="h-3 w-3 animate-spin rounded-full border-2 border-indigo-400 border-t-transparent shadow-[0_0_8px_rgba(99,102,241,0.4)]" />;
              stateGlow = "shadow-[0_0_20px_rgba(99,102,241,0.1)]";
            } else if (log.status === 'Completed') {
              statusColor = "border-emerald-500/50 bg-emerald-950/10 shadow-[0_4px_25px_rgba(16,185,129,0.05)] hover:border-emerald-550 hover:shadow-[0_4px_30px_rgba(16,185,129,0.15)]";
              statusText = "Completed";
              statusIcon = <CheckCircle2 size={15} className="text-emerald-400 filter drop-shadow-[0_0_3px_rgba(52,211,153,0.4)]" />;
              stateGlow = "hover:shadow-[0_0_20px_rgba(16,185,129,0.08)]";
            } else if (log.status === 'Failed') {
              statusColor = "border-rose-500/50 bg-rose-950/10 shadow-[0_4px_25px_rgba(244,63,94,0.05)] hover:border-rose-550 hover:shadow-[0_4px_30px_rgba(244,63,94,0.15)]";
              statusText = "Failed";
              statusIcon = <AlertCircle size={15} className="text-rose-400 filter drop-shadow-[0_0_3px_rgba(251,113,133,0.4)]" />;
              stateGlow = "hover:shadow-[0_0_20px_rgba(244,63,94,0.08)]";
            } else if (log.status === 'Pending') {
              statusColor = "border-slate-800 bg-slate-900/30 hover:border-indigo-500/30";
              statusText = "Pending";
              statusIcon = <div className="h-2.5 w-2.5 rounded-full bg-slate-500 animate-pulse shadow-[0_0_8px_rgba(148,163,184,0.5)]" />;
            }
          }

          return (
            <div 
              key={config.name} 
              className={`flex flex-col justify-between border rounded-2xl p-5 shadow-2xl transition-all duration-350 hover:-translate-y-1.5 backdrop-blur-md cursor-default select-none ${statusColor} ${stateGlow}`}
            >
              <div>
                {/* Header Step indicators */}
                <div className="flex items-center justify-between mb-4">
                  <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 font-mono text-[11px] font-black text-white shadow-[0_2px_8px_rgba(99,102,241,0.4)] border border-indigo-400/20">
                    0{stepNum}
                  </span>
                  <div className={`flex items-center gap-1.5 font-mono text-[10px] font-black uppercase tracking-wider px-2 py-1 rounded-md ${
                    statusText === 'Running' 
                      ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shadow-inner' 
                      : statusText === 'Completed' 
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-inner' 
                        : statusText === 'Failed' 
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20 shadow-inner'
                          : 'bg-slate-850/50 text-slate-400 border border-slate-700/20 shadow-inner'
                  }`}>
                    {statusIcon}
                    <span>{statusText}</span>
                  </div>
                </div>

                {/* Agent Details */}
                <h3 className="text-sm font-extrabold text-white leading-snug tracking-tight">{config.name}</h3>
                <span className="text-[10px] font-bold text-slate-400 block mt-1 tracking-tight">{config.role}</span>
                <p className="mt-3.5 text-[11px] text-slate-400 leading-relaxed border-t border-slate-800/80 pt-3 font-medium">
                  {config.goal}
                </p>
              </div>

              {/* Actionable items when completed/running */}
              {log && (
                <div className="mt-5 space-y-3.5 border-t border-slate-800/80 pt-3.5">
                  <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                    <span className="flex items-center gap-1.5">
                      <Clock size={12} className="text-slate-500" />
                      Execution Time
                    </span>
                    <span className="font-bold text-slate-200">{(log.execution_time || 0).toFixed(1)}s</span>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <button
                      disabled={!log.input_data}
                      onClick={() => setViewJsonId({ id: log.id, type: 'input' })}
                      className="btn-secondary py-1 text-[10px] font-bold cursor-pointer rounded-lg flex items-center justify-center gap-1"
                    >
                      <Eye size={11} />
                      Input Data
                    </button>
                    <button
                      disabled={!log.output_data}
                      onClick={() => setViewJsonId({ id: log.id, type: 'output' })}
                      className="btn-secondary py-1 text-[10px] font-bold cursor-pointer rounded-lg flex items-center justify-center gap-1"
                    >
                      <Eye size={11} />
                      Output JSON
                    </button>
                  </div>

                  <div className="rounded-lg bg-slate-950 p-2.5 font-mono text-[10px] text-indigo-300 leading-relaxed overflow-hidden h-20 relative border border-slate-800/80 shadow-inner flex flex-col justify-between">
                    <Terminal size={12} className="absolute right-2 top-2 text-slate-700" />
                    <div>
                      <span className="text-slate-500 font-extrabold block uppercase tracking-wider text-[9px] mb-1">Live Telemetry</span>
                      <p className="line-clamp-2 text-slate-300 font-medium leading-relaxed">
                        <span className="text-indigo-500 font-bold select-none mr-1">$</span>
                        {log.logs || 'Initializing execution channel...'}
                      </p>
                    </div>
                    {statusText === 'Running' && (
                      <span className="inline-block h-1.5 w-1 bg-indigo-400 animate-[ping_1.2s_infinite] shrink-0 mt-1" />
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* JSON Viewer Modal */}
      {viewJsonId && (() => {
        const activeLog = aiLogs.find((l) => l.id === viewJsonId.id);
        const codeText = activeLog ? (viewJsonId.type === 'input' ? activeLog.input_data : activeLog.output_data) : null;
        let formattedCode = codeText;
        try {
          if (codeText) formattedCode = JSON.stringify(JSON.parse(codeText), null, 2);
        } catch (_) {}

        return (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4 animate-[fadeIn_0.2s_ease-out]">
            <div className="w-full max-w-2xl rounded-2xl bg-slate-900 shadow-[0_25px_50px_-12px_rgba(0,0,0,0.5)] border border-slate-800 flex flex-col max-h-[80vh] overflow-hidden">
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
                <div className="flex items-center gap-2.5">
                  <Terminal size={16} className="text-indigo-400" />
                  <h3 className="text-sm font-bold text-white tracking-tight">
                    {activeLog?.agent_name} - {viewJsonId.type === 'input' ? 'Raw Input Context' : 'Structured Output'}
                  </h3>
                </div>
                <button 
                  onClick={() => setViewJsonId(null)}
                  className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition-all duration-150 cursor-pointer"
                >
                  <XIcon size={16} />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-6 bg-slate-950 text-slate-200 relative">
                <button
                  onClick={() => handleCopy(formattedCode || '')}
                  className="absolute right-4 top-4 z-10 btn-secondary py-1 px-2.5 text-[10px] font-bold cursor-pointer rounded-md flex items-center gap-1.5"
                >
                  {copied ? (
                    <>
                      <Check size={11} className="text-emerald-400" />
                      <span className="text-emerald-400">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy size={11} />
                      <span>Copy</span>
                    </>
                  )}
                </button>
                <pre className="font-mono text-xs overflow-x-auto whitespace-pre-wrap select-text pr-2 leading-relaxed text-indigo-200">
                  {formattedCode || 'No data recorded for this step.'}
                </pre>
              </div>

              <div className="flex items-center justify-end px-6 py-4 border-t border-slate-800 bg-slate-900 rounded-b-2xl">
                <button
                  onClick={() => setViewJsonId(null)}
                  className="btn-secondary font-bold cursor-pointer"
                >
                  Close Viewer
                </button>
              </div>
            </div>
          </div>
        );
      })()}

      {/* Success Board CTA */}
      {isPipelineComplete && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-2xl backdrop-blur-md animate-[fadeIn_0.5s_ease-out]">
          <div className="flex items-center gap-3.5">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400 shadow-[0_2px_8px_rgba(52,211,153,0.2)]">
              <CheckCircle2 size={20} className="animate-pulse" />
            </div>
            <div>
              <h4 className="text-sm font-extrabold text-white">Sprint Roadmap Generated Successfully!</h4>
              <p className="text-xs text-slate-400 mt-1 font-medium">
                All 5 CrewAI agents completed execution. View your interactive sprint backlog.
              </p>
            </div>
          </div>

          <Link
            to={`/projects/${projectId}`}
            className="btn-emerald font-bold flex items-center gap-1.5 cursor-pointer shadow-[0_2px_10px_rgba(16,185,129,0.15)]"
          >
            <span>Check Sprint Board</span>
            <ArrowRight size={14} />
          </Link>
        </div>
      )}
    </div>
  );
};

const XIcon: React.FC<{ size?: number }> = ({ size = 18 }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
);

export default ControlCenter;
