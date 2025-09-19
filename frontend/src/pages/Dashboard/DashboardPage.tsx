import React from 'react';
import { Grid, Card, CardContent, Typography, Box, Chip, LinearProgress } from '@mui/material';
import { TrendingUp, Ticket, People, School, CheckCircle, Schedule, Warning } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

const StatCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  trend?: string;
}> = ({ title, value, icon, color, trend }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3 }}
  >
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              p: 1,
              borderRadius: 2,
              backgroundColor: `${color}.light`,
              color: `${color}.main`,
              mr: 2,
            }}
          >
            {icon}
          </Box>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          {value}
        </Typography>
        {trend && (
          <Chip
            label={trend}
            size="small"
            color="success"
            sx={{ fontSize: '0.75rem' }}
          />
        )}
      </CardContent>
    </Card>
  </motion.div>
);

export const DashboardPage: React.FC = () => {
  const { t } = useTranslation();

  const stats = [
    {
      title: t('dashboard.totalTickets'),
      value: '1,234',
      icon: <Ticket />,
      color: 'primary',
      trend: '+12%',
    },
    {
      title: t('dashboard.openTickets'),
      value: '89',
      icon: <Schedule />,
      color: 'warning',
      trend: '-5%',
    },
    {
      title: t('dashboard.closedTickets'),
      value: '1,145',
      icon: <CheckCircle />,
      color: 'success',
      trend: '+8%',
    },
    {
      title: t('dashboard.satisfactionRate'),
      value: '94%',
      icon: <TrendingUp />,
      color: 'info',
      trend: '+2%',
    },
  ];

  const recentTickets = [
    { id: '#1234', title: 'Проблема с доступом к системе', status: 'В работе', priority: 'Высокий' },
    { id: '#1235', title: 'Запрос на добавление пользователя', status: 'Новый', priority: 'Средний' },
    { id: '#1236', title: 'Ошибка в отчете', status: 'Решен', priority: 'Низкий' },
  ];

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
          {t('dashboard.title')}
        </Typography>
        <Typography variant="body1" sx={{ mb: 4, color: 'text.secondary' }}>
          {t('dashboard.welcome')}
        </Typography>
      </motion.div>

      {/* Статистика */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <StatCard {...stat} />
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Последние тикеты */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                  {t('dashboard.recentTickets')}
                </Typography>
                {recentTickets.map((ticket, index) => (
                  <motion.div
                    key={ticket.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <Box
                      sx={{
                        p: 2,
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 2,
                        mb: 2,
                        '&:hover': {
                          backgroundColor: 'action.hover',
                        },
                      }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {ticket.id}
                        </Typography>
                        <Chip
                          label={ticket.priority}
                          size="small"
                          color={ticket.priority === 'Высокий' ? 'error' : ticket.priority === 'Средний' ? 'warning' : 'default'}
                        />
                      </Box>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        {ticket.title}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Chip
                          label={ticket.status}
                          size="small"
                          color={ticket.status === 'Решен' ? 'success' : ticket.status === 'В работе' ? 'primary' : 'default'}
                        />
                        <Typography variant="caption" color="text.secondary">
                          2 часа назад
                        </Typography>
                      </Box>
                    </Box>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Быстрые действия */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                  {t('dashboard.quickActions')}
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card
                      sx={{
                        p: 2,
                        cursor: 'pointer',
                        border: 1,
                        borderColor: 'primary.main',
                        '&:hover': {
                          backgroundColor: 'primary.light',
                          color: 'primary.contrastText',
                        },
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Ticket sx={{ mr: 2 }} />
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          {t('dashboard.createTicket')}
                        </Typography>
                      </Box>
                    </Card>
                  </motion.div>

                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card
                      sx={{
                        p: 2,
                        cursor: 'pointer',
                        border: 1,
                        borderColor: 'secondary.main',
                        '&:hover': {
                          backgroundColor: 'secondary.light',
                          color: 'secondary.contrastText',
                        },
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <School sx={{ mr: 2 }} />
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          {t('dashboard.searchKnowledge')}
                        </Typography>
                      </Box>
                    </Card>
                  </motion.div>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};
