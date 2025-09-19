import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  TextField,
  InputAdornment,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Typography,
  Chip,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  History as HistoryIcon,
  TrendingUp as TrendingIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';

interface SearchResult {
  id: string;
  title: string;
  description: string;
  type: 'ticket' | 'knowledge' | 'user' | 'setting';
  url: string;
  category?: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  status?: string;
}

interface SearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  onResultClick?: (result: SearchResult) => void;
  recentSearches?: string[];
  onClearRecent?: () => void;
  loading?: boolean;
  results?: SearchResult[];
  showSuggestions?: boolean;
  maxResults?: number;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = 'Поиск...',
  onSearch,
  onResultClick,
  recentSearches = [],
  onClearRecent,
  loading = false,
  results = [],
  showSuggestions = true,
  maxResults = 10,
}) => {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setQuery(value);
    setFocusedIndex(-1);
    
    if (value.length > 0) {
      setIsOpen(true);
      onSearch?.(value);
    } else {
      setIsOpen(false);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (!isOpen) return;

    const totalItems = Math.min(results.length, maxResults) + recentSearches.length;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setFocusedIndex(prev => (prev + 1) % totalItems);
        break;
      case 'ArrowUp':
        event.preventDefault();
        setFocusedIndex(prev => (prev - 1 + totalItems) % totalItems);
        break;
      case 'Enter':
        event.preventDefault();
        if (focusedIndex >= 0 && focusedIndex < results.length) {
          handleResultClick(results[focusedIndex]);
        } else if (focusedIndex >= results.length) {
          const recentIndex = focusedIndex - results.length;
          handleRecentClick(recentSearches[recentIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        inputRef.current?.blur();
        break;
    }
  };

  const handleResultClick = (result: SearchResult) => {
    onResultClick?.(result);
    setIsOpen(false);
    setQuery('');
    inputRef.current?.blur();
  };

  const handleRecentClick = (recentQuery: string) => {
    setQuery(recentQuery);
    onSearch?.(recentQuery);
    setIsOpen(false);
    inputRef.current?.blur();
  };

  const handleClear = () => {
    setQuery('');
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const getResultIcon = (type: string) => {
    switch (type) {
      case 'ticket':
        return '🎫';
      case 'knowledge':
        return '📚';
      case 'user':
        return '👤';
      case 'setting':
        return '⚙️';
      default:
        return '🔍';
    }
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'urgent':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'default';
      default:
        return 'default';
    }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (listRef.current && !listRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <Box sx={{ position: 'relative', width: '100%' }} ref={listRef}>
      <TextField
        ref={inputRef}
        fullWidth
        value={query}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onFocus={() => query.length > 0 && setIsOpen(true)}
        placeholder={placeholder}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              {loading ? (
                <CircularProgress size={20} />
              ) : (
                <SearchIcon color="action" />
              )}
            </InputAdornment>
          ),
          endAdornment: query && (
            <InputAdornment position="end">
              <IconButton onClick={handleClear} size="small">
                <ClearIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 3,
            backgroundColor: 'background.paper',
          },
        }}
      />

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <Paper
              sx={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                mt: 1,
                maxHeight: 400,
                overflow: 'auto',
                zIndex: 1000,
                boxShadow: 3,
              }}
            >
              {/* Результаты поиска */}
              {results.length > 0 && (
                <>
                  <Box sx={{ p: 2, pb: 1 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Результаты поиска
                    </Typography>
                  </Box>
                  <List sx={{ p: 0 }}>
                    {results.slice(0, maxResults).map((result, index) => (
                      <motion.div
                        key={result.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.2, delay: index * 0.05 }}
                      >
                        <ListItem
                          button
                          onClick={() => handleResultClick(result)}
                          sx={{
                            backgroundColor: focusedIndex === index ? 'action.hover' : 'transparent',
                            '&:hover': {
                              backgroundColor: 'action.hover',
                            },
                          }}
                        >
                          <ListItemIcon>
                            <Typography sx={{ fontSize: '1.2rem' }}>
                              {getResultIcon(result.type)}
                            </Typography>
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                                  {result.title}
                                </Typography>
                                {result.priority && (
                                  <Chip
                                    label={result.priority}
                                    size="small"
                                    color={getPriorityColor(result.priority)}
                                    sx={{ fontSize: '0.75rem' }}
                                  />
                                )}
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  {result.description}
                                </Typography>
                                {result.category && (
                                  <Chip
                                    label={result.category}
                                    size="small"
                                    variant="outlined"
                                    sx={{ mt: 0.5, fontSize: '0.75rem' }}
                                  />
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                      </motion.div>
                    ))}
                  </List>
                </>
              )}

              {/* Недавние поиски */}
              {recentSearches.length > 0 && query.length === 0 && (
                <>
                  {results.length > 0 && <Divider />}
                  <Box sx={{ p: 2, pb: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Недавние поиски
                      </Typography>
                      <IconButton size="small" onClick={onClearRecent}>
                        <CloseIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>
                  <List sx={{ p: 0 }}>
                    {recentSearches.map((recent, index) => (
                      <motion.div
                        key={recent}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.2, delay: index * 0.05 }}
                      >
                        <ListItem
                          button
                          onClick={() => handleRecentClick(recent)}
                          sx={{
                            backgroundColor: focusedIndex === results.length + index ? 'action.hover' : 'transparent',
                            '&:hover': {
                              backgroundColor: 'action.hover',
                            },
                          }}
                        >
                          <ListItemIcon>
                            <HistoryIcon color="action" />
                          </ListItemIcon>
                          <ListItemText
                            primary={recent}
                            primaryTypographyProps={{
                              variant: 'body2',
                              color: 'text.secondary',
                            }}
                          />
                        </ListItem>
                      </motion.div>
                    ))}
                  </List>
                </>
              )}

              {/* Пустое состояние */}
              {results.length === 0 && recentSearches.length === 0 && query.length > 0 && (
                <Box sx={{ p: 3, textAlign: 'center' }}>
                  <SearchIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="body2" color="text.secondary">
                    Ничего не найдено
                  </Typography>
                </Box>
              )}
            </Paper>
          </motion.div>
        )}
      </AnimatePresence>
    </Box>
  );
};
