import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

export const KnowledgeBasePage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        {t('knowledge.title')}
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="body1">
            База знаний в разработке...
          </Typography>
        </CardContent>
      </Card>
    </motion.div>
  );
};
