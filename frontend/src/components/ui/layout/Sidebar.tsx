// src/components/ui/layout/Sidebar.tsx
import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  Box,
  Typography,
  Chip
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Pets as AnimalsIcon,
  Groups as BatchesIcon,
  Assignment as CertificationsIcon,
  ShowChart as AnalyticsIcon,
  Devices as IoTIcon,
  ShoppingCart as MarketIcon,
  AccountBalance as GovernanceIcon,
  CardGiftcard as RewardsIcon,
  ExitToApp as LogoutIcon,
  AccountCircle as AccountCircleIcon // ← Añadir esta importación
} from '@mui/icons-material';
import { useAuth } from '../../../contexts/auth/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import '../../../assets/styles/global.scss';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      text: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/dashboard'
    },
    {
      text: 'Animales',
      icon: <AnimalsIcon />,
      path: '/animals',
      badge: '24'
    },
    {
      text: 'Lotes',
      icon: <BatchesIcon />,
      path: '/batches'
    },
    {
      text: 'Certificaciones',
      icon: <CertificationsIcon />,
      path: '/certifications'
    },
    { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
    { text: 'Dispositivos IoT', icon: <IoTIcon />, path: '/iot' },
    { text: 'Mercado', icon: <MarketIcon />, path: '/market' },
    { text: 'Gobernanza', icon: <GovernanceIcon />, path: '/governance' },
    { text: 'Recompensas', icon: <RewardsIcon />, path: '/rewards' },
    {
      text: 'Mi Perfil',
      icon: <AccountCircleIcon />,
      path: '/profile'
    }
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    onClose();
  };

  const handleLogout = () => {
    logout();
    onClose();
  };

  const drawerContent = (
    <Box className="sidebar-content">
      {/* Header */}
      <Box className="sidebar-header">
        <Typography variant="h6" className="sidebar-title">
          <DashboardIcon className="sidebar-title-icon" />
          GanadoChain
        </Typography>
      </Box>

      {/* User Info */}
      <Box className="sidebar-user-info">
        <Typography variant="subtitle2" noWrap className="user-name">
          {user?.username}
        </Typography>
        <Typography variant="body2" noWrap className="user-email">
          {user?.email}
        </Typography>
        <Chip
          label={user?.role}
          size="small"
          className="user-role-chip"
        />
        {user?.wallet_address && (
          <Typography variant="caption" noWrap className="user-wallet">
            {user.wallet_address.slice(0, 8)}...{user.wallet_address.slice(-6)}
          </Typography>
        )}
      </Box>

      {/* Navigation */}
      <List className="sidebar-menu">
        <ListSubheader className="menu-section-title">Navegación Principal</ListSubheader>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              onClick={() => handleNavigation(item.path)}
              className={`menu-item ${location.pathname === item.path ? 'active' : ''}`}
            >
              <ListItemIcon className="menu-item-icon">
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} className="menu-item-text" />
              {item.badge && (
                <Chip
                  label={item.badge}
                  size="small"
                  className="menu-item-badge"
                />
              )}
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      {/* Footer */}
      <Box className="sidebar-footer">
        <List>
          <ListItem disablePadding>
            <ListItemButton onClick={handleLogout} className="logout-button">
              <ListItemIcon>
                <LogoutIcon />
              </ListItemIcon>
              <ListItemText primary="Cerrar Sesión" />
            </ListItemButton>
          </ListItem>
        </List>
      </Box>
    </Box>
  );

  return (
    <Box component="nav" className="sidebar-nav">
      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        open={open}
        onClose={onClose}
        ModalProps={{ keepMounted: true }}
        className="sidebar-drawer-mobile"
      >
        {drawerContent}
      </Drawer>

      {/* Desktop Drawer */}
      <Drawer
        variant="permanent"
        className="sidebar-drawer-desktop"
        open
      >
        {drawerContent}
      </Drawer>
    </Box>
  );
};

export default Sidebar;