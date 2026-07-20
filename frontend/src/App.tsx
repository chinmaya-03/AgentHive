import React, { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { useAppDispatch } from './redux';
import { setUser, logout, setAuthLoading } from './redux/authSlice';
import { authApi } from './api/api';
import AppRoutes from './routes/AppRoutes';
import ErrorBoundary from './components/ErrorBoundary';

const App: React.FC = () => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      dispatch(setAuthLoading(true));
      authApi.me()
        .then((res) => {
          dispatch(setUser(res.data));
        })
        .catch((err) => {
          console.error('Session expired or invalid token', err);
          dispatch(logout());
        })
        .finally(() => {
          dispatch(setAuthLoading(false));
        });
    }
  }, [dispatch]);

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </ErrorBoundary>
  );
};

export default App;
