import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { motion } from 'framer-motion';
import { PWAProvider } from '@components/PWA/PWAProvider';
import { OfflineIndicator } from '@components/PWA/OfflineIndicator';
import { ThemeProvider } from '@contexts/ThemeContext';

// Lazy loading компонентов для оптимизации
const Layout = React.lazy(() => import('@components/Layout/Layout'));
const LoginPage = React.lazy(() => import('@pages/Auth/LoginPage'));
const DashboardPage = React.lazy(() => import('@pages/Dashboard/DashboardPage'));
const TicketsPage = React.lazy(() => import('@pages/Tickets/TicketsPage'));
const TicketDetailPage = React.lazy(() => import('@pages/Tickets/TicketDetailPage'));
const KnowledgeBasePage = React.lazy(() => import('@pages/Knowledge/KnowledgeBasePage'));
const UsersPage = React.lazy(() => import('@pages/Users/UsersPage'));
const SettingsPage = React.lazy(() => import('@pages/Settings/SettingsPage'));
const NotFoundPage = React.lazy(() => import('@pages/NotFound/NotFoundPage'));

// Компонент загрузки
const LoadingSpinner = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="100vh"
    flexDirection="column"
    gap={2}
  >
    <CircularProgress size={60} />
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
    >
      Загрузка...
    </motion.div>
  </Box>
);

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <PWAProvider>
        <OfflineIndicator />
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            {/* Публичные маршруты */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Защищенные маршруты */}
            <Route path="/" element={<Layout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="tickets" element={<TicketsPage />} />
              <Route path="tickets/:id" element={<TicketDetailPage />} />
              <Route path="knowledge" element={<KnowledgeBasePage />} />
              <Route path="users" element={<UsersPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
            
            {/* 404 страница */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Suspense>
      </PWAProvider>
    </ThemeProvider>
  );
};

export default App;
