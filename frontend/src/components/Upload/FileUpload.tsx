import React, { useCallback, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Alert,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  FilePresent as FileIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { useTranslation } from 'react-i18next';

interface FileWithPreview extends File {
  id: string;
  preview?: string;
  progress?: number;
  status?: 'uploading' | 'success' | 'error';
  error?: string;
}

interface FileUploadProps {
  onFilesChange?: (files: FileWithPreview[]) => void;
  onFileUpload?: (file: FileWithPreview) => Promise<void>;
  onFileRemove?: (fileId: string) => void;
  maxFiles?: number;
  maxSize?: number; // в байтах
  accept?: Record<string, string[]>;
  multiple?: boolean;
  disabled?: boolean;
  showPreview?: boolean;
  showProgress?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFilesChange,
  onFileUpload,
  onFileRemove,
  maxFiles = 10,
  maxSize = 10 * 1024 * 1024, // 10MB
  accept = {
    'image/*': ['.png', '.jpg', '.jpeg', '.gif'],
    'application/pdf': ['.pdf'],
    'text/*': ['.txt', '.doc', '.docx'],
  },
  multiple = true,
  disabled = false,
  showPreview = true,
  showProgress = true,
}) => {
  const { t } = useTranslation();
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const newFiles: FileWithPreview[] = acceptedFiles.map((file) => ({
        ...file,
        id: Math.random().toString(36).substr(2, 9),
        preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined,
        status: 'uploading',
        progress: 0,
      }));

      const updatedFiles = [...files, ...newFiles].slice(0, maxFiles);
      setFiles(updatedFiles);
      onFilesChange?.(updatedFiles);

      // Загружаем файлы
      newFiles.forEach((file) => {
        if (onFileUpload) {
          onFileUpload(file)
            .then(() => {
              setFiles((prev) =>
                prev.map((f) =>
                  f.id === file.id ? { ...f, status: 'success', progress: 100 } : f
                )
              );
            })
            .catch((error) => {
              setFiles((prev) =>
                prev.map((f) =>
                  f.id === file.id
                    ? { ...f, status: 'error', error: error.message }
                    : f
                )
              );
            });
        }
      });
    },
    [files, maxFiles, onFilesChange, onFileUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    multiple,
    disabled,
    maxSize,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
  });

  const handleRemoveFile = (fileId: string) => {
    const fileToRemove = files.find((f) => f.id === fileId);
    if (fileToRemove?.preview) {
      URL.revokeObjectURL(fileToRemove.preview);
    }

    const updatedFiles = files.filter((f) => f.id !== fileId);
    setFiles(updatedFiles);
    onFilesChange?.(updatedFiles);
    onFileRemove?.(fileId);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (file: FileWithPreview) => {
    if (file.type.startsWith('image/')) {
      return '🖼️';
    } else if (file.type === 'application/pdf') {
      return '📄';
    } else if (file.type.startsWith('text/')) {
      return '📝';
    } else {
      return '📎';
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'success':
        return <CheckIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <FileIcon color="action" />;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'uploading':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      {/* Область загрузки */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          textAlign: 'center',
          cursor: disabled ? 'not-allowed' : 'pointer',
          border: 2,
          borderStyle: 'dashed',
          borderColor: isDragActive || dragActive ? 'primary.main' : 'divider',
          backgroundColor: isDragActive || dragActive ? 'primary.light' : 'background.paper',
          opacity: disabled ? 0.6 : 1,
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: disabled ? 'divider' : 'primary.main',
            backgroundColor: disabled ? 'background.paper' : 'primary.light',
          },
        }}
      >
        <input {...getInputProps()} />
        <motion.div
          animate={{ scale: isDragActive ? 1.05 : 1 }}
          transition={{ duration: 0.2 }}
        >
          <UploadIcon
            sx={{
              fontSize: 48,
              color: isDragActive ? 'primary.main' : 'text.secondary',
              mb: 2,
            }}
          />
          <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
            {isDragActive
              ? 'Отпустите файлы здесь'
              : 'Перетащите файлы сюда или нажмите для выбора'}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Поддерживаемые форматы: PNG, JPG, PDF, TXT, DOC
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Максимум {maxFiles} файлов, до {formatFileSize(maxSize)} каждый
          </Typography>
        </motion.div>
      </Paper>

      {/* Список файлов */}
      {files.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
            Загруженные файлы ({files.length})
          </Typography>
          <List>
            <AnimatePresence>
              {files.map((file, index) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                >
                  <ListItem
                    sx={{
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 2,
                      mb: 1,
                      backgroundColor: 'background.paper',
                    }}
                  >
                    <Box sx={{ mr: 2, fontSize: '1.5rem' }}>
                      {getFileIcon(file)}
                    </Box>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {file.name}
                          </Typography>
                          <Chip
                            label={formatFileSize(file.size)}
                            size="small"
                            variant="outlined"
                            sx={{ fontSize: '0.75rem' }}
                          />
                          <Chip
                            label={file.status || 'pending'}
                            size="small"
                            color={getStatusColor(file.status)}
                            sx={{ fontSize: '0.75rem' }}
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          {showProgress && file.status === 'uploading' && (
                            <LinearProgress
                              variant="determinate"
                              value={file.progress || 0}
                              sx={{ mb: 1 }}
                            />
                          )}
                          {file.error && (
                            <Alert severity="error" sx={{ mt: 1 }}>
                              {file.error}
                            </Alert>
                          )}
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getStatusIcon(file.status)}
                        <IconButton
                          edge="end"
                          onClick={() => handleRemoveFile(file.id)}
                          color="error"
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </ListItemSecondaryAction>
                  </ListItem>
                </motion.div>
              ))}
            </AnimatePresence>
          </List>
        </Box>
      )}
    </Box>
  );
};
