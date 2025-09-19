import React, { useState, useEffect } from 'react';
import { Button, IconButton, Tooltip, Badge } from '@mui/material';
import { GetApp, InstallMobile } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { usePWA } from './PWAProvider';

interface InstallButtonProps {
  variant?: 'button' | 'icon';
  showBadge?: boolean;
}

export const InstallButton: React.FC<InstallButtonProps> = ({ 
  variant = 'button',
  showBadge = true 
}) => {
  const { canInstall, isInstalled, installApp } = usePWA();
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    if (canInstall && !isInstalled) {
      setShowTooltip(true);
      const timer = setTimeout(() => setShowTooltip(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [canInstall, isInstalled]);

  if (isInstalled || !canInstall) {
    return null;
  }

  const handleInstall = () => {
    installApp();
  };

  if (variant === 'icon') {
    return (
      <Tooltip 
        title="Установить приложение" 
        open={showTooltip}
        placement="bottom"
      >
        <Badge 
          color="primary" 
          variant="dot" 
          invisible={!showBadge}
        >
          <IconButton
            onClick={handleInstall}
            color="primary"
            size="large"
            component={motion.div}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <InstallMobile />
          </IconButton>
        </Badge>
      </Tooltip>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Button
        variant="contained"
        startIcon={<GetApp />}
        onClick={handleInstall}
        sx={{
          borderRadius: 2,
          textTransform: 'none',
          fontWeight: 500,
          px: 3,
          py: 1,
        }}
        component={motion.div}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        Установить приложение
      </Button>
    </motion.div>
  );
};
