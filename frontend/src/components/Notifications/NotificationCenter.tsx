import React, { useState } from 'react';
import {
  Drawer,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Badge,
  IconButton,
  Chip,
  Divider,
  Button,
  Tooltip,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Close as CloseIcon,
  MarkEmailRead as MarkReadIcon,
  Delete as DeleteIcon,
  MoreVert as MoreIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { formatDistanceToNow } from 'date-fns';
import { ru } from 'date-fns/locale';

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: Date;
  read: boolean;
  avatar?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface NotificationCenterProps {
  open: boolean;
  onClose: () => void;
  notifications?: Notification[];
  onMarkAsRead?: (id: string) => void;
  onDelete?: (id: string) => void;
  onMarkAllAsRead?: () => void;
  onClearAll?: () => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({
  open,
  onClose,
  notifications = [],
  onMarkAsRead,
  onDelete,
  onMarkAllAsRead,
  onClearAll,
}) => {
  const { t } = useTranslation();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const unreadCount = notifications.filter(n => !n.read).length;

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return '✅';
      case 'warning':
        return '⚠️';
      case 'error':
        return '❌';
      default:
        return 'ℹ️';
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'primary';
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <>
      <Drawer
        anchor="right"
        open={open}
        onClose={onClose}
        sx={{
          '& .MuiDrawer-paper': {
            width: 400,
            maxWidth: '90vw',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          {/* Заголовок */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Badge badgeContent={unreadCount} color="error">
                <NotificationsIcon />
              </Badge>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Уведомления
              </Typography>
            </Box>
            <Box>
              <IconButton onClick={handleMenuOpen} size="small">
                <MoreIcon />
              </IconButton>
              <IconButton onClick={onClose} size="small">
                <CloseIcon />
              </IconButton>
            </Box>
          </Box>

          {/* Меню действий */}
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={() => { onMarkAllAsRead?.(); handleMenuClose(); }}>
              <MarkReadIcon sx={{ mr: 1 }} />
              Отметить все как прочитанные
            </MenuItem>
            <MenuItem onClick={() => { onClearAll?.(); handleMenuClose(); }}>
              <DeleteIcon sx={{ mr: 1 }} />
              Очистить все
            </MenuItem>
          </Menu>

          <Divider sx={{ mb: 2 }} />

          {/* Список уведомлений */}
          {notifications.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <NotificationsIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                Нет уведомлений
              </Typography>
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              <AnimatePresence>
                {notifications.map((notification, index) => (
                  <motion.div
                    key={notification.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                  >
                    <ListItem
                      sx={{
                        p: 2,
                        mb: 1,
                        borderRadius: 2,
                        backgroundColor: notification.read ? 'transparent' : 'action.hover',
                        border: 1,
                        borderColor: 'divider',
                        '&:hover': {
                          backgroundColor: 'action.selected',
                        },
                      }}
                    >
                      <ListItemAvatar>
                        <Avatar
                          sx={{
                            backgroundColor: `${getNotificationColor(notification.type)}.light`,
                            color: `${getNotificationColor(notification.type)}.main`,
                          }}
                        >
                          {getNotificationIcon(notification.type)}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                            <Typography
                              variant="subtitle2"
                              sx={{
                                fontWeight: notification.read ? 400 : 600,
                                color: notification.read ? 'text.secondary' : 'text.primary',
                              }}
                            >
                              {notification.title}
                            </Typography>
                            <Chip
                              label={formatDistanceToNow(notification.timestamp, { 
                                addSuffix: true, 
                                locale: ru 
                              })}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.75rem' }}
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography
                              variant="body2"
                              sx={{
                                color: notification.read ? 'text.secondary' : 'text.primary',
                                mb: 1,
                              }}
                            >
                              {notification.message}
                            </Typography>
                            {notification.action && (
                              <Button
                                size="small"
                                variant="outlined"
                                onClick={notification.action.onClick}
                                sx={{ mr: 1 }}
                              >
                                {notification.action.label}
                              </Button>
                            )}
                            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                              {!notification.read && (
                                <Button
                                  size="small"
                                  startIcon={<MarkReadIcon />}
                                  onClick={() => onMarkAsRead?.(notification.id)}
                                >
                                  Прочитано
                                </Button>
                              )}
                              <Button
                                size="small"
                                color="error"
                                startIcon={<DeleteIcon />}
                                onClick={() => onDelete?.(notification.id)}
                              >
                                Удалить
                              </Button>
                            </Box>
                          </Box>
                        }
                      />
                    </ListItem>
                  </motion.div>
                ))}
              </AnimatePresence>
            </List>
          )}
        </Box>
      </Drawer>
    </>
  );
};
