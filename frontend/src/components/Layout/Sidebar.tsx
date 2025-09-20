import React from 'react';
import { Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Divider, Box, Typography, useTheme, useMediaQuery } from '@mui/material';
import { Dashboard, SupportAgent, School, People, Settings, Support } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const menuItems = [
  { path: '/dashboard', icon: Dashboard, label: 'navigation.dashboard' },
  { path: '/tickets', icon: SupportAgent, label: 'navigation.tickets' },
  { path: '/knowledge', icon: School, label: 'navigation.knowledge' },
  { path: '/users', icon: People, label: 'navigation.users' },
  { path: '/settings', icon: Settings, label: 'navigation.settings' },
];

export const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Заголовок */}
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Support 
            sx={{ 
              fontSize: 40, 
              color: 'primary.main',
              mb: 1 
            }} 
          />
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 600,
              color: 'text.primary'
            }}
          >
            WorkerNet
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              color: 'text.secondary',
              fontSize: '0.75rem'
            }}
          >
            Система поддержки
          </Typography>
        </motion.div>
      </Box>

      <Divider />

      {/* Навигационное меню */}
      <List sx={{ flexGrow: 1, pt: 2 }}>
        {menuItems.map((item, index) => {
          const isActive = location.pathname === item.path;
          const IconComponent = item.icon;

          return (
            <motion.div
              key={item.path}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <ListItem disablePadding sx={{ px: 2, mb: 0.5 }}>
                <ListItemButton
                  onClick={() => handleNavigation(item.path)}
                  selected={isActive}
                  sx={{
                    borderRadius: 2,
                    mb: 0.5,
                    '&.Mui-selected': {
                      backgroundColor: 'primary.main',
                      color: 'primary.contrastText',
                      '&:hover': {
                        backgroundColor: 'primary.dark',
                      },
                      '& .MuiListItemIcon-root': {
                        color: 'primary.contrastText',
                      },
                    },
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                >
                  <ListItemIcon>
                    <IconComponent />
                  </ListItemIcon>
                  <ListItemText 
                    primary={t(item.label)}
                    primaryTypographyProps={{
                      fontSize: '0.875rem',
                      fontWeight: isActive ? 600 : 400,
                    }}
                  />
                </ListItemButton>
              </ListItem>
            </motion.div>
          );
        })}
      </List>

      <Divider />

      {/* Информация о версии */}
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography 
          variant="caption" 
          sx={{ 
            color: 'text.secondary',
            fontSize: '0.75rem'
          }}
        >
          v1.0.0
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'persistent'}
      open={open}
      onClose={onClose}
      sx={{
        width: 280,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 280,
          boxSizing: 'border-box',
          backgroundColor: 'background.paper',
          borderRight: 1,
          borderColor: 'divider',
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};
