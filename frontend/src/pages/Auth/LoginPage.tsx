import React from 'react';
import { Box, Card, CardContent, Typography, TextField, Button, Container } from '@mui/material';
import { Login as LoginIcon } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

const LoginPage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card sx={{ width: '100%', maxWidth: 400 }}>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ textAlign: 'center', mb: 4 }}>
                <LoginIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
                  {t('auth.login')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Войдите в систему WorkerNet Portal
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <TextField
                  label={t('auth.username')}
                  variant="outlined"
                  fullWidth
                />
                <TextField
                  label={t('auth.password')}
                  type="password"
                  variant="outlined"
                  fullWidth
                />
                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  sx={{ py: 1.5 }}
                >
                  {t('auth.loginButton')}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      </Box>
    </Container>
  );
};

export default LoginPage;
