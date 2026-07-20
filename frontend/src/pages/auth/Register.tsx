import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAppDispatch } from '../../redux';
import { setCredentials, setAuthError } from '../../redux/authSlice';
import { authApi, extractErrorMessage } from '../../api/api';
import { AlertCircle, User, Mail, Lock, ShieldCheck, ArrowRight } from 'lucide-react';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      name: '',
      email: '',
      password: '',
      role: 'pm',
    }
  });

  const onSubmit = async (data: any) => {
    setLoading(true);
    setErrorMessage(null);
    try {
      // 1. Create User profile
      await authApi.register(data);

      // 2. Perform login and retrieve token
      const loginRes = await authApi.login({ email: data.email, password: data.password });
      const token = loginRes.data.access_token;
      localStorage.setItem('token', token);

      // 3. Retrieve user profile
      const profileRes = await authApi.me();
      const user = profileRes.data;

      // 4. Dispatch to store
      dispatch(setCredentials({ token, user }));
      navigate('/projects');
    } catch (err: any) {
      const msg = extractErrorMessage(
        err,
        'Registration failed. Please verify the backend server is running and try again.'
      );
      setErrorMessage(msg);
      dispatch(setAuthError(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        {/* Header Branding */}
        <div className="flex flex-col items-center text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-sm">
            <ShieldCheck size={28} />
          </div>
          <h2 className="mt-5 font-sans text-3xl font-bold tracking-tight text-white">
            Create your account
          </h2>
          <p className="mt-2 text-sm text-slate-400 max-w-sm">
            Sprint Board & Automation Suite
          </p>
        </div>

        {/* Form Card */}
        <div className="card-glass p-8 border border-slate-800 shadow-2xl">
          {errorMessage && (
            <div className="mb-6 flex items-start gap-3 rounded-xl bg-red-950/80 p-4 text-sm text-red-200 border border-red-800/60 shadow-inner">
              <AlertCircle size={18} className="shrink-0 mt-0.5 text-red-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
            {/* Full Name */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <User size={16} className="absolute left-3.5 top-3.5 text-slate-500" />
                <input
                  type="text"
                  {...register('name', { required: 'Full name is required' })}
                  placeholder="Alex Rivers"
                  className={`block w-full h-11 rounded-xl border bg-slate-900/80 pl-10 pr-4 text-sm text-white placeholder-slate-500 outline-none transition-all-custom ${
                    errors.name
                      ? 'border-red-500 focus:ring-2 focus:ring-red-500/40'
                      : 'border-slate-800 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30'
                  }`}
                />
              </div>
              {errors.name && (
                <span className="mt-1 block text-xs font-medium text-red-400">{errors.name.message}</span>
              )}
            </div>

            {/* Email Field */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-3.5 text-slate-500" />
                <input
                  type="email"
                  {...register('email', {
                    required: 'Email address is required',
                    pattern: { value: /^\S+@\S+$/i, message: 'Invalid email address' }
                  })}
                  placeholder="alex@company.com"
                  className={`block w-full h-11 rounded-xl border bg-slate-900/80 pl-10 pr-4 text-sm text-white placeholder-slate-500 outline-none transition-all-custom ${
                    errors.email
                      ? 'border-red-500 focus:ring-2 focus:ring-red-500/40'
                      : 'border-slate-800 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30'
                  }`}
                />
              </div>
              {errors.email && (
                <span className="mt-1 block text-xs font-medium text-red-400">{errors.email.message}</span>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-3.5 text-slate-500" />
                <input
                  type="password"
                  {...register('password', {
                    required: 'Password is required',
                    minLength: { value: 6, message: 'Password must be at least 6 characters long' }
                  })}
                  placeholder="••••••••"
                  className={`block w-full h-11 rounded-xl border bg-slate-900/80 pl-10 pr-4 text-sm text-white placeholder-slate-500 outline-none transition-all-custom ${
                    errors.password
                      ? 'border-red-500 focus:ring-2 focus:ring-red-500/40'
                      : 'border-slate-800 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30'
                  }`}
                />
              </div>
              {errors.password && (
                <span className="mt-1 block text-xs font-medium text-red-400">{errors.password.message}</span>
              )}
            </div>

            {/* Role Selection */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                Your Primary Role
              </label>
              <div className="relative">
                <ShieldCheck size={16} className="absolute left-3.5 top-3.5 text-slate-500" />
                <select
                  {...register('role')}
                  className="block w-full h-11 rounded-xl border border-slate-800 bg-slate-900/80 pl-10 pr-4 text-sm text-white outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30 transition-all-custom"
                >
                  <option value="pm">Product Manager / Scrum Master</option>
                  <option value="lead">Engineering Tech Lead</option>
                  <option value="developer">Senior Developer</option>
                  <option value="qa">QA / Risk Auditor</option>
                </select>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="mt-6 flex w-full h-12 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 font-sans text-base font-bold text-white shadow-lg shadow-indigo-600/30 hover:from-blue-500 hover:via-indigo-500 hover:to-violet-500 focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:opacity-50 transition-all-custom cursor-pointer"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  <span>Creating Account...</span>
                </div>
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          {/* Login Redirect link */}
          <div className="mt-6 border-t border-slate-800/80 pt-6 text-center text-sm">
            <span className="text-slate-400">Already have an account? </span>
            <Link to="/login" className="font-semibold text-indigo-400 hover:text-indigo-300 transition-all-custom">
              Sign in here
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
