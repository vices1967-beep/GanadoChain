#!/bin/bash

# Script de creación de estructura profesional para GanadoChain Frontend
# Arquitectura Web3 optimizada para startup blockchain

echo "🚀 Creando estructura frontend Web3 para GanadoChain..."
echo "📁 Iniciando creación de directorios..."

# Crear estructura principal
mkdir -p \
  src/{apis,assets,components,contexts,features,hooks,libraries,providers,router,services,stores,types,utils,views} \
  public/{icons,web3} \
  scripts/{deploy,contracts} \
  docs/{architecture,contracts} \
  tests/{unit,integration,contracts} \
  .github/workflows \
  docker

echo "📁 Creando estructura de APIs y servicios..."

# APIs y servicios
mkdir -p src/apis/{blockchain,rest,web3}
touch src/apis/blockchain/{contracts,events,transactions,utils}.ts
touch src/apis/rest/{auth,cattle,iot,market,governance,rewards,analytics}.ts
touch src/apis/web3/{providers,wallets,connectors}.ts
touch src/apis/index.ts

# Servicios principales
mkdir -p src/services/{auth,blockchain,notifications,storage,analytics}
touch src/services/auth/{authService,jwtService,walletConnectService}.ts
touch src/services/blockchain/{contractService,gasService,transactionService}.ts
touch src/services/notifications/{notificationService,alertService}.ts
touch src/services/storage/{localStorage,ipfsService}.ts
touch src/services/analytics/{metricsService,loggingService}.ts
touch src/services/index.ts

echo "📁 Creando componentes de UI profesionales..."

# Componentes UI organizados por dominio
mkdir -p src/components/ui/{common,web3,layout,forms,tables,modals}
touch src/components/ui/common/{Button,Input,Card,Loading,ErrorBoundary,Toast}.tsx
touch src/components/ui/web3/{WalletConnector,NetworkIndicator,TransactionStatus,NFTPreview}.tsx
touch src/components/ui/layout/{Header,Sidebar,Footer,PageContainer,PageHeader}.tsx
touch src/components/ui/forms/{FormikFields,Validation,CustomFields,Upload}.tsx
touch src/components/ui/tables/{DataTable,PaginatedTable,SortableTable}.tsx
touch src/components/ui/modals/{ModalManager,BaseModal,ConfirmationModal}.tsx

# Componentes específicos de dominio
mkdir -p src/components/domain/{cattle,blockchain,iot,market,governance,dashboard}
touch src/components/domain/cattle/{AnimalCard,BatchTable,HealthRecord,GeneticProfile}.tsx
touch src/components/domain/blockchain/{TransactionHistory,ContractInteractions,BlockStatus}.tsx
touch src/components/domain/iot/{DeviceStatus,SensorData,RealTimeMap}.tsx
touch src/components/domain/market/{ListingCard,TradeHistory,PriceChart}.tsx
touch src/components/domain/governance/{ProposalCard,VotingWidget,GovernanceStats}.tsx
touch src/components/domain/dashboard/{StatsGrid,MetricCard,ActivityFeed}.tsx

echo "📁 Creando features y módulos de negocio..."

# Features organizadas por dominio
mkdir -p src/features/{auth,cattle,blockchain,iot,market,governance,rewards,analytics,dashboard}
for feature in auth cattle blockchain iot market governance rewards analytics dashboard; do
  mkdir -p src/features/$feature/{components,hooks,utils,types,constants}
  touch src/features/$feature/components/index.ts
  touch src/features/$feature/hooks/use$(echo $feature | awk '{print toupper(substr($0,1,1)) substr($0,2)}').ts
  touch src/features/$feature/utils/$(echo $feature | awk '{print toupper(substr($0,1,1)) substr($0,2)}').utils.ts
  touch src/features/$feature/types/index.ts
  touch src/features/$feature/constants/index.ts
done

echo "📁 Creando hooks y contextos profesionales..."

# Hooks personalizados
mkdir -p src/hooks/{web3,ui,data}
touch src/hooks/web3/{useWeb3,useContract,useTransaction,useWallet}.ts
touch src/hooks/ui/{useModal,useToast,useForm,useTable}.ts
touch src/hooks/data/{useQuery,useMutation,usePagination,useSearch}.ts

# Contextos de aplicación
mkdir -p src/contexts/{web3,auth,ui,notifications}
touch src/contexts/web3/Web3Context.tsx
touch src/contexts/auth/AuthContext.tsx
touch src/contexts/ui/UIContext.tsx
touch src/contexts/notifications/NotificationContext.tsx

echo "📁 Configurando gestión de estado y stores..."

# Stores y estado global
mkdir -p src/stores/{slices,selectors,middlewares}
touch src/stores/slices/{auth,web3,ui,cattle,blockchain}.slice.ts
touch src/stores/selectors/{auth,web3,ui,cattle,blockchain}.selectors.ts
touch src/stores/middlewares/{logger,persist,web3}.ts
touch src/stores/{store,rootReducer,hooks}.ts

echo "📁 Configurando utilidades y librerías..."

# Utilidades y librerías
mkdir -p src/utils/{formatters,validators,parsers,date,numbers}
touch src/utils/formatters/{address,units,strings}.ts
touch src/utils/validators/{schema,patterns,web3}.ts
touch src/utils/parsers/{json,blockchain,response}.ts
touch src/utils/date/{format,calculate,relative}.ts
touch src/utils/numbers/{format,calculate,convert}.ts
touch src/utils/{constants,helpers,errors}.ts

# Tipos TypeScript
mkdir -p src/types/{api,web3,domain,app}
touch src/types/api/{rest,blockchain,response}.ts
touch src/types/web3/{contracts,transactions,providers}.ts
touch src/types/domain/{cattle,iot,market,governance}.ts
touch src/types/app/{state,contexts,router}.ts
touch src/types/index.ts

echo "📁 Configurando router y vistas..."

# Router y vistas
mkdir -p src/router/{routes,guards,components}
touch src/router/routes/{public,private,web3}.ts
touch src/router/guards/{AuthGuard,Web3Guard,RoleGuard}.tsx
touch src/router/components/{Router,RouteLoader,NetworkRedirect}.tsx
touch src/router/index.ts

# Vistas/páginas
mkdir -p src/views/{public,auth,dashboard,cattle,blockchain,iot,market,governance,admin}
touch src/views/public/{Home,About,Contact}.tsx
touch src/views/auth/{Login,Register,ConnectWallet,ResetPassword}.tsx
touch src/views/dashboard/{Overview,Analytics,Activity}.tsx
touch src/views/cattle/{Animals,Batches,Health,Genetics}.tsx
touch src/views/blockchain/{Transactions,Contracts,Events,Tokens}.tsx
touch src/views/iot/{Devices,Sensors,Map,Alerts}.tsx
touch src/views/market/{Listings,Trades,Assets,History}.tsx
touch src/views/governance/{Proposals,Voting,Delegate,Results}.tsx
touch src/views/admin/{Users,System,Contracts,Analytics}.tsx

echo "📁 Configurando assets y recursos estáticos..."

# Assets
mkdir -p src/assets/{images,icons,fonts,styles}
touch src/assets/styles/{global,theme,variables,components}.scss
mkdir -p public/static/{contracts,abis,metadata}

echo "📁 Configurando archivos de configuración..."

# Archivos de configuración principales
touch .env.example .env.production .env.development
touch docker/{Dockerfile,docker-compose.yml}
touch .github/workflows/{ci,cd}.yml
touch scripts/deploy/{build,test,deploy}.sh
touch scripts/contracts/{deploy,verify,interact}.sh
touch docs/architecture/{frontend,web3,decisions}.md
touch docs/contracts/{addresses,abis,interactions}.md

# Configuración principal
touch package.json
touch tsconfig.json
touch vite.config.ts # o webpack.config.ts
touch eslint.config.js
touch prettier.config.js
touch jest.config.js
touch .gitignore
touch README.md
touch CONTRIBUTING.md
touch LICENSE

echo "📁 Creando archivos de tests..."

# Tests
mkdir -p tests/unit/{components,hooks,utils}
mkdir -p tests/integration/{apis,services,contexts}
mkdir -p tests/contracts/{interactions,events}
touch tests/unit/components/.gitkeep
touch tests/unit/hooks/.gitkeep
touch tests/unit/utils/.gitkeep
touch tests/integration/apis/.gitkeep
touch tests/integration/services/.gitkeep
touch tests/integration/contexts/.gitkeep
touch tests/contracts/interactions/.gitkeep
touch tests/contracts/events/.gitkeep
touch tests/setup.ts

echo "✅ Estructura frontend Web3 creada exitosamente!"
echo ""
echo "📋 Next steps:"
echo "1. Instalar dependencias: npm install"
echo "2. Configurar variables de entorno: cp .env.example .env"
echo "3. Configurar contratos en public/static/contracts/"
echo "4. Ejecutar desarrollo: npm run dev"
echo ""
echo "🎯 Stack recomendado:"
echo " - React 18 + TypeScript"
echo " - Vite (build tool)"
echo " - Redux Toolkit + RTK Query"
echo " - Ethers.js / Web3.js"
echo " - Material-UI / Chakra UI"
echo " - React Hook Form + Formik"
echo " - Jest + Testing Library"
echo " - GitHub Actions CI/CD"