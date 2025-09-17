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

const Login: React.FC = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(credentials);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al iniciar sesión');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value,
    });
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
          Iniciar Sesión
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Usuario"
            name="username"
            value={credentials.username}
            onChange={handleChange}
            margin="normal"
            required
            disabled={isLoading}
          />
          
          <TextField
            fullWidth
            label="Contraseña"
            name="password"
            type="password"
            value={credentials.password}
            onChange={handleChange}
            margin="normal"
            required
            disabled={isLoading}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={isLoading}
            sx={{ mt: 3, mb: 2 }}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Iniciar Sesión'}
          </Button>
        </form>

        <Typography variant="body2" align="center" sx={{ mt: 2 }}>
          ¿No tienes cuenta?{' '}
          <Button
            color="primary"
            onClick={() => navigate('/register')}
            disabled={isLoading}
          >
            Regístrate
          </Button>
        </Typography>

        <Typography variant="body2" align="center" sx={{ mt: 1 }}>
          <Button
            color="secondary"
            onClick={() => navigate('/connect-wallet')}
            disabled={isLoading}
          >
            Conectar Wallet
          </Button>
        </Typography>
      </Paper>
    </Box>
  );
};

export default Login;