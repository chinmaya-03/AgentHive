import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../redux';
import { setSprintPlan, setDashboardMetrics, setTeamMembers } from '../../redux/projectSlice';
import { aiApi, teamApi } from '../../api/api';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  PieChart, 
  Pie, 
  Cell, 
  Legend
} from 'recharts';
import { 
  Users, 
  ChevronRight,
  UserCheck,
  Clock,
  ExternalLink,
  ShieldCheck,
  Code,
  Zap,
  Kanban,
  FolderGit2
} from 'lucide-react';

const COLORS = ['#6366f1', '#8b5cf6', '#d946ef', '#10b981', '#f43f5e'];

const Dashboard: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const dispatch = useAppDispatch();
  
  const { sprintPlan, dashboardMetrics, teamMembers } = useAppSelector((state) => state.projects);
  const [activeTab, setActiveTab] = useState<'board' | 'developers' | 'analytics' | 'risks'>('board');
  const [fetchingPlan, setFetchingPlan] = useState(false);

  const fetchDashboardData = () => {
    if (!projectId) return;
    setFetchingPlan(true);
    
    aiApi.getPlan(projectId)
      .then((res) => {
        dispatch(setSprintPlan(res.data));
      })
      .catch((err) => console.error('Failed fetching plan', err));

    aiApi.getDashboardMetrics(projectId)
      .then((res) => {
        dispatch(setDashboardMetrics(res.data));
      })
      .catch((err) => console.error('Failed fetching metrics', err))
      .finally(() => setFetchingPlan(false));

    teamApi.listMembers(projectId)
      .then((res) => {
        dispatch(setTeamMembers(res.data));
      })
      .catch((err) => console.error('Failed fetching team members', err));
  };

  useEffect(() => {
    fetchDashboardData();
  }, [projectId]);

  if (fetchingPlan && !sprintPlan) {
    return (
      <div className="flex h-96 flex-col items-center justify-center space-y-4">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent"></div>
        <p className="text-xs font-bold text-slate-400">Aggregating Sprint Analytics & Kanban Metrics...</p>
      </div>
    );
  }

  // Welcome state if project is empty (no sprints generated yet)
  const isPlanEmpty = !sprintPlan || sprintPlan.sprints.length === 0;

  if (isPlanEmpty) {
    return (
      <div className="max-w-4xl mx-auto space-y-8 py-4">
        {/* Welcome banner */}
        <div className="relative overflow-hidden rounded-2xl border border-slate-900 bg-slate-900/30 p-8 md:p-10 backdrop-blur-xl">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-20" />
          <div className="relative z-10 max-w-xl space-y-6">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600/10 text-indigo-400 border border-indigo-500/25 shadow-inner">
              <FolderGit2 size={20} />
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-black text-white tracking-tight">
                Welcome to AgentHive Planning Suite
              </h2>
              <p className="text-xs text-slate-400 leading-relaxed font-medium">
                AgentHive is an AI-first workspace designed to automate project breakdown, developer skill profiling, load allocation, and sprint risk auditing in one unified platform.
              </p>
            </div>
            <div className="pt-2">
              <Link
                to={`/projects/${projectId}/ai-center`}
                className="btn-primary"
              >
                <Zap size={14} />
                <span>Configure & Run AI Planner</span>
                <ChevronRight size={14} />
              </Link>
            </div>
          </div>
        </div>

        {/* Steps Guide */}
        <div className="grid gap-6 md:grid-cols-3">
          {/* Step 1 */}
          <div className="card-glass p-6 space-y-4 border border-slate-800">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-500/10 font-mono text-[11px] font-black text-indigo-400 border border-indigo-500/20">01</span>
            <div>
              <h3 className="text-xs font-black text-white uppercase tracking-wider">Upload Spec Document</h3>
              <p className="text-[11px] text-slate-400 leading-relaxed font-medium mt-2">
                Upload your core Software Requirements Specification (SRS) file to extract modular components automatically.
              </p>
            </div>
            <Link to={`/projects/${projectId}/srs`} className="text-[11px] font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
              <span>View SRS Manager</span> <ExternalLink size={12} />
            </Link>
          </div>

          {/* Step 2 */}
          <div className="card-glass p-6 space-y-4 border border-slate-800">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-500/10 font-mono text-[11px] font-black text-cyan-400 border border-cyan-500/20">02</span>
            <div>
              <h3 className="text-xs font-black text-white uppercase tracking-wider">Configure Team Profiles</h3>
              <p className="text-[11px] text-slate-400 leading-relaxed font-medium mt-2">
                Declare developers and core roles. The AI planner uses these skills to balance allocation capacity.
              </p>
            </div>
            <Link to={`/projects/${projectId}/team`} className="text-[11px] font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
              <span>Configure Team Matrix</span> <ExternalLink size={12} />
            </Link>
          </div>

          {/* Step 3 */}
          <div className="card-glass p-6 space-y-4 border border-slate-800">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/10 font-mono text-[11px] font-black text-emerald-400 border border-emerald-500/20">03</span>
            <div>
              <h3 className="text-xs font-black text-white uppercase tracking-wider">Run AI Planning Crew</h3>
              <p className="text-[11px] text-slate-400 leading-relaxed font-medium mt-2">
                Initiate the 5 CrewAI agents to plan requirements, estimate tasks, assign resources, and audit backlog risks.
              </p>
            </div>
            <Link to={`/projects/${projectId}/ai-center`} className="text-[11px] font-bold text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
              <span>Execute Orchestration</span> <ExternalLink size={12} />
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Dashboard Stats
  const metrics = dashboardMetrics?.summary || {
    total_team_members: 0,
    total_tasks: 0,
    total_sprints: 0,
    total_risks: 0,
  };

  // Group tasks by developer
  const allTasks = [
    ...(sprintPlan?.sprints.flatMap((s) => s.tasks.map((t) => ({ ...t, sprintName: s.name }))) || []),
    ...(sprintPlan?.unassigned_tasks.map((t) => ({ ...t, sprintName: 'Unscheduled' })) || []),
  ];

  const devMap: Record<string, { id: string; name: string; role: string; email: string; skills: any[]; tasks: any[]; totalHours: number }> = {};

  // Initialize with teamMembers
  teamMembers.forEach((member) => {
    devMap[member.id] = {
      id: member.id,
      name: member.name,
      role: member.role,
      email: member.email,
      skills: member.skills || [],
      tasks: [],
      totalHours: 0,
    };
  });

  // Add tasks to appropriate developer
  allTasks.forEach((task) => {
    if (task.assigned_to) {
      const devId = task.assigned_to.id;
      if (!devMap[devId]) {
        devMap[devId] = {
          id: devId,
          name: task.assigned_to.name,
          role: task.assigned_to.role || 'Developer',
          email: task.assigned_to.email || '',
          skills: task.assigned_to.skills || [],
          tasks: [],
          totalHours: 0,
        };
      }
      devMap[devId].tasks.push(task);
      devMap[devId].totalHours += task.estimated_hours || 0;
    }
  });



  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      
      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-900 gap-6">
        <button
          onClick={() => setActiveTab('board')}
          className={`pb-3 text-xs font-bold uppercase tracking-wider transition-all duration-300 relative flex items-center gap-2 cursor-pointer ${
            activeTab === 'board' ? 'text-indigo-400' : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <Kanban size={14} />
          <span>Sprint Backlog Board</span>
          {activeTab === 'board' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500 rounded-full" />}
        </button>
        <button
          onClick={() => setActiveTab('developers')}
          className={`pb-3 text-xs font-bold uppercase tracking-wider transition-all duration-300 relative flex items-center gap-2 cursor-pointer ${
            activeTab === 'developers' ? 'text-indigo-400' : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <Users size={14} />
          <span>Developer Load Allocation</span>
          {activeTab === 'developers' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500 rounded-full" />}
        </button>
        <button
          onClick={() => setActiveTab('analytics')}
          className={`pb-3 text-xs font-bold uppercase tracking-wider transition-all duration-300 relative flex items-center gap-2 cursor-pointer ${
            activeTab === 'analytics' ? 'text-indigo-400' : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <UserCheck size={14} />
          <span>Analytics & Load Balance</span>
          {activeTab === 'analytics' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500 rounded-full" />}
        </button>
        <button
          onClick={() => setActiveTab('risks')}
          className={`pb-3 text-xs font-bold uppercase tracking-wider transition-all duration-300 relative flex items-center gap-2 cursor-pointer ${
            activeTab === 'risks' ? 'text-indigo-400' : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <ShieldCheck size={14} />
          <span>Risk Auditing Report ({metrics.total_risks})</span>
          {activeTab === 'risks' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500 rounded-full" />}
        </button>
      </div>

      {/* Dynamic Tab Render */}
      {activeTab === 'developers' && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Object.values(devMap).map((dev) => {
            // Calculate workload percentage (assuming 40 hrs capacity)
            const workloadPct = Math.min(Math.round((dev.totalHours / 40) * 100), 150);
            const loadStatus = workloadPct > 100 ? 'Overloaded' : workloadPct > 80 ? 'Heavy' : 'Optimal';
            const loadBadgeColor = loadStatus === 'Overloaded' 
              ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' 
              : loadStatus === 'Heavy' 
              ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' 
              : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';

            return (
              <div 
                key={dev.id} 
                className="card-glass card-glass-hover p-6 space-y-4 flex flex-col justify-between border border-slate-800"
              >
                <div>
                  {/* Developer Header */}
                  <div className="flex items-start justify-between border-b border-slate-900 pb-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 font-extrabold text-xs shadow-inner">
                        {dev.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h3 className="text-xs font-black text-white uppercase tracking-wide">{dev.name}</h3>
                        <span className="text-[10px] text-slate-400 font-bold block mt-0.5">{dev.role}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-[9px] font-black uppercase tracking-wider border ${loadBadgeColor}`}>
                        {loadStatus}
                      </span>
                    </div>
                  </div>

                  {/* Dev Skills List */}
                  {dev.skills && dev.skills.length > 0 && (
                    <div className="py-3.5 border-b border-slate-900 flex flex-wrap gap-1.5">
                      {dev.skills.slice(0, 3).map((s, index) => (
                        <span key={index} className="text-[9px] font-bold bg-slate-900 border border-slate-800 text-slate-300 rounded-md px-2 py-0.5 uppercase tracking-wide">
                          {s.name} ({s.proficiency_level.charAt(0)})
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Capacity Progress Bar */}
                  <div className="py-4 space-y-2">
                    <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                      <span>Weekly Capacity Load</span>
                      <span className="font-bold text-slate-200">{dev.totalHours} hrs / 40 hrs ({workloadPct}%)</span>
                    </div>
                    <div className="w-full bg-slate-950 rounded-full h-2 border border-slate-900 overflow-hidden p-0.5">
                      <div 
                        className={`h-full rounded-full transition-all duration-500 ${
                          workloadPct > 100 ? 'bg-rose-500' : workloadPct > 80 ? 'bg-amber-500' : 'bg-emerald-500'
                        }`}
                        style={{ width: `${Math.min(workloadPct, 100)}%` }}
                      />
                    </div>
                  </div>

                  {/* Developer Tasks list */}
                  <div className="space-y-2 mt-2">
                    <span className="text-[9px] font-black uppercase tracking-wider text-slate-500 block">Assigned Tasks ({dev.tasks.length})</span>
                    {dev.tasks.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-6 text-center text-slate-500 border border-dashed border-slate-800/80 rounded-xl bg-slate-950/20">
                        <UserCheck size={16} className="opacity-40 mb-1 text-slate-400" />
                        <span className="text-[10px] font-bold text-slate-400">No tasks allocated</span>
                      </div>
                    ) : (
                      <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                        {dev.tasks.map((task) => (
                          <div 
                            key={task.id} 
                            className="bg-slate-950/80 border border-slate-905 p-3 rounded-xl space-y-2 hover:border-slate-800 transition-all duration-150"
                          >
                            <div className="flex items-center justify-between">
                              <h4 className="text-[11px] font-bold text-slate-200 line-clamp-1">{task.title}</h4>
                              <span className="font-mono text-[9px] font-bold text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded-md border border-indigo-500/20">{task.estimated_hours}h</span>
                            </div>
                            <div className="flex items-center justify-between text-[9px] text-slate-500 font-bold uppercase tracking-wider">
                              <span>{task.category}</span>
                              <span className="text-slate-400">{task.sprintName}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {activeTab === 'board' && (
        <div className="grid gap-6 md:grid-cols-3">
          {sprintPlan?.sprints.map((sprint, idx) => {
            const sprintNum = idx + 1;
            
            // Collect unique developer profiles working in this sprint
            const devAvatars: string[] = [];
            sprint.tasks.forEach((t: any) => {
              if (t.assigned_to && !devAvatars.includes(t.assigned_to.name)) {
                devAvatars.push(t.assigned_to.name);
              }
            });

            return (
              <div 
                key={sprint.id} 
                className="card-glass card-glass-hover p-6 space-y-4 flex flex-col justify-between border border-slate-800"
              >
                {/* Sprint Header */}
                <div>
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[9px] font-black uppercase text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 rounded px-1.5 py-0.5">
                          Sprint 0{sprintNum}
                        </span>
                        <span className="text-[10px] font-bold text-slate-400">Roadmap</span>
                      </div>
                      <h3 className="text-base font-extrabold text-white mt-1.5 leading-snug">{sprint.name}</h3>
                    </div>
                    <div className="text-right">
                      <span className="flex items-center gap-1 font-mono text-[10px] font-black text-indigo-400 bg-indigo-500/10 rounded-lg px-2.5 py-1 border border-indigo-500/20">
                        <Clock size={11} />
                        {sprint.total_hours} hrs
                      </span>
                    </div>
                  </div>

                  <p className="mt-3 text-[11px] text-slate-400 leading-relaxed border-b border-slate-900 pb-3.5 italic">
                    "{sprint.goal || 'Optimized sprint breakdown.'}"
                  </p>

                  {/* Completion, Priority & Collaborators */}
                  <div className="py-3 border-b border-slate-900 flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-1">
                      <span className="text-[9px] font-extrabold uppercase tracking-wider text-slate-500">Priority:</span>
                      <span className="inline-block rounded px-1.5 py-0.5 text-[9px] font-black uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        High
                      </span>
                    </div>
                    
                    {/* Collaborative Avatars overlap */}
                    {devAvatars.length > 0 && (
                      <div className="flex items-center">
                        <span className="text-[9px] font-extrabold uppercase tracking-wider text-slate-500 mr-2">Devs:</span>
                        <div className="flex -space-x-2">
                          {devAvatars.slice(0, 4).map((name, index) => (
                            <div 
                              key={index}
                              title={name}
                              className="h-5.5 w-5.5 rounded-full border border-slate-900 bg-gradient-to-tr from-indigo-600 to-blue-600 text-white text-[9px] font-black flex items-center justify-center cursor-default shadow"
                            >
                              {name.charAt(0).toUpperCase()}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Interactive Progress Tracking */}
                  <div className="py-3 border-b border-slate-900 space-y-2">
                    <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                      <span>Sprint Allocation</span>
                      <span className="font-bold text-slate-200">{sprint.tasks.length} items ({sprint.total_hours}h)</span>
                    </div>
                    <div className="w-full bg-slate-950 rounded-full h-1.5 border border-slate-900 overflow-hidden">
                      <div 
                        className="bg-indigo-500 h-full rounded-full transition-all duration-700 shadow-[0_0_8px_rgba(99,102,241,0.4)]"
                        style={{ width: `100%` }}
                      />
                    </div>
                  </div>

                  {/* Sprint Tasks list */}
                  <div className="mt-4 space-y-2.5">
                    {sprint.tasks.map((task) => (
                      <div 
                        key={task.id} 
                        className="bg-slate-950/80 border border-slate-900 rounded-xl p-3.5 space-y-3 hover:border-slate-800 transition-all duration-150 group"
                      >
                        <div>
                          {/* Header Tags */}
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="font-mono text-[8px] font-black tracking-widest uppercase text-slate-500">
                              {task.category}
                            </span>
                            <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                              task.difficulty === 'Hard' 
                                ? 'bg-rose-500/15 text-rose-400 border border-rose-500/20' 
                                : task.difficulty === 'Medium' 
                                ? 'bg-amber-500/15 text-amber-400 border border-amber-500/20' 
                                : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
                            }`}>
                              {task.difficulty}
                            </span>
                          </div>
                          <h4 className="text-xs font-bold text-slate-200 group-hover:text-indigo-400 transition-colors line-clamp-1">{task.title}</h4>
                          <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                            {task.description}
                          </p>
                        </div>

                        {/* Developer Assignment Badge */}
                        {task.assigned_to && (
                          <div className="flex items-center justify-between border-t border-slate-900 pt-2.5 mt-2.5">
                            <div className="flex items-center gap-2">
                              <div className="flex h-5 w-5 items-center justify-center rounded-full bg-gradient-to-tr from-indigo-600 to-blue-600 text-white font-extrabold text-[8px]">
                                {task.assigned_to.name.charAt(0)}
                              </div>
                              <div className="flex flex-col">
                                <span className="text-[9px] font-extrabold text-slate-300 leading-none">{task.assigned_to.name}</span>
                              </div>
                            </div>

                            <span className="font-mono text-[9px] font-bold text-slate-500">{task.estimated_hours}h</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="grid gap-8 md:grid-cols-2">
          {/* Workload Bar Chart */}
          <div className="card-glass p-6 space-y-4 border border-slate-800">
            <h3 className="text-xs font-black text-white uppercase tracking-wider flex items-center gap-2">
              <UserCheck size={14} className="text-indigo-400" />
              <span>Developer Workload Distribution</span>
            </h3>
            {dashboardMetrics?.developer_workloads && (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dashboardMetrics.developer_workloads} margin={{ left: -20, bottom: 5 }}>
                    <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#020617', borderColor: '#1e293b', borderRadius: '0.75rem', color: '#fff', fontSize: 11 }} />
                    <Bar dataKey="hours" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
            <p className="text-[11px] text-slate-400 text-center font-medium leading-relaxed">
              Total hours of planned tasks allocated to each developer resource compared to 40 hours standard.
            </p>
          </div>

          {/* Categories Pie Chart */}
          <div className="card-glass p-6 space-y-4 border border-slate-800">
            <h3 className="text-xs font-black text-white uppercase tracking-wider flex items-center gap-2">
              <Code size={14} className="text-indigo-400" />
              <span>Tasks by Technical Category</span>
            </h3>
            {dashboardMetrics?.tasks_by_category && (
              <div className="h-64 flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={dashboardMetrics.tasks_by_category}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {dashboardMetrics.tasks_by_category.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#020617', borderColor: '#1e293b', borderRadius: '0.75rem', color: '#fff', fontSize: 11 }} />
                    <Legend verticalAlign="bottom" height={36} iconSize={8} iconType="circle" wrapperStyle={{ fontSize: 10, fontWeight: 'bold' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
            <p className="text-[11px] text-slate-400 text-center font-medium leading-relaxed">
              Distribution of engineering backlog items across software domains.
            </p>
          </div>
        </div>
      )}

      {activeTab === 'risks' && (
        <div className="space-y-6">
          <div className="card-glass p-6 space-y-5 border border-slate-800">
            <h3 className="text-xs font-black text-white uppercase tracking-wider flex items-center gap-2">
              <ShieldCheck size={14} className="text-indigo-400" />
              <span>AI Risk Audit Reports</span>
            </h3>

            {dashboardMetrics?.risks?.items.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center text-emerald-400">
                <ShieldCheck size={32} className="mb-2" />
                <h4 className="text-xs font-black uppercase tracking-wider">No critical risks identified</h4>
                <p className="text-[11px] text-slate-400 max-w-xs mt-2 font-medium">
                  The Risk Analysis Agent verified balanced developer workloads and dependency ordering.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {sprintPlan?.risks.map((risk) => (
                  <div 
                    key={risk.id} 
                    className="flex flex-col md:flex-row items-start md:items-center justify-between border border-slate-900 rounded-xl p-5 gap-4 bg-slate-950/40 hover:border-slate-850 transition-all duration-300"
                  >
                    <div className="flex items-start gap-4">
                      <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border font-black text-xs ${
                        risk.severity === 'High' 
                          ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' 
                          : risk.severity === 'Medium' 
                          ? 'bg-amber-500/10 border-amber-500/20 text-amber-400' 
                          : 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400'
                      }`}>
                        {risk.severity.charAt(0)}
                      </div>

                      <div className="space-y-1">
                        <span className="text-[9px] font-black uppercase tracking-widest text-slate-500">{risk.risk_type}</span>
                        <h4 className="text-xs font-extrabold text-white leading-snug">{risk.description}</h4>
                        <p className="text-[11px] text-slate-300 leading-relaxed mt-1.5">
                          <span className="text-indigo-400 font-extrabold uppercase text-[9px] tracking-wider mr-1">Recommendation:</span>
                          {risk.recommendation}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
