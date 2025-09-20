import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, IconButton, Badge, Avatar, Menu, MenuItem, useTheme, useMediaQuery } from '@mui/material';
import { Menu as MenuIcon, Notifications, Settings, AccountCircle, GetApp, Search } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

import { Sidebar } from './Sidebar';
import { InstallButton } from '@components/PWA/InstallButton';
import { usePWA } from '@components/PWA/PWAProvider';
import { ThemeToggle } from '@components/Theme/ThemeToggle';
import { SearchBar } from '@components/Search/SearchBar';
import { NotificationCenter } from '@components/Notifications/NotificationCenter';

const Layout: React.FC = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { canInstall } = usePWA();
  
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Боковая панель */}
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      {/* Основной контент */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Верхняя панель */}
        <AppBar 
          position="sticky" 
          elevation={1}
          sx={{ 
            backgroundColor: 'background.paper',
            color: 'text.primary',
            borderBottom: 1,
            borderColor: 'divider'
          }}
        >
          <Toolbar>
            <IconButton
              edge="start"
              color="inherit"
              onClick={toggleSidebar}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            
            <Typography 
              variant="h6" 
              component="div" 
              sx={{ flexGrow: 1, fontWeight: 600 }}
            >
              WorkerNet Portal
            </Typography>

            {/* Поиск */}
            <Box sx={{ flexGrow: 1, maxWidth: 400, mx: 2 }}>
              <SearchBar
                placeholder="Поиск тикетов, пользователей, статей..."
                onSearch={setSearchQuery}
                showSuggestions={true}
              />
            </Box>

            {/* Переключатель темы */}
            <ThemeToggle variant="icon" />

            {/* Кнопка установки PWA */}
            {canInstall && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <InstallButton variant="icon" />
              </motion.div>
            )}

            {/* Уведомления */}
            <IconButton 
              color="inherit" 
              sx={{ mr: 1 }}
              onClick={() => setNotificationOpen(true)}
            >
              <Badge badgeContent={4} color="error">
                <Notifications />
              </Badge>
            </IconButton>

            {/* Настройки */}
            <IconButton color="inherit" sx={{ mr: 1 }}>
              <Settings />
            </IconButton>

            {/* Профиль пользователя */}
            <IconButton
              onClick={handleMenuOpen}
              color="inherit"
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                <AccountCircle />
              </Avatar>
            </IconButton>

            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
            >
              <MenuItem onClick={handleMenuClose}>
                <AccountCircle sx={{ mr: 1 }} />
                {t('navigation.profile')}
              </MenuItem>
              <MenuItem onClick={handleMenuClose}>
                <Settings sx={{ mr: 1 }} />
                {t('navigation.settings')}
              </MenuItem>
              <MenuItem onClick={handleMenuClose}>
                {t('navigation.logout')}
              </MenuItem>
            </Menu>
          </Toolbar>
        </AppBar>

        {/* Основной контент страницы */}
        <Box 
          component="main" 
          sx={{ 
            flexGrow: 1, 
            p: 3,
            backgroundColor: 'background.default',
            minHeight: 'calc(100vh - 64px)'
          }}
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Outlet />
          </motion.div>
        </Box>
      </Box>

      {/* Центр уведомлений */}
      <NotificationCenter
        open={notificationOpen}
        onClose={() => setNotificationOpen(false)}
        notifications={[
          {
            id: '1',
            title: 'Новый тикет #1234',
            message: 'Создан новый тикет "Проблема с доступом"',
            type: 'info',
            timestamp: new Date(),
            read: false,
          },
          {
            id: '2',
            title: 'Тикет #1233 решен',
            message: 'Тикет "Ошибка в отчете" был успешно решен',
            type: 'success',
            timestamp: new Date(Date.now() - 1000 * 60 * 30),
            read: false,
          },
          {
            id: '3',
            title: 'Эскалация тикета #1232',
            message: 'Тикет "Критическая ошибка" требует внимания',
            type: 'error',
            timestamp: new Date(Date.now() - 1000 * 60 * 60),
            read: true,
          },
        ]}
        onMarkAsRead={(id) => console.log('Mark as read:', id)}
        onDelete={(id) => console.log('Delete:', id)}
        onMarkAllAsRead={() => console.log('Mark all as read')}
        onClearAll={() => console.log('Clear all')}
      />
    </Box>
  );
};

export default Layout;
