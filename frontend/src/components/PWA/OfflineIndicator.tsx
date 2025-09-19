import React from 'react';
import { Box, Chip, Typography } from '@mui/material';
import { WifiOff, CloudOff } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { usePWA } from './PWAProvider';

export const OfflineIndicator: React.FC = () => {
  const { isOnline } = usePWA();

  return (
    <AnimatePresence>
      {!isOnline && (
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          transition={{ duration: 0.3 }}
        >
          <Box
            sx={{
              position: 'fixed',
              top: 16,
              left: '50%',
              transform: 'translateX(-50%)',
              zIndex: 9999,
            }}
          >
            <Chip
              icon={<WifiOff />}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CloudOff fontSize="small" />
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    Офлайн режим
                  </Typography>
                </Box>
              }
              color="warning"
              variant="filled"
              sx={{
                borderRadius: 2,
                px: 2,
                py: 1,
                '& .MuiChip-icon': {
                  color: 'inherit',
                },
              }}
            />
          </Box>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
