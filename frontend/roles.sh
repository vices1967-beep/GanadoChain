#!/bin/bash

# Script de adecuación de estructura para roles y consumidor GanadoChain
echo "🔧 Adecuando estructura para roles y consumidor..."

# Eliminar directorios que se reestructurarán
rm -rf src/views/admin/
rm -rf src/views/public/
rm -rf src/components/domain/dashboard/

# Crear estructura de roles
mkdir -p src/roles/{producer,veterinarian,consumer,admin,auditor}

# Crear componentes específicos por rol
mkdir -p src/roles/producer/{components,hooks,views}
touch src/roles/producer/components/{LivestockManager,BatchCreator,ProductionMetrics}.tsx
touch src/roles/producer/hooks/useProducer.ts
touch src/roles/producer/views/{Dashboard,Animals,Batches,Production}.tsx

mkdir -p src/roles/veterinarian/{components,hooks,views}
touch src/roles/veterinarian/components/{HealthRecords,VaccinationManager,MedicalHistory}.tsx
touch src/roles/veterinarian/hooks/useVeterinarian.ts
touch src/roles/veterinarian/views/{Dashboard,Health,Alerts,Reports}.tsx

mkdir -p src/roles/consumer/{components,hooks,views}
touch src/roles/consumer/components/{QRScanner,ProductHistory,CertificationView,QualityRating}.tsx
touch src/roles/consumer/hooks/useConsumer.ts
touch src/roles/consumer/views/{VerifyProduct,ProductHistory,QualityInfo}.tsx

mkdir -p src/roles/admin/{components,hooks,views}
touch src/roles/admin/components/{UserManager,RolesManager,SystemHealth}.tsx
touch src/roles/admin/hooks/useAdmin.ts
touch src/roles/admin/views/{Users,Roles,System,Analytics}.tsx

mkdir -p src/roles/auditor/{components,hooks,views}
touch src/roles/auditor/components/{AuditTrail,ComplianceChecker,CertificationValidator}.tsx
touch src/roles/auditor/hooks/useAuditor.ts
touch src/roles/auditor/views/{Audits,Compliance,Certifications}.tsx

# Crear sistema de permisos
mkdir -p src/auth/guards
touch src/auth/guards/{RoleGuard,PermissionGuard,RoleBasedRenderer}.tsx

mkdir -p src/auth/permissions
touch src/auth/permissions/{roles,permissions,constants}.ts

# Mejorar estructura de certificaciones
mkdir -p src/features/certifications/{components,hooks,types}
touch src/features/certifications/components/{CertificationBadge,CertificationList,CertificationDetail}.tsx
touch src/features/certifications/hooks/useCertifications.ts
touch src/features/certifications/types/index.ts

# Mejorar estructura de trazabilidad
mkdir -p src/features/traceability/{components,hooks,utils}
touch src/features/traceability/components/{TraceabilityTree,SupplyChainMap,QualityTimeline}.tsx
touch src/features/traceability/hooks/useTraceability.ts
touch src/features/traceability/utils/{formatters,parsers}.ts

# Crear servicios de QR y consumidor
mkdir -p src/services/consumer
touch src/services/consumer/{qrService,verificationService,productHistoryService}.ts

# Actualizar estructura de vistas
mkdir -p src/views/role-based/
mkdir -p src/views/public/{home,about,contact,product-verification}

# Crear componentes de landing page para consumidores
mkdir -p src/components/public/
touch src/components/public/{Hero,VerificationSection,ProductStories,TrustBadges}.tsx

# Actualizar types para roles
mkdir -p src/types/roles
touch src/types/roles/{producer,veterinarian,consumer,admin,auditor,common}.ts

# Crear hooks de autenticación mejorados
mkdir -p src/hooks/auth
touch src/hooks/auth/{useRoles,usePermissions,useAuthGuard}.ts

echo "✅ Estructura adecuada para roles y consumidor completada!"
echo ""
echo "📋 Cambios realizados:"
echo "1. ✅ Estructura de roles específicos (producer, veterinarian, consumer, admin, auditor)"
echo "2. ✅ Componentes y vistas diferenciadas por rol"
echo "3. ✅ Sistema de permisos y guards mejorado"
echo "4. ✅ Mejor estructura para certificaciones"
echo "5. ✅ Sistema de trazabilidad para consumidores"
echo "6. ✅ Servicios de QR y verificación"
echo "7. ✅ Landing page pública para verificación de productos"
echo "8. ✅ Types específicos para roles"