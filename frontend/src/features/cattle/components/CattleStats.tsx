// src/features/cattle/components/CattleStats.tsx
import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress
} from '@mui/material';
import {
  Pets as AnimalsIcon,
  Groups as BatchesIcon,
  Assignment as CertificationsIcon,
  TrendingUp as TrendingIcon
} from '@mui/icons-material';
import { CattleStats as CattleStatsType } from '../../../types/domain/cattle';

interface CattleStatsProps {
  stats: CattleStatsType;
}

const CattleStats: React.FC<CattleStatsProps> = ({ stats }) => {
  const statCards = [
    {
      title: 'Total Animales',
      value: stats.total_animals,
      icon: <AnimalsIcon sx={{ fontSize: 40 }} />,
      color: 'primary.main'
    },
    {
      title: 'Animales con NFT',
      value: stats.minted_animals,
      icon: <CertificationsIcon sx={{ fontSize: 40 }} />,
      color: 'secondary.main'
    },
    {
      title: 'Total Lotes',
      value: stats.total_batches,
      icon: <BatchesIcon sx={{ fontSize: 40 }} />,
      color: 'success.main'
    },
    {
      title: 'Salud Promedio',
      value: 'Buena',
      icon: <TrendingIcon sx={{ fontSize: 40 }} />,
      color: 'info.main',
      progress: true
    }
  ];

  return (
    <Grid container spacing={3}>
      {statCards.map((card, index) => (
        <Grid size={{ xs: 12, sm: 6, md: 3 }} key={index}>
          <Card sx={{ bgcolor: card.color, color: 'white' }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {card.value}
                  </Typography>
                  <Typography variant="body2">
                    {card.title}
                  </Typography>
                </Box>
                <Box sx={{ opacity: 0.8 }}>
                  {card.icon}
                </Box>
              </Box>
              {card.progress && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress
                    variant="determinate"
                    value={75}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      bgcolor: 'rgba(255, 255, 255, 0.3)',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: 'white'
                      }
                    }}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default CattleStats;