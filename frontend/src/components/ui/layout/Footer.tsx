// src/components/layout/Footer.tsx
import React from 'react';
import { Box, Typography, Link } from '@mui/material';
import '../../../assets/styles/global.scss';

const Footer: React.FC = () => {
  return (
    <Box component="footer" className="app-footer">
      <Typography variant="body2" className="footer-text">
        © {new Date().getFullYear()} GanadoChain - Sistema de Trazabilidad Blockchain
      </Typography>
      <Typography variant="caption" className="footer-version">
        Versión {import.meta.env.VITE_APP_VERSION || '1.0.0'}
      </Typography>
      <Box className="footer-links">
        <Link href="#" variant="body2" className="footer-link">
          Términos
        </Link>
        <Link href="#" variant="body2" className="footer-link">
          Privacidad
        </Link>
        <Link href="#" variant="body2" className="footer-link">
          Soporte
        </Link>
      </Box>
    </Box>
  );
};

export default Footer;