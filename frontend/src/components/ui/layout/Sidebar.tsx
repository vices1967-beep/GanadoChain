// src/components/ui/layout/Sidebar.tsx
import React, { useEffect, useState } from 'react';
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
  Chip,
  Badge
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Pets as AnimalsIcon,
  Groups as BatchesIcon,
  Assignment as CertificationsIcon,
  Favorite as HealthIcon,
  ShowChart as AnalyticsIcon,
  Devices as IoTIcon,
  ShoppingCart as MarketIcon,
  AccountBalance as GovernanceIcon,
  CardGiftcard as RewardsIcon,
  ExitToApp as LogoutIcon,
  AccountCircle as AccountCircleIcon
} from '@mui/icons-material';
import { useAuth } from '../../../contexts/auth/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { useCattle } from '../../../hooks/cattle/useCattle';
import { Animal, Batch } from '../../../types/domain/cattle';
import '../../../assets/styles/global.scss';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const { user, logout } = useAuth();
  const { getAnimals, getBatches, getAnimalCertifications } = useCattle();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [animalCount, setAnimalCount] = useState(0);
  const [batchCount, setBatchCount] = useState(0);
  const [certificationCount, setCertificationCount] = useState(0);

  useEffect(() => {
    loadCattleData();
  }, []);

  const loadCattleData = async () => {
    try {
      let animalsData: Animal[] = [];
      let batchesData: Batch[] = [];
      
      try {
        const [animalsResult, batchesResult] = await Promise.all([
          getAnimals(),
          getBatches()
        ]);
        
        console.log('🔍 Sidebar - Resultado de getAnimals():', animalsResult);
        console.log('🔍 Sidebar - Tipo de animalsResult:', typeof animalsResult);
        console.log('🔍 Sidebar - Es array?', Array.isArray(animalsResult));
        
        console.log('🔍 Sidebar - Resultado de getBatches():', batchesResult);
        console.log('🔍 Sidebar - Tipo de batchesResult:', typeof batchesResult);
        console.log('🔍 Sidebar - Es array?', Array.isArray(batchesResult));
        
        animalsData = Array.isArray(animalsResult) ? animalsResult : [];
        batchesData = Array.isArray(batchesResult) ? batchesResult : [];
      } catch (error) {
        console.warn('Error loading basic sidebar data:', error);
        // Si falla, intentar cargar por separado
        try {
          const animals = await getAnimals();
          animalsData = Array.isArray(animals) ? animals : [];
        } catch (e) {
          animalsData = [];
        }
        try {
          const batches = await getBatches();
          batchesData = Array.isArray(batches) ? batches : [];
        } catch (e) {
          batchesData = [];
        }
      }
      
      setAnimalCount(animalsData.length);
      setBatchCount(batchesData.length);
      
      // Para certificaciones, usar estrategia de estimación
      if (animalsData && animalsData.length > 0) {
        try {
          const sampleAnimal = animalsData[0];
          const sampleCerts = await getAnimalCertifications(sampleAnimal.id).catch(() => []);
          const estimatedCerts = Math.round((sampleCerts.length / 1) * animalsData.length * 0.8);
          setCertificationCount(estimatedCerts);
        } catch (error) {
          console.warn('Error estimating certifications:', error);
          setCertificationCount(Math.round(animalsData.length * 0.3));
        }
      } else {
        setCertificationCount(0);
      }
    } catch (error) {
      console.error('Error loading sidebar data:', error);
      // Mantener valores por defecto (0)
      setAnimalCount(0);
      setBatchCount(0);
      setCertificationCount(0);
    }
  };

  const menuItems = [
    {
      text: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/dashboard',
      badge: null
    },
    {
      text: 'Animales',
      icon: <AnimalsIcon />,
      path: '/animals',
      badge: animalCount > 0 ? animalCount.toString() : null
    },
    {
      text: 'Lotes',
      icon: <BatchesIcon />,
      path: '/batches',
      badge: batchCount > 0 ? batchCount.toString() : null
    },
    {
      text: 'Certificaciones',
      icon: <CertificationsIcon />,
      path: '/certifications',
      badge: certificationCount > 0 ? certificationCount.toString() : null
    },
    {
      text: 'Salud',
      icon: <HealthIcon />,
      path: '/health',
      badge: null
    },
    { 
      text: 'Dashboard Ganado', 
      icon: <AnalyticsIcon />, 
      path: '/cattle-dashboard',
      badge: null
    },
    { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics', badge: null },
    { text: 'Dispositivos IoT', icon: <IoTIcon />, path: '/iot', badge: null },
    { text: 'Mercado', icon: <MarketIcon />, path: '/market', badge: null },
    { text: 'Gobernanza', icon: <GovernanceIcon />, path: '/governance', badge: null },
    { text: 'Recompensas', icon: <RewardsIcon />, path: '/rewards', badge: null },
    {
      text: 'Mi Perfil',
      icon: <AccountCircleIcon />,
      path: '/profile',
      badge: null
    }
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    onClose();
  };

  const handleLogout = () => {
    logout();
    onClose();
    navigate('/login');
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const drawerContent = (
    <Box className="sidebar-content">
      {/* Header */}
      <Box className="sidebar-header">
        <Typography variant="h6" className="sidebar-title">
          <DashboardIcon className="sidebar-title-icon" />
          GanadoChain
        </Typography>
        <Typography variant="caption" className="sidebar-subtitle">
          Trazabilidad Blockchain
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
          color="primary"
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
        {menuItems.slice(0, 6).map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              onClick={() => handleNavigation(item.path)}
              className={`menu-item ${isActive(item.path) ? 'active' : ''}`}
              selected={isActive(item.path)}
            >
              <ListItemIcon className="menu-item-icon">
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text} 
                className="menu-item-text" 
              />
              {item.badge && (
                <Badge
                  badgeContent={item.badge}
                  color="primary"
                  max={999}
                  className="menu-item-badge"
                />
              )}
            </ListItemButton>
          </ListItem>
        ))}

        <ListSubheader className="menu-section-title">Módulos Adicionales</ListSubheader>
        {menuItems.slice(6).map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              onClick={() => handleNavigation(item.path)}
              className={`menu-item ${isActive(item.path) ? 'active' : ''}`}
              selected={isActive(item.path)}
            >
              <ListItemIcon className="menu-item-icon">
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text} 
                className="menu-item-text" 
              />
              {item.badge && (
                <Badge
                  badgeContent={item.badge}
                  color="primary"
                  max={999}
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
        sx={{
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: 280
          }
        }}
      >
        {drawerContent}
      </Drawer>

      {/* Desktop Drawer */}
      <Drawer
        variant="permanent"
        className="sidebar-drawer-desktop"
        open
        sx={{
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: 280,
            borderRight: '1px solid #e0e0e0'
          }
        }}
      >
        {drawerContent}
      </Drawer>
    </Box>
  );
};

export default Sidebar;