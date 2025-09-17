#!/bin/bash

# Script de limpieza y optimización de estructura GanadoChain
echo "🧹 Limpiando y optimizando estructura..."

# 1. ELIMINAR DUPLICADOS Y ESTRUCTURAS REDUNDANTES

# Las vistas de roles reemplazan a las vistas genéricas
echo "🗑️ Eliminando vistas redundantes..."
rm -rf src/views/{admin,blockchain,cattle,dashboard,governance,iot,market}/

# Los componentes de dominio están duplicados con los componentes de roles
echo "🗑️ Eliminando componentes de dominio redundantes..."
rm -rf src/components/domain/

# Los hooks de features están duplicados con hooks específicos
echo "🗑️ Limpiando hooks duplicados..."
rm -rf src/features/*/hooks/

# Los types de features están duplicados
echo "🗑️ Limpiando types duplicados..."
rm -rf src/features/*/types/

# Utils de features redundantes
echo "🗑️ Limpiando utils duplicados..."
rm -rf src/features/*/utils/

# Constants de features redundantes
echo "🗑️ Limpiando constants duplicados..."
rm -rf src/features/*/constants/

# 2. REORGANIZAR ESTRUCTURA MÁS LÓGICA

# Mover componentes públicos a estructura más clara
echo "📁 Reorganizando componentes públicos..."
mkdir -p src/views/public/components/
mv src/components/public/* src/views/public/components/
rm -rf src/components/public/

# Consolidar servicios de consumer
echo "📁 Reorganizando servicios de consumer..."
mkdir -p src/services/consumer/
mv src/services/consumer/* src/services/consumer/

# 3. ELIMINAR DIRECTORIOS VACÍOS O INNECESARIOS
echo "🗑️ Eliminando directorios vacíos..."
find . -type d -empty -delete

# 4. OPTIMIZAR ESTRUCTURA DE ROLES
echo "📁 Optimizando estructura de roles..."

# Crear index files para mejor importación
for role_dir in src/roles/*; do
  if [ -d "$role_dir" ]; then
    touch "$role_dir/index.ts"
    touch "$role_dir/components/index.ts"
    touch "$role_dir/views/index.ts"
  fi
done

# 5. CREAR ESTRUCTURA DE BARRELS PARA MEJORES IMPORTS
echo "📁 Creando barrel exports..."

# Crear barrels para features
for feature in src/features/*; do
  if [ -d "$feature" ]; then
    echo "export * from './components';" > "$feature/index.ts"
  fi
done

# Crear barrels para servicios
echo "export * from './auth';" > src/services/auth/index.ts
echo "export * from './blockchain';" > src/services/blockchain/index.ts
echo "export * from './consumer';" > src/services/consumer/index.ts
echo "export * from './notifications';" > src/services/notifications/index.ts
echo "export * from './storage';" > src/services/storage/index.ts

# 6. LIMPIAR ESTRUCTURA DE TYPES
echo "📁 Optimizando estructura de types..."

# Consolidar types de roles
mkdir -p src/types/roles/
echo "export * from './admin';" > src/types/roles/index.ts
echo "export * from './auditor';" >> src/types/roles/index.ts
echo "export * from './consumer';" >> src/types/roles/index.ts
echo "export * from './producer';" >> src/types/roles/index.ts
echo "export * from './veterinarian';" >> src/types/roles/index.ts
echo "export * from './common';" >> src/types/roles/index.ts

# 7. ACTUALIZAR ESTRUCTURA DE VISTAS PÚBLICAS
echo "📁 Reorganizando vistas públicas..."
mkdir -p src/views/public/{home,about,contact,product-verification}

# Mover componentes a sus vistas correspondientes
mkdir -p src/views/public/home/components
mkdir -p src/views/public/product-verification/components

# 8. ELIMINAR ARCHIVOS REDUNDANTES EN VIEWS
echo "🗑️ Limpiando views redundantes..."
# Las vistas específicas por rol reemplazan las genéricas

# 9. OPTIMIZAR ESTRUCTURA DE AUTH
echo "📁 Optimizando estructura de auth..."
echo "export * from './guards';" > src/auth/index.ts
echo "export * from './permissions';" >> src/auth/index.ts

# 10. CREAR ESTRUCTURA CONSISTENTE PARA HOOKS
echo "📁 Organizando hooks consistentemente..."
mkdir -p src/hooks/{auth,web3,ui,data,roles}

# Mover hooks de auth a su carpeta correspondiente
mv src/hooks/auth/* src/hooks/auth/

# 11. LIMPIAR SERVICES REDUNDANTES
echo "🗑️ Eliminando services redundantes..."
# Mantener estructura actual de services

# 12. VERIFICAR Y CREAR ARCHIVOS FALTANTES
echo "📁 Creando archivos de configuración faltantes..."
touch src/views/public/home/Home.tsx
touch src/views/public/about/About.tsx
touch src/views/public/contact/Contact.tsx
touch src/views/public/product-verification/ProductVerification.tsx

# 13. ACTUALIZAR ARCHIVOS DE RUTAS
echo "📁 Actualizando estructura de rutas..."
mkdir -p src/router/routes/roles
touch src/router/routes/roles/{producer,veterinarian,consumer,admin,auditor}.ts

# 14. ELIMINAR CARPETAS DE FEATURES REDUNDANTES
echo "🗑️ Eliminando features redundantes..."
# Mantener features para lógica de negocio, pero limpiar estructura
for feature in src/features/*; do
  if [ -d "$feature" ]; then
    # Limpiar estructura interna
    rm -rf "$feature/components"  # Los componentes están en roles/
    rm -rf "$feature/constants"   # Las constants están en utils/
    rm -rf "$feature/types"       # Los types están en types/
    rm -rf "$feature/utils"       # Los utils están en utils/
    rm -rf "$feature/hooks"       # Los hooks están en hooks/
  fi
done

# 15. CREAR NUEVA ESTRUCTURA ÓPTIMA
echo "📁 Creando estructura optimizada final..."

# Estructura final optimizada
cat > README_STRUCTURE.md << 'EOF'
# Estructura Optimizada GanadoChain Frontend
