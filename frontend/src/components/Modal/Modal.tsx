import React, { useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Box,
  Typography,
  useTheme,
  useMediaQuery,
  Button,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  fullWidth?: boolean;
  fullScreen?: boolean;
  disableBackdropClick?: boolean;
  disableEscapeKeyDown?: boolean;
  showCloseButton?: boolean;
  loading?: boolean;
}

export const Modal: React.FC<ModalProps> = ({
  open,
  onClose,
  title,
  children,
  actions,
  maxWidth = 'sm',
  fullWidth = true,
  fullScreen = false,
  disableBackdropClick = false,
  disableEscapeKeyDown = false,
  showCloseButton = true,
  loading = false,
}) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [open]);

  const handleClose = (event: {}, reason: string) => {
    if (disableBackdropClick && reason === 'backdropClick') {
      return;
    }
    if (disableEscapeKeyDown && reason === 'escapeKeyDown') {
      return;
    }
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth={maxWidth}
      fullWidth={fullWidth}
      fullScreen={fullScreen || isMobile}
      PaperProps={{
        sx: {
          borderRadius: fullScreen ? 0 : 3,
          boxShadow: 3,
        },
      }}
      TransitionComponent={({ children, ...props }: any) => (
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          transition={{ duration: 0.3 }}
          {...props}
        >
          {children}
        </motion.div>
      )}
    >
      {/* Заголовок */}
      {title && (
        <DialogTitle
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            pb: 1,
            borderBottom: 1,
            borderColor: 'divider',
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {title}
          </Typography>
          {showCloseButton && (
            <IconButton
              onClick={onClose}
              size="small"
              sx={{
                color: 'text.secondary',
                '&:hover': {
                  color: 'text.primary',
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <CloseIcon />
            </IconButton>
          )}
        </DialogTitle>
      )}

      {/* Контент */}
      <DialogContent
        sx={{
          p: 3,
          '&.MuiDialogContent-root': {
            paddingTop: title ? 2 : 3,
          },
        }}
      >
        {loading ? (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: 200,
            }}
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            >
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  border: 3,
                  borderColor: 'primary.light',
                  borderTopColor: 'primary.main',
                  borderRadius: '50%',
                }}
              />
            </motion.div>
          </Box>
        ) : (
          children
        )}
      </DialogContent>

      {/* Действия */}
      {actions && (
        <DialogActions
          sx={{
            p: 3,
            pt: 1,
            borderTop: 1,
            borderColor: 'divider',
            gap: 1,
          }}
        >
          {actions}
        </DialogActions>
      )}
    </Dialog>
  );
};

// Компонент для подтверждения
interface ConfirmModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title?: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  confirmColor?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  loading?: boolean;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  open,
  onClose,
  onConfirm,
  title = 'Подтверждение',
  message,
  confirmText = 'Подтвердить',
  cancelText = 'Отмена',
  confirmColor = 'primary',
  loading = false,
}) => {
  const { t } = useTranslation();

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      maxWidth="xs"
      actions={
        <Box sx={{ display: 'flex', gap: 1 }}>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button
              variant="outlined"
              onClick={onClose}
              disabled={loading}
            >
              {cancelText}
            </Button>
          </motion.div>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button
              variant="contained"
              color={confirmColor}
              onClick={onConfirm}
              disabled={loading}
            >
              {confirmText}
            </Button>
          </motion.div>
        </Box>
      }
    >
      <Typography variant="body1">{message}</Typography>
    </Modal>
  );
};
