import React, { useEffect } from 'react';
import { Outlet, Link, useNavigate, useParams, useLocation } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../redux';
import { logout } from '../redux/authSlice';
import { projectsApi } from '../api/api';
import { setProjects, setCurrentProject, clearActiveProject } from '../redux/projectSlice';
import { 
  LayoutDashboard, 
  Users, 
  Cpu, 
  FolderGit2, 
  LogOut, 
  ChevronDown,
  User as UserIcon,
  FileText,
  Plus
} from 'lucide-react';

const Layout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  const { projectId } = useParams<{ projectId: string }>();
  
  const { user } = useAppSelector((state) => state.auth);
  const { list: projects } = useAppSelector((state) => state.projects);

  // Fetch projects list on mount
  useEffect(() => {
    projectsApi.list()
      .then((res) => {
        dispatch(setProjects(res.data));
        // If a projectId is in URL, set active project
        if (projectId) {
          const active = res.data.find((p: any) => p.id === projectId);
          if (active) dispatch(setCurrentProject(active));
        }
      })
      .catch((err) => console.error('Failed fetching projects', err));
  }, [dispatch, projectId]);

  const handleProjectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedId = e.target.value;
    if (selectedId === '_new') {
      navigate('/projects/new');
      return;
    }
    
    if (selectedId) {
      const active = projects.find((p) => p.id === selectedId);
      if (active) {
        dispatch(setCurrentProject(active));
        navigate(`/projects/${selectedId}`);
      }
    } else {
      dispatch(clearActiveProject());
      navigate('/projects');
    }
  };

  const handleLogout = () => {
    dispatch(logout());
    dispatch(clearActiveProject());
    navigate('/login');
  };

  // Helper to determine if navigation link is active
  const isActive = (path: string) => {
    return location.pathname === path || (path !== `/projects/${projectId}` && location.pathname.startsWith(path));
  };

  const menuItems = projectId ? [
    {
      name: 'Sprint Board',
      path: `/projects/${projectId}`,
      icon: <LayoutDashboard size={16} />
    },
    {
      name: 'Requirements SRS',
      path: `/projects/${projectId}/srs`,
      icon: <FileText size={16} />
    },
    {
      name: 'Team & Skill Matrix',
      path: `/projects/${projectId}/team`,
      icon: <Users size={16} />
    },
    {
      name: 'AI Agent Telemetry',
      path: `/projects/${projectId}/ai-center`,
      icon: <Cpu size={16} />
    },
  ] : [];

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 font-sans">
      {/* Sidebar */}
      <aside className="flex w-64 flex-col border-r border-slate-900 bg-slate-950 shrink-0">
        {/* Brand Logo */}
        <div className="flex h-16 items-center px-6 border-b border-slate-900/60 justify-between">
          <Link to="/projects" className="flex items-center gap-2.5 group">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600/10 text-indigo-400 border border-indigo-500/25 shadow-inner group-hover:scale-105 transition-all duration-300">
              <FolderGit2 size={16} className="group-hover:rotate-6 transition-all" />
            </div>
            <div className="flex flex-col">
              <span className="font-sans text-base font-extrabold tracking-tight text-white group-hover:text-indigo-300 transition-colors">
                AgentHive
              </span>
            </div>
          </Link>
        </div>

        {/* Sidebar Links */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          {projectId ? (
            <div className="space-y-4">
              <div className="px-3 text-[10px] font-black uppercase tracking-widest text-slate-500">
                Workspace Menu
              </div>
              <div className="space-y-1.5">
                {menuItems.map((item) => {
                  const active = isActive(item.path);
                  return (
                    <Link
                      key={item.name}
                      to={item.path}
                      className={`flex items-center gap-3 rounded-xl px-3.5 py-2.5 font-sans text-xs font-bold transition-all duration-300 relative group overflow-hidden border border-transparent ${
                        active
                          ? 'bg-slate-900/90 text-white border-slate-800 shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)]'
                          : 'text-slate-400 hover:bg-slate-900/40 hover:text-slate-200'
                      }`}
                    >
                      {active && (
                        <div className="absolute left-0 top-3 bottom-3 w-1 bg-indigo-500 rounded-full" />
                      )}
                      <span className={`${active ? 'text-indigo-400' : 'text-slate-400 group-hover:text-slate-200'} transition-colors`}>
                        {item.icon}
                      </span>
                      <span>{item.name}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-10 px-4 text-center rounded-xl bg-slate-900/20 border border-slate-900">
              <div className="h-10 w-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mb-3">
                <FolderGit2 size={20} />
              </div>
              <p className="text-[11px] text-slate-400 font-bold leading-relaxed">
                Select or create a project workspace to begin multi-agent sprint planning.
              </p>
            </div>
          )}
        </div>

        {/* Bottom Workspace Links */}
        <div className="border-t border-slate-900 p-4 space-y-2">
          <Link
            to="/projects"
            className={`flex items-center gap-3 rounded-xl px-3.5 py-2.5 font-sans text-xs font-bold transition-all duration-300 border border-transparent ${
              location.pathname === '/projects'
                ? 'bg-slate-900/90 text-white border-slate-800 shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)]'
                : 'text-slate-400 hover:bg-slate-900/40 hover:text-slate-200'
            }`}
          >
            <FolderGit2 size={16} />
            <span>All Projects</span>
          </Link>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden bg-slate-950">
        {/* Top Navbar */}
        <header className="flex h-16 items-center justify-between border-b border-slate-900 bg-slate-950/80 backdrop-blur-md px-8 shadow-sm">
          {/* Project Selector dropdown */}
          <div className="flex items-center gap-4">
            <div className="relative flex items-center">
              <FolderGit2 size={14} className="absolute left-3.5 text-slate-400" />
              <select
                value={projectId || ''}
                onChange={handleProjectChange}
                className="h-9 rounded-xl border border-slate-800 bg-slate-900/80 pl-10 pr-10 font-sans text-xs font-bold text-white shadow-inner transition-all focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/25 appearance-none cursor-pointer min-w-[220px]"
              >
                <option value="" className="bg-slate-900 text-slate-400">Select Project Workspace</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id} className="bg-slate-900 text-white">
                    {p.name}
                  </option>
                ))}
                <option value="_new" className="bg-slate-900 text-indigo-400 font-bold">+ Create New Project</option>
              </select>
              <ChevronDown size={12} className="absolute right-3.5 pointer-events-none text-slate-400" />
            </div>

            <Link
              to="/projects/new"
              className="hidden sm:flex items-center gap-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 px-3.5 py-2 text-xs font-bold text-slate-200 transition-all duration-300"
            >
              <Plus size={12} />
              <span>New Workspace</span>
            </Link>
          </div>

          {/* User profile & Logout */}
          <div className="flex items-center gap-5">
            {user && (
              <div className="flex items-center gap-3 border-r border-slate-900 pr-5">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-tr from-indigo-600 to-blue-600 text-white font-extrabold text-xs shadow-md">
                  {user.name ? user.name.charAt(0).toUpperCase() : <UserIcon size={14} />}
                </div>
                <div className="flex flex-col">
                  <span className="font-sans text-xs font-extrabold text-white leading-tight">{user.name}</span>
                  <span className="font-sans text-[9px] font-black uppercase tracking-wider text-indigo-400">{user.role || 'Member'}</span>
                </div>
              </div>
            )}

            <button
              onClick={handleLogout}
              className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/60 px-3.5 py-2 font-sans text-xs font-bold text-slate-300 hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/30 transition-all duration-300 cursor-pointer"
            >
              <LogOut size={13} />
              <span>Logout</span>
            </button>
          </div>
        </header>

        {/* Dynamic Outlet Render */}
        <main className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
