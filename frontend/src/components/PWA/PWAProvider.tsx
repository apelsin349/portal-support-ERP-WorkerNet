import React, { createContext, useContext, useEffect, useState } from 'react';
import { Box, Snackbar, Alert, Button, Dialog, DialogTitle, DialogContent, DialogActions, Typography } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';

interface PWAContextType {
  isOnline: boolean;
  isInstalled: boolean;
  canInstall: boolean;
  installPrompt: any;
  installApp: () => void;
  updateAvailable: boolean;
  updateApp: () => void;
}

const PWAContext = createContext<PWAContextType | undefined>(undefined);

export const usePWA = () => {
  const context = useContext(PWAContext);
  if (!context) {
    throw new Error('usePWA must be used within a PWAProvider');
  }
  return context;
};

interface PWAProviderProps {
  children: React.ReactNode;
}

export const PWAProvider: React.FC<PWAProviderProps> = ({ children }) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isInstalled, setIsInstalled] = useState(false);
  const [canInstall, setCanInstall] = useState(false);
  const [installPrompt, setInstallPrompt] = useState<any>(null);
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [showInstallDialog, setShowInstallDialog] = useState(false);
  const [showUpdateDialog, setShowUpdateDialog] = useState(false);

  useEffect(() => {
    // Проверка онлайн статуса
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Проверка установки PWA
    const checkInstalled = () => {
      const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      const isInStandaloneMode = ('standalone' in window.navigator) && (window.navigator as any).standalone;
      
      setIsInstalled(isStandalone || (isIOS && isInStandaloneMode));
    };

    checkInstalled();

    // Обработка установки PWA
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e);
      setCanInstall(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // Обработка успешной установки
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setCanInstall(false);
      setInstallPrompt(null);
    };

    window.addEventListener('appinstalled', handleAppInstalled);

    // Регистрация Service Worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then((registration) => {
          console.log('Service Worker зарегистрирован:', registration);

          // Проверка обновлений
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  setUpdateAvailable(true);
                  setShowUpdateDialog(true);
                }
              });
            }
          });
        })
        .catch((error) => {
          console.error('Ошибка регистрации Service Worker:', error);
        });
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const installApp = async () => {
    if (installPrompt) {
      const result = await installPrompt.prompt();
      console.log('Результат установки:', result);
      setInstallPrompt(null);
      setCanInstall(false);
    }
  };

  const updateApp = () => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistration().then((registration) => {
        if (registration && registration.waiting) {
          registration.waiting.postMessage({ type: 'SKIP_WAITING' });
          window.location.reload();
        }
      });
    }
  };

  const contextValue: PWAContextType = {
    isOnline,
    isInstalled,
    canInstall,
    installPrompt,
    installApp,
    updateAvailable,
    updateApp,
  };

  return (
    <PWAContext.Provider value={contextValue}>
      {children}
      
      {/* Уведомление о статусе подключения */}
      <AnimatePresence>
        {!isOnline && (
          <motion.div
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -100, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Snackbar
              open={!isOnline}
              anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
            >
              <Alert severity="warning" variant="filled">
                Нет подключения к интернету. Работа в офлайн режиме.
              </Alert>
            </Snackbar>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Диалог установки PWA */}
      <Dialog open={showInstallDialog} onClose={() => setShowInstallDialog(false)}>
        <DialogTitle>
          Установить WorkerNet Portal
        </DialogTitle>
        <DialogContent>
          <Typography>
            Установите приложение для быстрого доступа и работы в офлайн режиме.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowInstallDialog(false)}>
            Позже
          </Button>
          <Button onClick={installApp} variant="contained">
            Установить
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог обновления */}
      <Dialog open={showUpdateDialog} onClose={() => setShowUpdateDialog(false)}>
        <DialogTitle>
          Доступно обновление
        </DialogTitle>
        <DialogContent>
          <Typography>
            Доступна новая версия приложения. Обновить сейчас?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowUpdateDialog(false)}>
            Позже
          </Button>
          <Button onClick={updateApp} variant="contained">
            Обновить
          </Button>
        </DialogActions>
      </Dialog>
    </PWAContext.Provider>
  );
};
