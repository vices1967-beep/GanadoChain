// src/assets/styles/theme.ts
import { createTheme } from '@mui/material/styles';

// Importar variables SCSS (si necesitas usarlas en JS)
// Nota: Esto es opcional, ya que los temas de MUI son independientes de SCSS
const primaryColor = '#2e7d32';
const primaryDark = '#1b5e20';
const primaryLight = '#4caf50';
const secondaryColor = '#ff9800';
const secondaryDark = '#f57c00';
const secondaryLight = '#ffb74d';
const backgroundGray = '#f5f5f5';
const white = '#ffffff';
const darkGray = '#424242';
const mediumGray = '#757575';

// Tema claro (por defecto)
export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: primaryColor,
      light: primaryLight,
      dark: primaryDark,
      contrastText: white,
    },
    secondary: {
      main: secondaryColor,
      light: secondaryLight,
      dark: secondaryDark,
      contrastText: white,
    },
    success: {
      main: '#4CAF50',
      light: '#81C784',
      dark: '#388E3C',
    },
    warning: {
      main: '#FF9800',
      light: '#FFB74D',
      dark: '#F57C00',
    },
    error: {
      main: '#F44336',
      light: '#EF5350',
      dark: '#D32F2F',
    },
    info: {
      main: '#2196F3',
      light: '#64B5F6',
      dark: '#1976D2',
    },
    background: {
      default: backgroundGray,
      paper: white,
    },
    text: {
      primary: darkGray,
      secondary: mediumGray,
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h4: {
      fontWeight: 500,
    },
    h6: {
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: primaryColor,
        },
      },
    },
  },
});

// Tema oscuro
export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#4CAF50',
      light: '#81C784',
      dark: '#388E3C',
      contrastText: white,
    },
    secondary: {
      main: '#FFB74D',
      light: '#FFE97D',
      dark: '#FF9800',
      contrastText: darkGray,
    },
    success: {
      main: '#66BB6A',
      light: '#81C784',
      dark: '#388E3C',
    },
    warning: {
      main: '#FFA726',
      light: '#FFB74D',
      dark: '#F57C00',
    },
    error: {
      main: '#EF5350',
      light: '#EF9A9A',
      dark: '#C62828',
    },
    info: {
      main: '#42A5F5',
      light: '#64B5F6',
      dark: '#1976D2',
    },
    background: {
      default: '#121212',
      paper: '#1E1E1E',
    },
    text: {
      primary: white,
      secondary: '#B0B0B0',
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h4: {
      fontWeight: 500,
    },
    h6: {
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.3)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1B5E20',
        },
      },
    },
  },
});

// Exportar el tema por defecto (light)
export default lightTheme;