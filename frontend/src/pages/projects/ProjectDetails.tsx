import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../redux';
import { setRequirements } from '../../redux/projectSlice';
import { projectsApi, extractErrorMessage } from '../../api/api';
import { 
  FileText, 
  Upload, 
  Trash2, 
  ChevronDown, 
  ChevronUp, 
  ArrowRight,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  FileCode2,
  Zap
} from 'lucide-react';

const SAMPLE_SRS_CONTENT = `SOFTWARE REQUIREMENT SPECIFICATION (SRS)
PROJECT: E-Commerce Microservices AI Platform

1. SYSTEM OVERVIEW & SCOPE
The E-Commerce Microservices AI Platform is a high-availability online retail ecosystem.
The platform requires user authentication, microservices architecture, automated inventory webhooks, Stripe payment integration, real-time stock management, and AI-driven personalized product recommendations.

2. CORE MODULES & FUNCTIONAL REQUIREMENTS

MODULE 1: USER AUTHENTICATION & PROFILE MANAGEMENT
- FR-1.1: Implement JWT multi-factor authentication for customer registration, login, and password resets.
- FR-1.2: Support RBAC (Role-Based Access Control) for Customers, Store Managers, and System Administrators.
- FR-1.3: Store encrypted user passwords using bcrypt with salt rounds >= 12.

MODULE 2: PRODUCT CATALOG & SEARCH ENGINE
- FR-2.1: Provide REST API endpoints to CRUD products, categories, tags, and variants.
- FR-2.2: Integrate PostgreSQL full-text search and Elasticsearch index for sub-50ms product query latency.
- FR-2.3: Support bulk product updates via CSV upload.

MODULE 3: SHOPPING CART & CHECKOUT PIPELINE
- FR-3.1: Maintain real-time customer shopping session cart state stored in Redis.
- FR-3.2: Integrate Stripe API for secure credit card processing, digital wallets (Apple Pay/Google Pay), and refund processing.
- FR-3.3: Calculate order subtotal, sales tax dynamically based on shipping ZIP code, and shipping rates.

MODULE 4: INVENTORY & ORDER FULFILLMENT WEBHOOKS
- FR-4.1: Broadcast inventory reservation events to RabbitMQ queues upon cart checkout.
- FR-4.2: Implement webhook handlers for warehouse inventory updates and automated stock re-ordering triggers.
- FR-4.3: Generate automated email and SMS delivery tracking updates to customers upon dispatch.

MODULE 5: AI RECOMMENDATION ENGINE & TELEMETRY
- FR-5.1: Collect real-time user browsing telemetry events and process them using a streaming data pipeline.
- FR-5.2: Serve personalized product recommendations on product detail pages and checkout screens.
`;

const formatDate = (dateStr?: string) => {
  if (!dateStr) return 'N/A';
  const date = new Date(dateStr);
  return isNaN(date.getTime()) ? 'N/A' : date.toLocaleDateString();
};

const ProjectDetails: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const dispatch = useAppDispatch();
  
  const { currentProject, requirements } = useAppSelector((state) => state.projects);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  
  const [expandedReqId, setExpandedReqId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchRequirements = () => {
    if (!projectId) return;
    projectsApi.listRequirements(projectId)
      .then((res) => {
        dispatch(setRequirements(res.data));
      })
      .catch((err) => {
        console.error('Failed to load requirements', err);
      });
  };

  useEffect(() => {
    fetchRequirements();
  }, [projectId]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0 || !projectId) return;

    const file = files[0];
    await processUpload(file);
    e.target.value = '';
  };

  const processUpload = async (file: File) => {
    if (!projectId) return;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);

    setUploading(true);
    setUploadError(null);
    try {
      await projectsApi.uploadRequirement(projectId, formData);
      fetchRequirements();
    } catch (err: any) {
      const msg = extractErrorMessage(err, 'Failed to upload and parse requirements.');
      setUploadError(msg);
    } finally {
      setUploading(false);
    }
  };

  const handleLoadSample = async () => {
    const blob = new Blob([SAMPLE_SRS_CONTENT], { type: 'text/plain' });
    const sampleFile = new File([blob], 'sample_ecommerce_srs.txt', { type: 'text/plain' });
    await processUpload(sampleFile);
  };

  const handleReqDelete = async (reqId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!projectId || !confirm('Are you sure you want to delete this requirement document?')) return;
    
    setDeletingId(reqId);
    try {
      await projectsApi.deleteRequirement(projectId, reqId);
      fetchRequirements();
      if (expandedReqId === reqId) setExpandedReqId(null);
    } catch (err: any) {
      alert(extractErrorMessage(err, 'Failed to delete requirement.'));
    } finally {
      setDeletingId(null);
    }
  };

  const toggleExpand = (reqId: string) => {
    setExpandedReqId(expandedReqId === reqId ? null : reqId);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-10">
      {/* Project Header */}
      {currentProject && (
        <div className="relative overflow-hidden rounded-2xl border border-slate-900 bg-slate-900/30 p-6 md:p-8 shadow-xl backdrop-blur-xl">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-20" />
          <div className="relative z-10">
            <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">Software Workspace Workspace</span>
            <h1 className="text-3xl font-extrabold text-white mt-1.5 tracking-tight">{currentProject.name}</h1>
            <p className="mt-2 text-xs text-slate-400 leading-relaxed max-w-3xl font-medium">
              {currentProject.description || 'No detailed system description provided.'}
            </p>
          </div>
        </div>
      )}

      {/* Two Column Grid */}
      <div className="grid gap-8 md:grid-cols-3">
        {/* Left Column - Upload Section */}
        <div className="md:col-span-1 space-y-6">
          <div className="card-glass p-6 space-y-5 sticky top-6 border border-slate-800 shadow-xl">
            <div>
              <h3 className="text-xs font-black uppercase tracking-wider text-white flex items-center gap-2">
                <Upload size={14} className="text-indigo-400" />
                <span>Upload SRS Document</span>
              </h3>
              <p className="text-[11px] text-slate-400 leading-relaxed font-medium mt-1">
                Upload your Software Requirement Specification (SRS) notes. Supports PDF, DOCX, or plain TXT files.
              </p>
            </div>

            {uploadError && (
              <div className="rounded-xl bg-red-955 p-3 text-[10px] text-red-200 border border-red-800/60 flex items-start gap-2 animate-pulse">
                <AlertCircle size={14} className="shrink-0 mt-0.5 text-red-400" />
                <span>{uploadError}</span>
              </div>
            )}

            {/* Quick Sample Load Button */}
            <button
              onClick={handleLoadSample}
              disabled={uploading}
              className="btn-emerald w-full text-xs cursor-pointer font-bold"
              title="Instantly upload a pre-written SRS document"
            >
              {uploading ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              ) : (
                <Zap size={14} />
              )}
              <span>Load Sample SRS Spec</span>
            </button>

            <div className="flex items-center gap-2 my-2 text-[9px] uppercase font-black text-slate-550 justify-center">
              <span className="h-px bg-slate-900 flex-1"></span>
              <span>OR UPLOAD CUSTOM FILE</span>
              <span className="h-px bg-slate-900 flex-1"></span>
            </div>

            {/* Upload Dropzone */}
            <label className={`flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-6 cursor-pointer transition-all duration-300 ${
              uploading 
                ? 'border-indigo-500 bg-indigo-500/10' 
                : 'border-slate-850 hover:border-indigo-500/60 hover:bg-slate-900/40'
            }`}>
              {uploading ? (
                <div className="flex flex-col items-center justify-center text-center">
                  <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-400 border-t-transparent mb-3" />
                  <span className="text-xs font-semibold text-indigo-400">Extracting Document Text...</span>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center text-center">
                  <div className="h-9 w-9 rounded-xl bg-slate-900 border border-slate-850 flex items-center justify-center text-indigo-400 mb-3 shadow-inner">
                    <Upload size={16} />
                  </div>
                  <span className="text-xs font-bold text-slate-200">Select File to Upload</span>
                  <span className="text-[10px] text-slate-500 mt-1 font-bold">PDF, DOCX, TXT</span>
                </div>
              )}
              <input
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
              />
            </label>

            {/* Navigation Shortcuts */}
            <div className="border-t border-slate-900 pt-4 flex flex-col gap-2.5">
              <Link
                to={`/projects/${projectId}/team`}
                className="btn-secondary w-full"
              >
                <span>Setup Team Configuration</span>
                <ArrowRight size={14} />
              </Link>
              <Link
                to={`/projects/${projectId}/ai-center`}
                className="btn-primary w-full"
              >
                <Sparkles size={14} />
                <span>Kickoff AI Orchestrator</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Right Column - Requirements Repository */}
        <div className="md:col-span-2 space-y-6">
          <div className="card-glass p-6 space-y-6 border border-slate-800 shadow-xl">
            <h3 className="text-xs font-black uppercase tracking-wider text-white flex items-center gap-2">
              <FileText size={14} className="text-indigo-400" />
              <span>Requirements Documents Repository</span>
            </h3>

            {requirements.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center space-y-4">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-900 border border-slate-850 text-slate-500 shadow-inner">
                  <FileCode2 size={24} />
                </div>
                <div>
                  <h4 className="text-xs font-black uppercase tracking-wider text-slate-300">No requirements documents uploaded</h4>
                  <p className="text-[11px] text-slate-500 max-w-xs mt-1.5 leading-relaxed font-semibold">
                    Get started by loading our demo e-commerce Microservices spec, or select your own document using the dropzone.
                  </p>
                </div>
                <button
                  onClick={handleLoadSample}
                  disabled={uploading}
                  className="btn-emerald text-xs mt-2"
                >
                  <Zap size={14} />
                  <span>⚡ Load Demo SRS Document Now</span>
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {requirements.map((req) => (
                  <div 
                    key={req.id} 
                    className="border border-slate-900 rounded-xl overflow-hidden bg-slate-950/40 hover:border-slate-850 transition-all duration-300"
                  >
                    {/* Header */}
                    <div 
                      onClick={() => toggleExpand(req.id)}
                      className="flex items-center justify-between p-4 cursor-pointer select-none"
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                          <FileText size={16} />
                        </div>
                        <div>
                          <span className="text-xs font-extrabold text-white block line-clamp-1">
                            {req.filename || req.original_filename || 'Requirement Document'}
                          </span>
                          <span className="text-[9px] text-slate-500 uppercase tracking-widest block mt-0.5">
                            {req.file_type || (req.file_extension ? req.file_extension.replace('.', '').toUpperCase() : 'TXT')} • uploaded {formatDate(req.created_at || req.upload_timestamp)}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        {req.status === 'Processed' ? (
                          <span className="flex items-center gap-1 rounded bg-emerald-500/10 px-2 py-0.5 text-[9px] font-black uppercase tracking-wider text-emerald-400 border border-emerald-500/20">
                            <CheckCircle2 size={11} />
                            Processed
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 rounded bg-amber-500/10 px-2 py-0.5 text-[9px] font-black uppercase tracking-wider text-amber-400 border border-amber-500/20">
                            Pending
                          </span>
                        )}

                        <div className="flex items-center gap-1.5">
                          <button
                            disabled={deletingId === req.id}
                            onClick={(e) => handleReqDelete(req.id, e)}
                            className="rounded-lg p-1.5 text-slate-500 hover:bg-rose-500/20 hover:text-rose-400 transition-all duration-150 cursor-pointer"
                            title="Delete Document"
                          >
                            {deletingId === req.id ? (
                              <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-400 border-t-transparent" />
                            ) : (
                              <Trash2 size={14} />
                            )}
                          </button>

                          <div className="text-slate-500">
                            {expandedReqId === req.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Extracted Text */}
                    {expandedReqId === req.id && (
                      <div className="border-t border-slate-900 p-4 bg-slate-950 text-slate-300">
                        <span className="font-mono text-[9px] uppercase tracking-widest text-slate-500 mb-2.5 block border-b border-slate-900 pb-1.5 font-bold">Extracted Text Content</span>
                        <pre className="font-mono text-xs overflow-x-auto whitespace-pre-wrap max-h-96 leading-relaxed text-indigo-200/90 select-text pr-2">
                          {req.extracted_text || 'No text extracted from document.'}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectDetails;
