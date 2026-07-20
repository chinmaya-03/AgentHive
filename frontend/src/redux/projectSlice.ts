import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface Project {
  id: string;
  name: string;
  description: string;
  status: string;
  created_at: string;
}

interface Requirement {
  id: string;
  project_id?: string;
  original_filename?: string;
  filename?: string;
  file_extension?: string;
  file_type?: string;
  processing_status?: string;
  status?: string;
  extracted_text: string | null;
  upload_timestamp?: string;
  created_at?: string;
}

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: string;
  skills: Array<{
    skill_id: string;
    name: string;
    category: string;
    proficiency_level: string;
  }>;
}

interface AgentLog {
  id: string;
  agent_name: string;
  status: string;
  input_data: string | null;
  output_data: string | null;
  execution_time: number;
  logs: string | null;
  created_at: string;
}

interface SprintPlan {
  sprints: Array<{
    id: string;
    name: string;
    goal: string;
    total_hours: number;
    tasks: Array<any>;
  }>;
  unassigned_tasks: Array<any>;
  risks: Array<{
    id: string;
    risk_type: string;
    description: string;
    severity: string;
    recommendation: string;
  }>;
}

interface DashboardMetrics {
  summary: {
    total_team_members: number;
    total_tasks: number;
    total_sprints: number;
    total_risks: number;
  };
  tasks_by_category: Array<{ name: string; value: number }>;
  developer_workloads: Array<{ name: string; role: string; hours: number; tasks: number }>;
  sprint_statistics: Array<{ name: string; hours: number; tasks: number }>;
  risks: {
    total: number;
    high: number;
    medium: number;
    low: number;
    items: Array<any>;
  };
}

interface ProjectState {
  list: Project[];
  currentProject: Project | null;
  requirements: Requirement[];
  teamMembers: TeamMember[];
  aiLogs: AgentLog[];
  sprintPlan: SprintPlan | null;
  dashboardMetrics: DashboardMetrics | null;
  loading: boolean;
  error: string | null;
}

const initialState: ProjectState = {
  list: [],
  currentProject: null,
  requirements: [],
  teamMembers: [],
  aiLogs: [],
  sprintPlan: null,
  dashboardMetrics: null,
  loading: false,
  error: null,
};

const projectSlice = createSlice({
  name: 'projects',
  initialState,
  reducers: {
    setProjects(state, action: PayloadAction<Project[]>) {
      state.list = action.payload;
      state.loading = false;
      state.error = null;
    },
    setCurrentProject(state, action: PayloadAction<Project>) {
      state.currentProject = action.payload;
    },
    setRequirements(state, action: PayloadAction<Requirement[]>) {
      state.requirements = action.payload;
    },
    setTeamMembers(state, action: PayloadAction<TeamMember[]>) {
      state.teamMembers = action.payload;
    },
    setAiLogs(state, action: PayloadAction<AgentLog[]>) {
      state.aiLogs = action.payload;
    },
    setSprintPlan(state, action: PayloadAction<SprintPlan>) {
      state.sprintPlan = action.payload;
    },
    setDashboardMetrics(state, action: PayloadAction<DashboardMetrics>) {
      state.dashboardMetrics = action.payload;
    },
    setProjectLoading(state, action: PayloadAction<boolean>) {
      state.loading = action.payload;
    },
    setProjectError(state, action: PayloadAction<string | null>) {
      state.error = action.payload;
      state.loading = false;
    },
    clearActiveProject(state) {
      state.currentProject = null;
      state.requirements = [];
      state.teamMembers = [];
      state.aiLogs = [];
      state.sprintPlan = null;
      state.dashboardMetrics = null;
    },
  },
});

export const {
  setProjects,
  setCurrentProject,
  setRequirements,
  setTeamMembers,
  setAiLogs,
  setSprintPlan,
  setDashboardMetrics,
  setProjectLoading,
  setProjectError,
  clearActiveProject,
} = projectSlice.actions;

export default projectSlice.reducer;
