#!/bin/bash

# setup-src.sh
# Crea la estructura de src/ desde cero según el esquema definido

echo "🏗️  Creando estructura de src/ desde cero..."

# Eliminar cualquier residuo
rm -rf src/
mkdir -p src

# API
mkdir -p src/api/{cattle,iot,market,consumer,governance,reports,admin,veterinarian,auditor,frigorifico,blockchain}

# Components
mkdir -p src/components/{cattle,iot,market,consumer,governance,reports,admin,veterinarian,auditor,frigorifico,common/{Layout,UI,Charts}}

# Config
mkdir -p src/config

# Contexts
mkdir -p src/contexts

# Hooks
mkdir -p src/hooks

# Pages (todos los módulos)
mkdir -p src/pages/{Dashboard,Auth,Error,Cattle,IoT,Market,Consumer,Governance,Reports,Admin,Veterinarian,Auditor,Frigorifico}

# Styles
mkdir -p src/styles/{base,components,layouts,themes}

# Types
mkdir -p src/types

# Utils
mkdir -p src/utils/{blockchain,charts,formatters,qr,validators}

# Archivos vacíos para cada carpeta (barrel files)
touch src/api/cattle/index.ts
touch src/api/iot/index.ts
touch src/api/market/index.ts
touch src/api/consumer/index.ts
touch src/api/governance/index.ts
touch src/api/reports/index.ts
touch src/api/admin/index.ts
touch src/api/veterinarian/index.ts
touch src/api/auditor/index.ts
touch src/api/frigorifico/index.ts
touch src/api/blockchain/index.ts
touch src/api/axiosConfig.ts
touch src/api/websocket.ts

touch src/components/cattle/index.tsx
touch src/components/iot/index.tsx
touch src/components/market/index.tsx
touch src/components/consumer/index.tsx
touch src/components/governance/index.tsx
touch src/components/reports/index.tsx
touch src/components/admin/index.tsx
touch src/components/veterinarian/index.tsx
touch src/components/auditor/index.tsx
touch src/components/frigorifico/index.tsx
touch src/components/common/Layout/index.tsx
touch src/components/common/UI/index.ts
touch src/components/common/Charts/index.ts
touch src/components/index.tsx

touch src/config/api.ts
touch src/config/blockchain.ts
touch src/config/routes.tsx
touch src/config/web3.ts
touch src/config/index.ts

touch src/contexts/AuthContext.tsx
touch src/contexts/BlockchainContext.tsx
touch src/contexts/NotificationContext.tsx
touch src/contexts/WebSocketContext.tsx
touch src/contexts/index.tsx

touch src/hooks/useAuth.ts
touch src/hooks/useBlockchain.ts
touch src/hooks/useApi.ts
touch src/hooks/useDashboardData.ts
touch src/hooks/useForm.ts
touch src/hooks/useWebSocket.ts
touch src/hooks/index.ts

touch src/styles/base/reset.css
touch src/styles/base/typography.css
touch src/styles/base/variables.css
touch src/styles/components/buttons.css
touch src/styles/components/cards.css
touch src/styles/components/forms.css
touch src/styles/components/tables.css
touch src/styles/components/index.css
touch src/styles/layouts/dashboard.css
touch src/styles/layouts/header.css
touch src/styles/layouts/sidebar.css
touch src/styles/layouts/index.css
touch src/styles/themes/light.css
touch src/styles/themes/dark.css
touch src/styles/themes/index.css
touch src/styles/index.css

touch src/types/cattle.ts
touch src/types/iot.ts
touch src/types/market.ts
touch src/types/consumer.ts
touch src/types/governance.ts
touch src/types/reports.ts
touch src/types/admin.ts
touch src/types/veterinarian.ts
touch src/types/auditor.ts
touch src/types/frigorifico.ts
touch src/types/blockchain.ts
touch src/types/index.ts

touch src/utils/blockchain/contracts.ts
touch src/utils/blockchain/web3.ts
touch src/utils/blockchain/utils.ts
touch src/utils/blockchain/index.ts
touch src/utils/charts/config.ts
touch src/utils/charts/dataProcessing.ts
touch src/utils/charts/index.ts
touch src/utils/formatters/date.ts
touch src/utils/formatters/numbers.ts
touch src/utils/formatters/strings.ts
touch src/utils/formatters/index.ts
touch src/utils/qr/generator.ts
touch src/utils/qr/scanner.ts
touch src/utils/qr/index.ts
touch src/utils/validators/forms.ts
touch src/utils/validators/blockchain.ts
touch src/utils/validators/index.ts
touch src/utils/index.ts

# PAGES: Crear index.tsx en cada carpeta de página
for dir in Dashboard Auth Error Cattle IoT Market Consumer Governance Reports Admin Veterinarian Auditor Frigorifico; do
  mkdir -p "src/pages/$dir"
  touch "src/pages/$dir/index.tsx"
done

# Subcarpetas dentro de Cattle
mkdir -p src/pages/Cattle/{Animals,Batches,Health,Genetics,Certification,NFTs,Transactions}
touch src/pages/Cattle/Animals/List.tsx
touch src/pages/Cattle/Animals/Create.tsx
touch src/pages/Cattle/Animals/Edit.tsx
touch src/pages/Cattle/Animals/View.tsx
touch src/pages/Cattle/Batches/List.tsx
touch src/pages/Cattle/Batches/Create.tsx
touch src/pages/Cattle/Batches/View.tsx
touch src/pages/Cattle/Health/Records.tsx
touch src/pages/Cattle/Health/Analytics.tsx
touch src/pages/Cattle/Health/Alerts.tsx
touch src/pages/Cattle/Genetics/Pedigree.tsx
touch src/pages/Cattle/Genetics/Breeding.tsx
touch src/pages/Cattle/Certification/Certify.tsx
touch src/pages/Cattle/Certification/Verify.tsx
touch src/pages/Cattle/NFTs/Mint.tsx
touch src/pages/Cattle/NFTs/History.tsx
touch src/pages/Cattle/NFTs/View.tsx
touch src/pages/Cattle/Transactions/List.tsx
touch src/pages/Cattle/Transactions/Status.tsx
touch src/pages/Cattle/Transactions/GasOptimizer.tsx

# Subcarpetas IoT
mkdir -p src/pages/IoT/{Devices,Monitoring,Analytics}
touch src/pages/IoT/Devices/List.tsx
touch src/pages/IoT/Devices/Register.tsx
touch src/pages/IoT/Devices/Configure.tsx
touch src/pages/IoT/Monitoring/RealTime.tsx
touch src/pages/IoT/Monitoring/History.tsx
touch src/pages/IoT/Monitoring/Alerts.tsx
touch src/pages/IoT/Analytics/Health.tsx
touch src/pages/IoT/Analytics/Movement.tsx
touch src/pages/IoT/Analytics/Predictive.tsx

# Subcarpetas Market
mkdir -p src/pages/Market/{Listings,Trading,Rewards}
touch src/pages/Market/Listings/Browse.tsx
touch src/pages/Market/Listings/Create.tsx
touch src/pages/Market/Listings/MyListings.tsx
touch src/pages/Market/Listings/View.tsx
touch src/pages/Market/Trading/Buy.tsx
touch src/pages/Market/Trading/Sell.tsx
touch src/pages/Market/Trading/History.tsx
touch src/pages/Market/Trading/OrderBook.tsx
touch src/pages/Market/Rewards/Claim.tsx
touch src/pages/Market/Rewards/Leaderboard.tsx
touch src/pages/Market/Rewards/Staking.tsx
touch src/pages/Market/Rewards/Distribution.tsx

# Subcarpetas Consumer
mkdir -p src/pages/Consumer/{Search,Verification,Sustainability,Documentation}
touch src/pages/Consumer/Search/Index.tsx
touch src/pages/Consumer/Verification/QRScanner.tsx
touch src/pages/Consumer/Verification/Result.tsx
touch src/pages/Consumer/Verification/History.tsx
touch src/pages/Consumer/Sustainability/Metrics.tsx
touch src/pages/Consumer/Sustainability/Reports.tsx
touch src/pages/Consumer/Documentation/Index.tsx

# Subcarpetas Governance
mkdir -p src/pages/Governance/{Active,Proposals,Voting,Timeline,Stats}
touch src/pages/Governance/Active/Index.tsx
touch src/pages/Governance/Proposals/List.tsx
touch src/pages/Governance/Proposals/Create.tsx
touch src/pages/Governance/Proposals/View.tsx
touch src/pages/Governance/Voting/Form.tsx
touch src/pages/Governance/Voting/Results.tsx
touch src/pages/Governance/Timeline/Index.tsx
touch src/pages/Governance/Stats/Index.tsx

# Subcarpetas Reports
mkdir -p src/pages/Reports/{Audit,Compliance,Financial,SystemHealth}
touch src/pages/Reports/Audit/Index.tsx
touch src/pages/Reports/Compliance/Index.tsx
touch src/pages/Reports/Financial/Index.tsx
touch src/pages/Reports/SystemHealth/Index.tsx

# Subcarpetas Admin
mkdir -p src/pages/Admin/{Users,System,Analytics}
touch src/pages/Admin/Users/List.tsx
touch src/pages/Admin/Users/Manage.tsx
touch src/pages/Admin/Users/Roles.tsx
touch src/pages/Admin/System/Config.tsx
touch src/pages/Admin/System/Maintenance.tsx
touch src/pages/Admin/System/Metrics.tsx
touch src/pages/Admin/Analytics/Index.tsx

# Subcarpetas Veterinarian
mkdir -p src/pages/Veterinarian/{HealthRecords,Certificates,Timeline,Approvals}
touch src/pages/Veterinarian/HealthRecords/List.tsx
touch src/pages/Veterinarian/HealthRecords/Add.tsx
touch src/pages/Veterinarian/HealthRecords/View.tsx
touch src/pages/Veterinarian/Certificates/Issue.tsx
touch src/pages/Veterinarian/Certificates/Validate.tsx
touch src/pages/Veterinarian/Timeline/Index.tsx
touch src/pages/Veterinarian/Approvals/Index.tsx

# Subcarpetas Auditor
mkdir -p src/pages/Auditor/{Logs,ComplianceReports,BlockchainVerify,Certify}
touch src/pages/Auditor/Logs/Index.tsx
touch src/pages/Auditor/ComplianceReports/Generate.tsx
touch src/pages/Auditor/ComplianceReports/Download.tsx
touch src/pages/Auditor/BlockchainVerify/Index.tsx
touch src/pages/Auditor/Certify/Index.tsx

# Subcarpetas Frigorífico
mkdir -p src/pages/Frigorifico/{Receipt,Cuts,NFTsChild,QRFinal,ProcessLogs}
touch src/pages/Frigorifico/Receipt/Scan.tsx
touch src/pages/Frigorifico/Cuts/Define.tsx
touch src/pages/Frigorifico/Cuts/Assign.tsx
touch src/pages/Frigorifico/NFTsChild/Generate.tsx
touch src/pages/Frigorifico/QRFinal/Print.tsx
touch src/pages/Frigorifico/ProcessLogs/Log.tsx

# Archivos raíz
touch src/App.tsx
touch src/index.ts
touch src/main.tsx
touch src/vite-env.d.ts

echo "✅ Estructura de src/ creada correctamente."
echo ""
echo "📌 Ahora puedes empezar a desarrollar cada componente, hook o página."
echo "   Usa 'tree -L 3 src' para ver la estructura."