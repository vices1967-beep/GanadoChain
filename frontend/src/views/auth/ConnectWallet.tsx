import React, { useState } from 'react';
import { useAuth } from '../../contexts/auth/AuthContext';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';

const ConnectWallet: React.FC = () => {
  const [walletAddress, setWalletAddress] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { loginWithWallet } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!walletAddress.startsWith('0x') || walletAddress.length !== 42) {
      setError('Dirección de wallet inválida');
      return;
    }

    setIsLoading(true);

    try {
      await loginWithWallet(walletAddress);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al conectar wallet');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: 2,
      }}
    >
      <Paper
        elevation={8}
        sx={{
          padding: 4,
          width: '100%',
          maxWidth: 400,
          borderRadius: 2,
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom align="center" color="primary">
          🐄 GanadoChain
        </Typography>
        
        <Typography variant="h6" component="h2" gutterBottom align="center">
          Conectar Wallet
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Dirección de Wallet"
            value={walletAddress}
            onChange={(e) => setWalletAddress(e.target.value)}
            margin="normal"
            required
            disabled={isLoading}
            placeholder="0x..."
            helperText="Ingresa tu dirección de wallet de Ethereum"
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={isLoading || !walletAddress}
            sx={{ mt: 3, mb: 2 }}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Conectar Wallet'}
          </Button>
        </form>

        <Typography variant="body2" align="center" sx={{ mt: 2 }}>
          <Button
            color="primary"
            onClick={() => navigate('/login')}
            disabled={isLoading}
          >
            Iniciar sesión con usuario
          </Button>
        </Typography>
      </Paper>
    </Box>
  );
};

export default ConnectWallet;