// UserProfile.tsx
import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  TextField,
  Button,
  Grid,
  Divider,
  Switch,
  FormControlLabel,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Alert
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Notifications as NotificationsIcon,
  History as HistoryIcon,
  VpnKey as KeyIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { userService } from '@/services/api/userService';
import { User, UserPreference, Notification, ActivityLog, ApiToken } from '@/types/domain/user';
import '../../assets/styles/components/UserProfile.scss';

const UserProfile = () => {
  const [user, setUser] = useState<User | null>(null);
  const [preferences, setPreferences] = useState<UserPreference[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([]);
  const [apiTokens, setApiTokens] = useState<ApiToken[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      setLoading(true);
      const [
        userResponse,
        preferencesResponse,
        notificationsResponse,
        activityLogsResponse,
        apiTokensResponse
      ] = await Promise.all([
        userService.getCurrentUser(),
        userService.getUserPreferences(),
        userService.getNotifications(),
        userService.getActivityLogs(),
        userService.getApiTokens()
      ]);

      setUser(userResponse.data);
      
      // Manejar respuestas vacías o null
      setPreferences(preferencesResponse.data || []);
      setNotifications(notificationsResponse.data || []);
      setActivityLogs(activityLogsResponse.data || []);
      setApiTokens(apiTokensResponse.data || []);
      
    } catch (err) {
      setError('Error al cargar los datos del usuario');
      console.error('Error fetching user data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!user) return;
    
    try {
      await userService.updateUser(user.id, user);
      setIsEditing(false);
      // Mostrar mensaje de éxito
    } catch (err) {
      setError('Error al guardar los cambios');
      console.error('Error updating user:', err);
    }
  };

  const handleCancel = () => {
    fetchUserData();
    setIsEditing(false);
  };

  const handlePreferenceChange = (key: string, value: any) => {
    setPreferences(prev => 
      prev.map(pref => 
        pref.key === key ? { ...pref, value } : pref
      )
    );
  };

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>{error}</div>;
  if (!user) return <div>Usuario no encontrado</div>;

  return (
    <div className="user-profile">
      <Typography variant="h4" gutterBottom>
        Perfil de Usuario
      </Typography>
      
      <Grid container spacing={3} className="stats-grid">
        {/* Información básica del usuario */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar 
                  sx={{ width: 80, height: 80, mr: 2 }}
                  src={user.profile_image}
                >
                  {user.first_name?.[0]}{user.last_name?.[0]}
                </Avatar>
                <Box>
                  <Typography variant="h6">
                    {user.first_name} {user.last_name}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {user.email}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    @{user.username}
                  </Typography>
                </Box>
                <IconButton 
                  sx={{ ml: 'auto' }} 
                  onClick={() => setIsEditing(!isEditing)}
                >
                  <EditIcon />
                </IconButton>
              </Box>

              <Divider sx={{ my: 2 }} />

              {isEditing ? (
                <Box component="form" sx={{ mt: 2 }}>
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12, sm: 6 }}>
                      <TextField
                        fullWidth
                        label="Nombre"
                        value={user.first_name || ''}
                        onChange={(e) => setUser({...user, first_name: e.target.value})}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, sm: 6 }}>
                      <TextField
                        fullWidth
                        label="Apellido"
                        value={user.last_name || ''}
                        onChange={(e) => setUser({...user, last_name: e.target.value})}
                      />
                    </Grid>
                    <Grid size={{ xs: 12 }}>
                      <TextField
                        fullWidth
                        label="Email"
                        type="email"
                        value={user.email}
                        onChange={(e) => setUser({...user, email: e.target.value})}
                      />
                    </Grid>
                  </Grid>
                  
                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <Button 
                      variant="contained" 
                      startIcon={<SaveIcon />}
                      onClick={handleSave}
                    >
                      Guardar
                    </Button>
                    <Button 
                      variant="outlined" 
                      startIcon={<CancelIcon />}
                      onClick={handleCancel}
                    >
                      Cancelar
                    </Button>
                  </Box>
                </Box>
              ) : (
                <Box>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Miembro desde:</strong> {new Date(user.date_joined).toLocaleDateString()}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Último acceso:</strong> {new Date(user.last_login).toLocaleDateString()}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Preferencias del usuario */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Preferencias
              </Typography>
              
              {preferences && preferences.length > 0 ? (
                preferences.map(preference => (
                  <FormControlLabel
                    key={preference.key}
                    control={
                      <Switch
                        checked={preference.value === 'true' || preference.value === true}
                        onChange={(e) => handlePreferenceChange(
                          preference.key, 
                          e.target.checked
                        )}
                      />
                    }
                    label={preference.key.replace(/_/g, ' ').toUpperCase()}
                    sx={{ display: 'block', mb: 1 }}
                  />
                ))
              ) : (
                <Alert severity="info" icon={<InfoIcon />}>
                  No hay preferencias configuradas
                </Alert>
              )}
              
              <Button 
                variant="outlined" 
                sx={{ mt: 2 }}
                onClick={() => userService.updatePreferences(preferences)}
                disabled={preferences.length === 0}
              >
                Guardar Preferencias
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Actividad y Notificaciones */}
        <Grid size={{ xs: 12, md: 6 }}>
          {/* Notificaciones */}
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <NotificationsIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Notificaciones</Typography>
              </Box>
              
              {notifications && notifications.length > 0 ? (
                <>
                  <List dense>
                    {notifications.slice(0, 5).map(notification => (
                      <ListItem key={notification.id} divider>
                        <ListItemText
                          primary={notification.message}
                          secondary={new Date(notification.timestamp).toLocaleDateString()}
                        />
                        {!notification.read && (
                          <Chip label="Nuevo" color="primary" size="small" />
                        )}
                      </ListItem>
                    ))}
                  </List>
                  
                  <Button 
                    fullWidth 
                    sx={{ mt: 1 }}
                    onClick={() => userService.markAllNotificationsAsRead()}
                  >
                    Marcar todas como leídas
                  </Button>
                </>
              ) : (
                <Alert severity="info" icon={<InfoIcon />}>
                  No hay notificaciones
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Actividad Reciente */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <HistoryIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Actividad Reciente</Typography>
              </Box>
              
              {activityLogs && activityLogs.length > 0 ? (
                <List dense>
                  {activityLogs.slice(0, 5).map(log => (
                    <ListItem key={log.id} divider>
                      <ListItemText
                        primary={log.action}
                        secondary={new Date(log.timestamp).toLocaleDateString()}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Alert severity="info" icon={<InfoIcon />}>
                  No hay actividad reciente
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* API Tokens */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <KeyIcon sx={{ mr: 1 }} />
                <Typography variant="h6">API Tokens</Typography>
              </Box>
              
              {apiTokens && apiTokens.length > 0 ? (
                <>
                  <List dense>
                    {apiTokens.map(token => (
                      <ListItem key={token.id} divider>
                        <ListItemIcon>
                          <KeyIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary={token.name}
                          secondary={`Último uso: ${token.last_used ? new Date(token.last_used).toLocaleDateString() : 'Nunca'}`}
                        />
                        <IconButton 
                          size="small"
                          onClick={() => userService.revokeToken(token.id)}
                        >
                          <CancelIcon />
                        </IconButton>
                      </ListItem>
                    ))}
                  </List>
                  
                  <Button 
                    variant="contained" 
                    fullWidth 
                    sx={{ mt: 1 }}
                    onClick={() => userService.generateToken('Nuevo Token')}
                  >
                    Generar Nuevo Token
                  </Button>
                </>
              ) : (
                <Alert severity="info" icon={<InfoIcon />}>
                  No hay API Tokens generados
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </div>
  );
};

export default UserProfile;