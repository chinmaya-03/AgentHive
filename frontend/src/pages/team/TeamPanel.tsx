import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useForm, useFieldArray } from 'react-hook-form';
import { useAppDispatch, useAppSelector } from '../../redux';
import { setTeamMembers } from '../../redux/projectSlice';
import { teamApi, aiApi, extractErrorMessage } from '../../api/api';
import { 
  Users, 
  Plus, 
  Trash2, 
  UserPlus, 
  Mail, 
  Code2, 
  ArrowRight,
  Briefcase,
  PlusCircle,
  X,
  AlertCircle,
  Pencil
} from 'lucide-react';

interface Skill {
  id: string;
  name: string;
  category: string;
}

const TeamPanel: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const dispatch = useAppDispatch();
  
  const { teamMembers } = useAppSelector((state) => state.projects);
  const [globalSkills, setGlobalSkills] = useState<Skill[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [sprintPlan, setSprintPlan] = useState<any>(null);
  const [editingMemberId, setEditingMemberId] = useState<string | null>(null);
  const [expandedDevTasks, setExpandedDevTasks] = useState<Record<string, boolean>>({});

  const { register, control, handleSubmit, reset, watch, formState: { errors } } = useForm({
    defaultValues: {
      name: '',
      email: '',
      role: 'Backend Developer',
      skills: [] as Array<{ skill_id: string; proficiency_level: string }>
    }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'skills'
  });

  const watchedSkills = watch('skills') || [];

  const fetchData = () => {
    if (!projectId) return;
    teamApi.listMembers(projectId)
      .then((res) => {
        dispatch(setTeamMembers(res.data));
      })
      .catch((err) => console.error('Failed fetching members', err));

    aiApi.getPlan(projectId)
      .then((res) => {
        setSprintPlan(res.data);
      })
      .catch((err) => console.error('Failed fetching plan for team panel', err));
  };

  useEffect(() => {
    fetchData();

    teamApi.listSkills()
      .then((res) => {
        setGlobalSkills(res.data);
      })
      .catch((err) => console.error('Failed fetching skills registry', err));
  }, [projectId]);

  const handleCloseModal = () => {
    setShowAddModal(false);
    setEditingMemberId(null);
    reset({
      name: '',
      email: '',
      role: 'Backend Developer',
      skills: []
    });
  };

  const handleEditClick = (member: any) => {
    setEditingMemberId(member.id);
    reset({
      name: member.name,
      email: member.email,
      role: member.role,
      skills: member.skills.map((s: any) => ({
        skill_id: s.skill_id,
        proficiency_level: s.proficiency_level
      }))
    });
    setShowAddModal(true);
  };

  const onSubmit = async (data: any) => {
    if (!projectId) return;
    setSubmitting(true);
    setErrorMsg(null);
    try {
      if (editingMemberId) {
        await teamApi.updateMember(projectId, editingMemberId, data);
      } else {
        await teamApi.addMember(projectId, data);
      }
      fetchData();
      handleCloseModal();
    } catch (err: any) {
      setErrorMsg(extractErrorMessage(err, 'Failed to save team member.'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (memberId: string) => {
    if (!projectId || !confirm('Are you sure you want to remove this team member? All their task assignments will be cleared.')) return;
    
    try {
      await teamApi.deleteMember(projectId, memberId);
      fetchData();
    } catch (err: any) {
      alert(extractErrorMessage(err, 'Failed to delete member.'));
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="font-sans text-3xl font-extrabold text-white tracking-tight">Team Configuration</h1>
          <p className="mt-1.5 text-xs text-slate-400 font-medium">
            Define developer resource profiles and skill levels for automated task matching.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary"
        >
          <UserPlus size={14} />
          <span>Add Team Member</span>
        </button>
      </div>

      {/* Team grid list */}
      {teamMembers.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center card-glass border border-slate-800">
          <Users size={32} className="text-slate-650 mb-3" />
          <h3 className="text-sm font-black uppercase tracking-wider text-white">No team members added yet</h3>
          <p className="mt-2 text-xs text-slate-400 max-w-xs leading-relaxed font-medium">
            The multi-agent coordinator needs developer resources to assign tasks to. Click "Add Team Member" to register developers.
          </p>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {teamMembers.map((member) => {
            const devTasks = [
              ...(sprintPlan?.sprints.flatMap((s: any) => s.tasks.map((t: any) => ({ ...t, sprintName: s.name }))) || []),
              ...(sprintPlan?.unassigned_tasks.map((t: any) => ({ ...t, sprintName: 'Unscheduled' })) || [])
            ].filter(t => t.assigned_to?.id === member.id);

            const totalHours = devTasks.reduce((sum, t) => sum + (t.estimated_hours || 0), 0);
            const capacityPct = Math.min(Math.round((totalHours / 40) * 100), 150);
            const isOverloaded = capacityPct > 100;
            const workloadText = isOverloaded ? 'Overloaded' : capacityPct > 80 ? 'Heavy' : 'Optimal';
            const workloadColor = isOverloaded 
              ? 'bg-rose-500/10 text-rose-455 border-rose-500/25' 
              : capacityPct > 80 
              ? 'bg-amber-500/10 text-amber-455 border-amber-500/25' 
              : 'bg-emerald-500/10 text-emerald-455 border-emerald-500/25';

            return (
              <div key={member.id} className="card-glass card-glass-hover p-6 flex flex-col justify-between border border-slate-800 relative group">
                <div>
                  {/* Header bar */}
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-sm font-black text-white uppercase tracking-wide leading-tight">{member.name}</h3>
                      <span className="text-[11px] text-slate-400 block mt-1 flex items-center gap-1.5 font-medium">
                        <Mail size={12} className="text-slate-500" />
                        {member.email}
                      </span>
                    </div>

                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 focus-within:opacity-100 transition-all duration-300">
                      <button
                        onClick={() => handleEditClick(member)}
                        className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-800 hover:text-white transition-all duration-150 cursor-pointer"
                        title="Edit Developer & Skills"
                      >
                        <Pencil size={12} />
                      </button>
                      <button
                        onClick={() => handleDelete(member.id)}
                        className="rounded-lg p-1.5 text-slate-500 hover:bg-rose-500/20 hover:text-rose-400 transition-all duration-150 cursor-pointer"
                        title="Remove Member"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>

                  {/* Role badge */}
                  <div className="flex items-center gap-1.5 text-[10px] font-black uppercase tracking-wider text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 rounded-md px-2.5 py-1 w-max mb-4">
                    <Briefcase size={11} />
                    {member.role}
                  </div>

                  {/* Weekly workload capacity indicator */}
                  <div className="py-3 border-t border-slate-900 space-y-2">
                    <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                      <span>Workload Balance</span>
                      <span className="font-bold text-slate-200">{totalHours}h / 40h ({capacityPct}%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-slate-950 rounded-full h-1.5 border border-slate-900 overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all duration-500 ${
                            isOverloaded ? 'bg-rose-500' : capacityPct > 80 ? 'bg-amber-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${Math.min(capacityPct, 100)}%` }}
                        />
                      </div>
                      <span className={`rounded-md px-1.5 py-0.5 text-[8px] font-black uppercase border tracking-wider ${workloadColor}`}>
                        {workloadText}
                      </span>
                    </div>
                  </div>

                  {/* Skills section */}
                  <div className="space-y-2 border-t border-slate-900 pt-3">
                    <span className="text-[9px] font-black uppercase tracking-wider text-slate-500 block mb-1">Skills & Proficiency</span>
                    {member.skills && member.skills.length > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {member.skills.map((s, idx) => (
                          <div 
                            key={idx} 
                            className="flex items-center gap-1 text-[10px] font-bold border rounded-md px-2 py-0.5 bg-slate-900 text-slate-300 border-slate-800"
                          >
                            <Code2 size={10} className="text-indigo-400" />
                            {s.name}
                            <span className="text-[9px] italic font-black text-indigo-400">({s.proficiency_level.charAt(0)})</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className="text-[10px] text-slate-550 italic font-medium">No skills declared.</span>
                    )}
                  </div>

                  {/* Allotted Tasks section */}
                  <div className="space-y-2 border-t border-slate-900 pt-3.5 mt-3.5">
                    <button
                      onClick={() => {
                        setExpandedDevTasks(prev => ({
                          ...prev,
                          [member.id]: !prev[member.id]
                        }));
                      }}
                      className="flex items-center justify-between w-full text-[10px] font-black uppercase tracking-wider text-slate-500 hover:text-slate-350 transition-colors cursor-pointer"
                    >
                      <span className="flex items-center gap-1.5">
                        <Users size={11} className="text-indigo-400" />
                        <span>Allotted Backlog Tasks ({devTasks.length})</span>
                      </span>
                      <span className="text-indigo-400 text-[9px] font-extrabold uppercase">
                        {expandedDevTasks[member.id] ? 'Hide' : 'Show'}
                      </span>
                    </button>

                    {expandedDevTasks[member.id] && (
                      <div className="space-y-2 mt-2 max-h-40 overflow-y-auto pr-1">
                        {devTasks.length === 0 ? (
                          <span className="text-[10px] text-slate-550 italic block py-1.5 bg-slate-950/20 px-2 rounded-lg border border-dashed border-slate-900">No tasks allotted.</span>
                        ) : (
                          devTasks.map((task: any) => (
                            <div 
                              key={task.id} 
                              className="bg-slate-950/85 border border-slate-900 p-2.5 rounded-xl text-[10px] space-y-1 hover:border-slate-850 transition-all duration-150"
                            >
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-slate-200 line-clamp-1 flex-1 mr-2">{task.title}</span>
                                <span className="font-mono text-slate-400 shrink-0">{task.estimated_hours}h</span>
                              </div>
                              <div className="flex items-center justify-between text-[8px] text-slate-500 font-black uppercase tracking-wider">
                                <span>{task.category}</span>
                                <span className="text-indigo-400/80 font-bold">{task.sprintName}</span>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Next Step CTA */}
      {teamMembers.length > 0 && (
        <div className="flex justify-end pt-4">
          <Link
            to={`/projects/${projectId}/ai-center`}
            className="btn-primary"
          >
            <span>Configure AI Backlog Run</span>
            <ArrowRight size={14} />
          </Link>
        </div>
      )}

      {/* Add Member Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4 animate-[fadeIn_0.2s_ease-out]">
          <div className="w-full max-w-lg rounded-2xl bg-slate-900 shadow-2xl border border-slate-800 flex flex-col max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
              <h3 className="text-sm font-black uppercase tracking-wider text-white">
                {editingMemberId ? 'Edit Project Developer' : 'Add Project Developer'}
              </h3>
              <button 
                onClick={handleCloseModal}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition-all duration-150 cursor-pointer"
              >
                <X size={16} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-5 bg-slate-950/30">
              {errorMsg && (
                <div className="rounded-lg bg-red-955 p-3 text-xs text-red-200 border border-red-800/60 flex items-start gap-2 animate-pulse">
                  <AlertCircle size={14} className="shrink-0 mt-0.5 text-red-405" />
                  <span>{errorMsg}</span>
                </div>
              )}

              <form id="add-member-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div>
                  <label className="block text-[10px] font-black uppercase tracking-wider text-slate-400 mb-1.5">Developer Name</label>
                  <input
                    type="text"
                    {...register('name', { required: 'Name is required' })}
                    placeholder="e.g. Alex Rivers"
                    className="block w-full h-10 rounded-xl border border-slate-800 bg-slate-950 px-3.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                  />
                  {errors.name && <span className="text-[10px] text-red-400 mt-1 block font-bold">{errors.name.message}</span>}
                </div>

                <div>
                  <label className="block text-[10px] font-black uppercase tracking-wider text-slate-400 mb-1.5">Email Address</label>
                  <input
                    type="email"
                    {...register('email', { 
                      required: 'Email is required',
                      pattern: { value: /^\S+@\S+$/i, message: 'Invalid email address' }
                    })}
                    placeholder="e.g. alex@company.com"
                    className="block w-full h-10 rounded-xl border border-slate-800 bg-slate-950 px-3.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                  />
                  {errors.email && <span className="text-[10px] text-red-400 mt-1 block font-bold">{errors.email.message}</span>}
                </div>

                <div>
                  <label className="block text-[10px] font-black uppercase tracking-wider text-slate-400 mb-1.5">Developer Role</label>
                  <select
                    {...register('role')}
                    className="block w-full h-10 rounded-xl border border-slate-800 bg-slate-950 px-3 text-xs text-white focus:border-indigo-500 focus:outline-none cursor-pointer"
                  >
                    <option value="Backend Developer">Backend Developer</option>
                    <option value="Frontend Developer">Frontend Developer</option>
                    <option value="Fullstack Developer">Fullstack Developer</option>
                    <option value="Database Engineer">Database Engineer</option>
                    <option value="QA Engineer">QA Engineer</option>
                    <option value="DevOps Engineer">DevOps Engineer</option>
                  </select>
                </div>

                <div className="border-t border-slate-900 pt-4">
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-[10px] font-black uppercase tracking-wider text-slate-400">Skills declared</label>
                    <button
                      type="button"
                      onClick={() => append({ skill_id: globalSkills[0]?.id || '', proficiency_level: 'Mid' })}
                      className="flex items-center gap-1 text-[10px] font-bold text-indigo-400 hover:text-indigo-300 transition-all duration-300 cursor-pointer"
                    >
                      <PlusCircle size={14} />
                      Add Skill Tag
                    </button>
                  </div>

                  {fields.length === 0 ? (
                    <span className="text-[11px] text-slate-500 italic block py-2">Click "Add Skill Tag" to assign tech stack skills.</span>
                  ) : (
                    <div className="space-y-2">
                      {fields.map((field, index) => {
                        return (
                          <div key={field.id} className="flex items-center gap-3 bg-slate-950 p-2 rounded-xl border border-slate-900">
                            <select
                              {...register(`skills.${index}.skill_id` as const, { required: true })}
                              className="h-9 flex-1 rounded-lg border border-slate-850 bg-slate-900 px-2 text-xs text-white focus:border-indigo-500 focus:outline-none cursor-pointer"
                            >
                              {globalSkills.map((s) => {
                                const isChosen = watchedSkills.some((ws, wsIdx) => ws.skill_id === s.id && wsIdx !== index);
                                return (
                                  <option key={s.id} value={s.id} disabled={isChosen}>
                                    [{s.category}] {s.name}
                                  </option>
                                );
                              })}
                            </select>

                            <select
                              {...register(`skills.${index}.proficiency_level` as const)}
                              className="h-9 w-28 rounded-lg border border-slate-850 bg-slate-900 px-2 text-xs text-white focus:border-indigo-500 focus:outline-none cursor-pointer"
                            >
                              <option value="Junior">Junior</option>
                              <option value="Mid">Mid</option>
                              <option value="Senior">Senior</option>
                            </select>

                            <button
                              type="button"
                              onClick={() => remove(index)}
                              className="text-slate-500 hover:text-rose-400 p-1 cursor-pointer"
                            >
                              <X size={16} />
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </form>
            </div>

            <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-800 bg-slate-900 rounded-b-2xl">
              <button
                type="button"
                onClick={handleCloseModal}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                form="add-member-form"
                disabled={submitting}
                className="btn-primary"
              >
                {submitting ? (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                ) : (
                  <>
                    {editingMemberId ? <Pencil size={12} /> : <Plus size={12} />}
                    <span>{editingMemberId ? 'Save Changes' : 'Register Resource'}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeamPanel;
