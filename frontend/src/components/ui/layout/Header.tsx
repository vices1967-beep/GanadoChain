// src/components/ui/layout/Header.tsx
import React from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Badge,
  Avatar,
  Box,
  Menu,
  MenuItem,
  Tooltip
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { useAuth } from '../../../contexts/auth/AuthContext';
import '../../../assets/styles/global.scss';

interface HeaderProps {
  toggleSidebar: () => void;
}

const Header: React.FC<HeaderProps> = ({ toggleSidebar }) => {
  const { user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleClose();
    logout();
  };

  return (
    <AppBar className="header-app-bar">
      <Toolbar className="header-toolbar">
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={toggleSidebar}
          className="toggle-sidebar-btn"
        >
          <MenuIcon />
        </IconButton>

        <Typography variant="h6" noWrap component="div" className="header-title">
          Dashboard
        </Typography>

        <Box className="search-box">
          <SearchIcon className="search-icon" />
          <input
            type="text"
            placeholder="Buscar..."
            className="search-input"
          />
        </Box>

        <Box className="header-actions">
          <IconButton color="inherit" className="notification-btn">
            <Badge badgeContent={4} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          <Tooltip title="Configuración de cuenta">
            <IconButton
              onClick={handleMenu}
              color="inherit"
              className="user-menu-btn"
            >
              <Avatar
                className="user-avatar"
              >
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </Avatar>
            </IconButton>
          </Tooltip>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
            onClick={handleClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            className="user-menu"
          >
            <MenuItem onClick={handleClose}>Perfil</MenuItem>
            <MenuItem onClick={handleClose}>Configuración</MenuItem>
            <MenuItem onClick={handleLogout}>Cerrar Sesión</MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;