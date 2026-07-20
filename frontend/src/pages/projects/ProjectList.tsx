import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../redux';
import { setProjects, setProjectLoading, setProjectError, setCurrentProject } from '../../redux/projectSlice';
import { projectsApi, extractErrorMessage } from '../../api/api';
import { 
  FolderGit2, 
  Plus, 
  Trash2, 
  ArrowRight,
  Clock,
  Activity,
  Zap,
  Bot,
  Layers,
  ShieldCheck,
  Kanban
} from 'lucide-react';

const ProjectList: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { list: projects, loading, error } = useAppSelector((state) => state.projects);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [creatingDemo, setCreatingDemo] = useState(false);

  const fetchProjects = () => {
    dispatch(setProjectLoading(true));
    projectsApi.list()
      .then((res) => {
        dispatch(setProjects(res.data));
      })
      .catch((err) => {
        const msg = extractErrorMessage(err, 'Failed to load projects.');
        dispatch(setProjectError(msg));
      });
  };

  useEffect(() => {
    fetchProjects();
  }, [dispatch]);

  const handleCreateDemo = async () => {
    setCreatingDemo(true);
    try {
      const demoData = {
        name: "E-Commerce Microservices AI Platform",
        description: "Production SaaS platform requirement spec including user authentication, payment processing, inventory webhooks, and CrewAI sprint planning.",
        status: "active"
      };
      const res = await projectsApi.create(demoData);
      const newProj = res.data;
      dispatch(setCurrentProject(newProj));
      fetchProjects();
      navigate(`/projects/${newProj.id}`);
    } catch (err: any) {
      alert(extractErrorMessage(err, 'Failed to generate demo project.'));
    } finally {
      setCreatingDemo(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    if (!confirm('Are you sure you want to delete this project? All associated tasks, sprints, team members, and AI telemetry will be deleted.')) {
      return;
    }
    
    setDeletingId(id);
    try {
      await projectsApi.delete(id);
      fetchProjects();
    } catch (err: any) {
      alert(extractErrorMessage(err, 'Failed to delete project.'));
    } finally {
      setDeletingId(null);
    }
  };

  if (loading && projects.length === 0) {
    return (
      <div className="flex h-screen flex-col items-center justify-center space-y-4 bg-slate-950">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent"></div>
        <p className="text-xs font-bold text-slate-400">Loading AgentHive Workspaces...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-slate-950 text-slate-100 font-sans">
      {/* Small Navbar */}
      <header className="flex h-16 items-center justify-between border-b border-slate-900 bg-slate-950 px-8">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600/10 text-indigo-400 border border-indigo-500/25 shadow-inner">
            <FolderGit2 size={16} />
          </div>
          <span className="text-base font-extrabold tracking-tight text-white">
            AgentHive Workspaces
          </span>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-10 space-y-8">
        {/* Top Banner / Hero */}
        <div className="relative overflow-hidden rounded-2xl border border-slate-900 bg-slate-900/30 p-8 backdrop-blur-xl">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-20" />
          <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div className="space-y-3.5 max-w-2xl">
              <div className="inline-flex items-center gap-2 rounded-full bg-indigo-500/10 px-3 py-1 text-[10px] font-black uppercase tracking-wider text-indigo-400 ring-1 ring-indigo-500/25">
                <FolderGit2 size={11} />
                <span>Multi-Agent Sprint Orchestrator</span>
              </div>
              <h1 className="text-3xl font-black text-white tracking-tight sm:text-4xl">
                Sprint Planning Workspace
              </h1>
              <p className="text-xs text-slate-400 leading-relaxed font-medium">
                Initialize your workspace and upload raw requirements documents. Our 5-stage CrewAI planner pipeline analyzes the specifications, breakdown engineering tasks, assigns resource capacities, and audits risk metrics.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 shrink-0">
              <button
                onClick={handleCreateDemo}
                disabled={creatingDemo}
                className="btn-secondary font-bold"
                title="Instantly generate a sample project with sample requirements"
              >
                {creatingDemo ? (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                ) : (
                  <Zap size={14} className="text-amber-400" />
                )}
                <span>Generate Demo Workspace</span>
              </button>

              <Link
                to="/projects/new"
                className="btn-primary"
              >
                <Plus size={14} />
                <span>Create Project</span>
              </Link>
            </div>
          </div>

          {/* Stats Row */}
          <div className="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-slate-900 pt-6 font-mono">
            <div>
              <span className="block text-[9px] uppercase tracking-wider text-slate-550 font-black">Active Workspace</span>
              <span className="text-xl font-bold text-white mt-1 block">{projects.length}</span>
            </div>
            <div>
              <span className="block text-[9px] uppercase tracking-wider text-slate-550 font-black">Agent Pipeline</span>
              <span className="text-xl font-bold text-emerald-400 mt-1 block flex items-center gap-1.5">
                <Bot size={16} /> 5 CrewAI Deployed
              </span>
            </div>
            <div>
              <span className="block text-[9px] uppercase tracking-wider text-slate-550 font-black">LLM Provider</span>
              <span className="text-xl font-bold text-cyan-400 mt-1 block">Groq Llama 70B</span>
            </div>
            <div>
              <span className="block text-[9px] uppercase tracking-wider text-slate-550 font-black">Telemetry Sync</span>
              <span className="text-xl font-bold text-indigo-400 mt-1 block">Real-time Logs</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="rounded-xl bg-red-955 p-4 border border-red-800/60 text-xs text-red-200 font-bold animate-pulse">
            {error}
          </div>
        )}

        {/* Projects Grid or Empty State */}
        {projects.length === 0 ? (
          <div className="card-glass p-12 text-center border border-slate-800 space-y-6">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shadow-lg shadow-indigo-500/10">
              <FolderGit2 size={28} />
            </div>
            <div className="max-w-md mx-auto space-y-2">
              <h3 className="text-sm font-black uppercase tracking-wider text-white">No active workspaces initialized</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-medium">
                Get started by initializing a custom project workspace, or generate a fully-featured demo workspace to instantly try out AgentHive planning capabilities.
              </p>
            </div>

            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={handleCreateDemo}
                disabled={creatingDemo}
                className="btn-emerald text-xs"
              >
                {creatingDemo ? (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                ) : (
                  <Zap size={14} />
                )}
                <span>Generate Demo Workspace</span>
              </button>

              <Link
                to="/projects/new"
                className="btn-primary"
              >
                <Plus size={14} />
                <span>Create Custom Project</span>
              </Link>
            </div>

            {/* Onboarding Cards Preview */}
            <div className="mt-12 pt-8 border-t border-slate-900 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
              <div className="p-5 rounded-xl bg-slate-900/20 border border-slate-900">
                <div className="flex items-center gap-2 text-indigo-400 font-bold text-xs mb-2 uppercase tracking-wide">
                  <Layers size={14} />
                  <span>1. Upload Requirement Spec</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed font-medium">
                  Upload PDF, DOCX, or plain text SRS documents. Our document parser extracts modules and key capabilities automatically.
                </p>
              </div>

              <div className="p-5 rounded-xl bg-slate-900/20 border border-slate-900">
                <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs mb-2 uppercase tracking-wide">
                  <Kanban size={14} />
                  <span>2. Multi-Agent Breakdown</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed font-medium">
                  5 specialized AI agents work in sequence: Requirement Analyst ➔ Task Specialist ➔ Skill Matcher ➔ Sprint Planner ➔ Risk Auditor.
                </p>
              </div>

              <div className="p-5 rounded-xl bg-slate-900/20 border border-slate-900">
                <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs mb-2 uppercase tracking-wide">
                  <ShieldCheck size={14} />
                  <span>3. Interactive Board & Risks</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed font-medium">
                  Review structured sprint cards, workload analytics by developer, skill matching matrix, and automated risk analysis reports.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-black uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <FolderGit2 size={16} className="text-indigo-400" />
                <span>Active Workspace Directory</span>
              </h2>
              <span className="text-2xs text-slate-500 font-bold uppercase tracking-wider">{projects.length} workspaces available</span>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {projects.map((project) => (
                <Link
                  key={project.id}
                  to={`/projects/${project.id}`}
                  className="card-glass card-glass-hover p-6 flex flex-col justify-between group relative border border-slate-800"
                >
                  <div>
                    {/* Status Pill & Actions */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-1.5 rounded bg-emerald-500/10 px-2 py-0.5 text-[9px] font-black uppercase tracking-wider text-emerald-450 border border-emerald-500/20 shadow-sm">
                        <Activity size={10} />
                        <span>{project.status || 'Active'}</span>
                      </div>

                      <button
                        disabled={deletingId === project.id}
                        onClick={(e) => handleDelete(project.id, e)}
                        className="rounded-lg p-1.5 text-slate-500 hover:bg-rose-500/20 hover:text-rose-450 transition-all duration-150 opacity-0 group-hover:opacity-100 focus:opacity-100 cursor-pointer"
                        title="Delete Workspace"
                      >
                        {deletingId === project.id ? (
                          <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-400 border-t-transparent" />
                        ) : (
                          <Trash2 size={14} />
                        )}
                      </button>
                    </div>

                    {/* Title & Description */}
                    <h3 className="text-sm font-extrabold text-white group-hover:text-indigo-400 transition-colors uppercase tracking-wide line-clamp-1">
                      {project.name}
                    </h3>
                    <p className="mt-2 text-xs text-slate-400 line-clamp-2 min-h-[2.5rem] leading-relaxed font-medium">
                      {project.description || 'Software workspace for AI requirement parsing and sprint generation.'}
                    </p>
                  </div>

                  {/* Footer details */}
                  <div className="mt-6 flex items-center justify-between border-t border-slate-900 pt-4 font-mono">
                    <span className="flex items-center gap-1.5 text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                      <Clock size={12} />
                      {new Date(project.created_at).toLocaleDateString()}
                    </span>
                    <span className="flex items-center gap-1 text-[10px] font-black text-indigo-400 uppercase tracking-wider group-hover:translate-x-1 transition-all duration-300">
                      Open Workspace
                      <ArrowRight size={12} />
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default ProjectList;
