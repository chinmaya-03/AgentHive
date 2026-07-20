import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Authentication Pages
import Login from '../pages/auth/Login';
import Register from '../pages/auth/Register';

// Layout & Security Wrappers
import ProtectedRoute from '../components/ProtectedRoute';
import Layout from '../layouts/Layout';

// Features Pages
import ProjectList from '../pages/projects/ProjectList';
import CreateProject from '../pages/projects/CreateProject';
import ProjectDetails from '../pages/projects/ProjectDetails';
import TeamPanel from '../pages/team/TeamPanel';
import ControlCenter from '../pages/ai-center/ControlCenter';
import Dashboard from '../pages/dashboard/Dashboard';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Private Routes (without sidebar layout) */}
      <Route 
        path="/projects" 
        element={
          <ProtectedRoute>
            <ProjectList />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/projects/new" 
        element={
          <ProtectedRoute>
            <CreateProject />
          </ProtectedRoute>
        } 
      />

      {/* Private Routes (with sidebar/navbar workspace layout) */}
      <Route 
        path="/projects/:projectId" 
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* Dashboard (Sprint Planner board & Analytics charts) */}
        <Route index element={<Dashboard />} />
        
        {/* Requirement Document Upload Repository */}
        <Route path="srs" element={<ProjectDetails />} />
        
        {/* Team Members list & Skills declaration */}
        <Route path="team" element={<TeamPanel />} />
        
        {/* CrewAI Orchestrator workflow terminal visualizer */}
        <Route path="ai-center" element={<ControlCenter />} />
      </Route>

      {/* Catch-all Redirect */}
      <Route path="*" element={<Navigate to="/projects" replace />} />
    </Routes>
  );
};

export default AppRoutes;
