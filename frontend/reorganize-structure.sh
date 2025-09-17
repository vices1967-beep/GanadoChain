#!/bin/bash
# Script de reorganización estructural para GanadoChain Frontend
# Este script reorganiza la estructura para alinearla con el backend

echo "Iniciando reorganización estructural de GanadoChain Frontend..."

# Crear directorios faltantes críticos
echo "Creando directorios faltantes..."
mkdir -p src/features/core
mkdir -p src/features/reports
mkdir -p src/features/certifications
mkdir -p src/apis/rest/core
mkdir -p src/apis/rest/reports
mkdir -p src/services/core
mkdir -p src/services/reports
mkdir -p src/stores/slices/core
mkdir -p src/stores/slices/reports
mkdir -p src/stores/selectors/core
mkdir -p src/stores/selectors/reports
mkdir -p src/types/domain/core
mkdir -p src/types/domain/reports

# Reorganizar features por módulos del backend
echo "Reorganizando features..."
# Mover y renombrar features existentes para mejor alineación
mv src/features/analytics src/features/analytics-temp
mv src/features/rewards src/features/rewards-temp

# Crear nueva estructura de features
mkdir -p src/features/analytics/{components,hooks,views}
mkdir -p src/features/core/{components,hooks,views}
mkdir -p src/features/governance/{components,hooks,views}
mkdir -p src/features/reports/{components,hooks,views}
mkdir -p src/features/rewards/{components,hooks,views}
mkdir -p src/features/certifications/{components,hooks,views}

# Mover contenido existente a nueva estructura
mv src/features/analytics-temp/* src/features/analytics/ 2>/dev/null
mv src/features/rewards-temp/* src/features/rewards/ 2>/dev/null
rmdir src/features/analytics-temp
rmdir src/features/rewards-temp

# Reorganizar APIs REST
echo "Reorganizando APIs REST..."
mkdir -p src/apis/rest/backup
mv src/apis/rest/*.ts src/apis/rest/backup/ 2>/dev/null

# Crear estructura de APIs alineada con backend
touch src/apis/rest/core.ts
touch src/apis/rest/analytics.ts
touch src/apis/rest/blockchain.ts
touch src/apis/rest/cattle.ts
touch src/apis/rest/consumer.ts
touch src/apis/rest/governance.ts
touch src/apis/rest/iot.ts
touch src/apis/rest/market.ts
touch src/apis/rest/reports.ts
touch src/apis/rest/rewards.ts

# Reorganizar servicios
echo "Reorganizando servicios..."
mkdir -p src/services/backup
mv src/services/*.ts src/services/backup/ 2>/dev/null

# Crear servicios alineados con backend
touch src/services/core/coreService.ts
touch src/services/analytics/analyticsService.ts
touch src/services/blockchain/blockchainService.ts
touch src/services/cattle/cattleService.ts
touch src/services/consumer/consumerService.ts
touch src/services/governance/governanceService.ts
touch src/services/iot/iotService.ts
touch src/services/market/marketService.ts
touch src/services/reports/reportService.ts
touch src/services/rewards/rewardService.ts

# Reorganizar stores y slices
echo "Reorganizando stores..."
mkdir -p src/stores/slices/backup
mv src/stores/slices/*.ts src/stores/slices/backup/ 2>/dev/null

# Crear slices alineados
touch src/stores/slices/core.slice.ts
touch src/stores/slices/analytics.slice.ts
touch src/stores/slices/blockchain.slice.ts
touch src/stores/slices/cattle.slice.ts
touch src/stores/slices/consumer.slice.ts
touch src/stores/slices/governance.slice.ts
touch src/stores/slices/iot.slice.ts
touch src/stores/slices/market.slice.ts
touch src/stores/slices/reports.slice.ts
touch src/stores/slices/rewards.slice.ts

# Reorganizar tipos TypeScript
echo "Reorganizando tipos..."
mkdir -p src/types/domain/backup
mv src/types/domain/*.ts src/types/domain/backup/ 2>/dev/null

# Crear tipos alineados con backend
touch src/types/domain/core.ts
touch src/types/domain/analytics.ts
touch src/types/domain/blockchain.ts
touch src/types/domain/cattle.ts
touch src/types/domain/consumer.ts
touch src/types/domain/governance.ts
touch src/types/domain/iot.ts
touch src/types/domain/market.ts
touch src/types/domain/reports.ts
touch src/types/domain/rewards.ts

# Crear archivos de índice para nuevos módulos
echo "Creando archivos índice..."
for dir in src/features/* src/apis/rest src/services src/stores/slices src/types/domain; do
  if [ -d "$dir" ]; then
    touch "$dir/index.ts"
  fi
done

# Crear estructura de componentes para nuevos módulos
echo "Creando estructura de componentes..."
# Core components
mkdir -p src/features/core/components/SystemHealth
mkdir -p src/features/core/components/MetricsDashboard
mkdir -p src/features/core/components/ConfigManager

# Governance components
mkdir -p src/features/governance/components/ProposalList
mkdir -p src/features/governance/components/ProposalDetail
mkdir -p src/features/governance/components/VotingInterface
mkdir -p src/features/governance/components/GovernanceStats

# Reports components
mkdir -p src/features/reports/components/ReportGenerator
mkdir -p src/features/reports/components/ComplianceReports
mkdir -p src/features/reports/components/AuditReports
mkdir -p src/features/reports/components/FinancialReports

# Rewards components
mkdir -p src/features/rewards/components/StakingInterface
mkdir -p src/features/rewards/components/RewardClaim
mkdir -p src/features/rewards/components/Leaderboard
mkdir -p src/features/rewards/components/RewardStats

# Crear archivos básicos de componentes
create_component() {
  local dir=$1
  local name=$2
  cat > "$dir/${name}.tsx" << EOF
import React from 'react';

const ${name}: React.FC = () => {
  return (
    <div>
      <h2>${name}</h2>
      {/* Implementar componente aquí */}
    </div>
  );
};

export default ${name};
EOF
  touch "$dir/index.ts"
}

echo "Creando componentes básicos..."
create_component "src/features/core/components/SystemHealth" "SystemHealth"
create_component "src/features/core/components/MetricsDashboard" "MetricsDashboard"
create_component "src/features/core/components/ConfigManager" "ConfigManager"

create_component "src/features/governance/components/ProposalList" "ProposalList"
create_component "src/features/governance/components/ProposalDetail" "ProposalDetail"
create_component "src/features/governance/components/VotingInterface" "VotingInterface"
create_component "src/features/governance/components/GovernanceStats" "GovernanceStats"

create_component "src/features/reports/components/ReportGenerator" "ReportGenerator"
create_component "src/features/reports/components/ComplianceReports" "ComplianceReports"
create_component "src/features/reports/components/AuditReports" "AuditReports"
create_component "src/features/reports/components/FinancialReports" "FinancialReports"

create_component "src/features/rewards/components/StakingInterface" "StakingInterface"
create_component "src/features/rewards/components/RewardClaim" "RewardClaim"
create_component "src/features/rewards/components/Leaderboard" "Leaderboard"
create_component "src/features/rewards/components/RewardStats" "RewardStats"

# Actualizar archivos de barril (index.ts)
echo "Actualizando archivos de barril..."
for feature in core governance reports rewards; do
  cat > "src/features/${feature}/index.ts" << EOF
export * from './components';
export * from './hooks';
export * from './views';
EOF
done

# Crear estructura de vistas para nuevos módulos
echo "Creando vistas..."
for feature in core governance reports rewards; do
  mkdir -p "src/features/${feature}/views"
  touch "src/features/${feature}/views/index.ts"
  
  case $feature in
    core)
      views=("SystemMetrics" "HealthCheck" "SystemConfig" "Dashboard" "Validation" "Maintenance" "APIInfo")
      ;;
    governance)
      views=("Proposals" "Voting" "GovernanceStats" "UserVoting" "ActiveProposals" "ProposalTimeline")
      ;;
    reports)
      views=("Compliance" "Audit" "Financial" "SystemHealth" "Export" "ReportGenerator")
      ;;
    rewards)
      views=("Rewards" "Staking" "Claim" "Leaderboard" "UserRewards")
      ;;
  esac
  
  for view in "${views[@]}"; do
    cat > "src/features/${feature}/views/${view}View.tsx" << EOF
import React from 'react';

const ${view}View: React.FC = () => {
  return (
    <div>
      <h1>${view}</h1>
      {/* Implementar vista aquí */}
    </div>
  );
};

export default ${view}View;
EOF
    echo "export { default as ${view}View } from './${view}View';" >> "src/features/${feature}/views/index.ts"
  done
done

# Crear hooks básicos para nuevos módulos
echo "Creando hooks..."
for feature in core governance reports rewards; do
  mkdir -p "src/features/${feature}/hooks"
  touch "src/features/${feature}/hooks/index.ts"
  
  cat > "src/features/${feature}/hooks/use${feature^}.ts" << EOF
import { useCallback } from 'react';

export const use${feature^} = () => {
  // Implementar lógica específica del módulo ${feature}
  
  const fetchData = useCallback(async () => {
    // Lógica para fetch data
  }, []);

  return {
    fetchData,
    // otros métodos y valores
  };
};
EOF
  echo "export * from './use${feature^}';" >> "src/features/${feature}/hooks/index.ts"
done

# Actualizar el enrutamiento para incluir nuevos módulos
echo "Actualizando enrutamiento..."
mkdir -p src/router/routes/backup
mv src/router/routes/*.ts src/router/routes/backup/ 2>/dev/null

# Crear rutas para nuevos módulos
cat > src/router/routes/core.ts << 'EOF'
import { lazy } from 'react';

export const coreRoutes = [
  {
    path: '/core/metrics',
    component: lazy(() => import('../../../features/core/views/SystemMetricsView')),
    roles: ['admin'],
  },
  {
    path: '/core/health',
    component: lazy(() => import('../../../features/core/views/HealthCheckView')),
    roles: ['admin'],
  },
  // ... otras rutas core
];
EOF

cat > src/router/routes/governance.ts << 'EOF'
import { lazy } from 'react';

export const governanceRoutes = [
  {
    path: '/governance/proposals',
    component: lazy(() => import('../../../features/governance/views/ProposalsView')),
    roles: ['admin', 'user'],
  },
  {
    path: '/governance/voting',
    component: lazy(() => import('../../../features/governance/views/VotingView')),
    roles: ['admin', 'user'],
  },
  // ... otras rutas governance
];
EOF

cat > src/router/routes/reports.ts << 'EOF'
import { lazy } from 'react';

export const reportsRoutes = [
  {
    path: '/reports/compliance',
    component: lazy(() => import('../../../features/reports/views/ComplianceView')),
    roles: ['admin', 'auditor'],
  },
  {
    path: '/reports/audit',
    component: lazy(() => import('../../../features/reports/views/AuditView')),
    roles: ['admin', 'auditor'],
  },
  // ... otras rutas reports
];
EOF

cat > src/router/routes/rewards.ts << 'EOF'
import { lazy } from 'react';

export const rewardsRoutes = [
  {
    path: '/rewards/staking',
    component: lazy(() => import('../../../features/rewards/views/StakingView')),
    roles: ['admin', 'user'],
  },
  {
    path: '/rewards/leaderboard',
    component: lazy(() => import('../../../features/rewards/views/LeaderboardView')),
    roles: ['admin', 'user'],
  },
  // ... otras rutas rewards
];
EOF

# Actualizar archivo de rutas principal
cat > src/router/routes/index.ts << 'EOF'
import { coreRoutes } from './core';
import { governanceRoutes } from './governance';
import { reportsRoutes } from './reports';
import { rewardsRoutes } from './rewards';
// importar otras rutas

export const allRoutes = [
  ...coreRoutes,
  ...governanceRoutes,
  ...reportsRoutes,
  ...rewardsRoutes,
  // ... otras rutas
];
EOF

echo "Reorganización completada."
echo "Estructura reorganizada:"
tree -d -L 3 src/features
echo ""
echo "Próximos pasos:"
echo "1. Revisar los archivos movidos a las carpetas backup/"
echo "2. Implementar la lógica específica en los nuevos servicios"
echo "3. Conectar los nuevos componentes con los endpoints del backend"
echo "4. Actualizar los tipos TypeScript con interfaces completas"
echo "5. Configurar las stores y slices para los nuevos módulos"