import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAppDispatch } from '../../redux';
import { setCurrentProject, setProjectLoading, setProjectError } from '../../redux/projectSlice';
import { projectsApi } from '../../api/api';
import { ChevronLeft, FolderGit2, Sparkles } from 'lucide-react';

const SAMPLE_PROJECT_TEMPLATES = [
  {
    title: "E-Commerce Microservices AI Platform",
    desc: "Comprehensive SaaS application spec covering JWT user authentication, Stripe payment processing gateway, product catalog search, inventory webhooks, and automated order fulfillment."
  },
  {
    title: "Healthcare Patient Portal & Telemedicine System",
    desc: "HIPAA-compliant software spec featuring appointment scheduling, real-time video consultations, electronic health record (EHR) integrations, and automated patient prescription reminders."
  },
  {
    title: "FinTech Automated Portfolio Manager",
    desc: "Real-time stock trading and crypto portfolio analytics engine with websocket market data feeds, automated risk threshold triggers, and tax reporting PDF generators."
  }
];

const CreateProject: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { register, handleSubmit, setValue, formState: { errors } } = useForm({
    defaultValues: {
      name: '',
      description: '',
      status: 'active'
    }
  });

  const onSubmit = async (data: any) => {
    setLoading(true);
    setErrorMessage(null);
    dispatch(setProjectLoading(true));
    try {
      const res = await projectsApi.create(data);
      const newProj = res.data;
      dispatch(setCurrentProject(newProj));
      navigate(`/projects/${newProj.id}`);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to create project. Please try again.';
      setErrorMessage(msg);
      dispatch(setProjectError(msg));
    } finally {
      setLoading(false);
    }
  };

  const handleApplyTemplate = (tpl: { title: string; desc: string }) => {
    setValue('name', tpl.title);
    setValue('description', tpl.desc);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Breadcrumb */}
      <Link 
        to="/projects" 
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-all-custom"
      >
        <ChevronLeft size={16} />
        <span>Back to Projects</span>
      </Link>

      {/* Header */}
      <div>
        <h1 className="font-sans text-3xl font-extrabold text-white tracking-tight">Create New Workspace</h1>
        <p className="mt-1.5 text-sm text-slate-400">
          Initialize an isolated project workspace for SRS document parsing, team skill mapping, and automated sprint backlogs.
        </p>
      </div>

      {/* Quick Template Selector */}
      <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
        <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 uppercase tracking-wider">
          <Sparkles size={14} />
          <span>Quick Template Starter</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          {SAMPLE_PROJECT_TEMPLATES.map((tpl, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleApplyTemplate(tpl)}
              className="p-3 text-left rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800/80 transition-all-custom group"
            >
              <div className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300 line-clamp-1">
                {tpl.title}
              </div>
              <div className="text-2xs text-slate-500 line-clamp-2 mt-1">
                {tpl.desc}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Card Form */}
      <div className="card-glass p-8 border border-slate-800 shadow-2xl">
        {errorMessage && (
          <div className="mb-6 rounded-xl bg-red-950/80 p-4 border border-red-800/60 text-sm text-red-200">
            {errorMessage}
          </div>
        )}

        <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {/* Project Name */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
              Project / Workspace Name
            </label>
            <input
              type="text"
              {...register('name', { required: 'Project name is required' })}
              placeholder="e.g. AgentHive E-Commerce System"
              className={`block w-full h-11 rounded-xl border bg-slate-950 px-4 text-sm text-white placeholder-slate-500 outline-none transition-all-custom ${
                errors.name
                  ? 'border-red-500 focus:ring-2 focus:ring-red-500/40'
                  : 'border-slate-800 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30'
              }`}
            />
            {errors.name && (
              <span className="mt-1 block text-xs font-medium text-red-400">{errors.name.message}</span>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
              Description & System Scope
            </label>
            <textarea
              rows={4}
              {...register('description', { maxLength: { value: 1000, message: 'Description cannot exceed 1000 characters' } })}
              placeholder="Provide context regarding the software requirements, target user personas, and core technical scope..."
              className={`block w-full rounded-xl border bg-slate-950 p-4 text-sm text-white placeholder-slate-500 outline-none transition-all-custom ${
                errors.description
                  ? 'border-red-500 focus:ring-2 focus:ring-red-500/40'
                  : 'border-slate-800 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30'
              }`}
            />
            {errors.description && (
              <span className="mt-1 block text-xs font-medium text-red-400">{errors.description.message}</span>
            )}
          </div>

          {/* Buttons */}
          <div className="flex items-center justify-end gap-3 border-t border-slate-800/80 pt-6">
            <Link
              to="/projects"
              className="btn-secondary"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary"
            >
              {loading ? (
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
              ) : (
                <>
                  <FolderGit2 size={16} />
                  <span>Initialize Workspace</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateProject;
