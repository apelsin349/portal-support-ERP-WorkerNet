import React from 'react';
import { IconButton, Tooltip, Switch, FormControlLabel, Box } from '@mui/material';
import { DarkMode, LightMode, BrightnessAuto } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useTheme } from '@contexts/ThemeContext';

interface ThemeToggleProps {
  variant?: 'icon' | 'switch' | 'button';
  showAuto?: boolean;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ 
  variant = 'icon',
  showAuto = false 
}) => {
  const { isDarkMode, toggleTheme } = useTheme();

  if (variant === 'switch') {
    return (
      <FormControlLabel
        control={
          <Switch
            checked={isDarkMode}
            onChange={toggleTheme}
            color="primary"
          />
        }
        label={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {isDarkMode ? <DarkMode /> : <LightMode />}
            {isDarkMode ? 'Темная' : 'Светлая'}
          </Box>
        }
      />
    );
  }

  if (variant === 'button') {
    return (
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Tooltip title={isDarkMode ? 'Светлая тема' : 'Темная тема'}>
          <IconButton
            onClick={toggleTheme}
            color="inherit"
            sx={{
              p: 1.5,
              borderRadius: 2,
              backgroundColor: 'action.hover',
              '&:hover': {
                backgroundColor: 'action.selected',
              },
            }}
          >
            <motion.div
              animate={{ rotate: isDarkMode ? 180 : 0 }}
              transition={{ duration: 0.3 }}
            >
              {isDarkMode ? <LightMode /> : <DarkMode />}
            </motion.div>
          </IconButton>
        </Tooltip>
      </motion.div>
    );
  }

  return (
    <Tooltip title={isDarkMode ? 'Светлая тема' : 'Темная тема'}>
      <IconButton
        onClick={toggleTheme}
        color="inherit"
        size="large"
      >
        <motion.div
          animate={{ rotate: isDarkMode ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          {isDarkMode ? <LightMode /> : <DarkMode />}
        </motion.div>
      </IconButton>
    </Tooltip>
  );
};
