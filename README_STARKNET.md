# 🥩 BeefChain - Traceability Anchored on Bitcoin

**A hybrid blockchain architecture (StarkNet + Bitcoin) for premium meat traceability.**

[![StarkNet](https://img.shields.io/badge/StarkNet-%5E0.9.0-ff69b4)](https://starknet.io/)
[![Bitcoin](https://img.shields.io/badge/Bitcoin-Atomiq%20Protocol-orange)](https://atomiq.xyz/)
[![Xverse](https://img.shields.io/badge/Wallet-Xverse-green)](https://www.xverse.app/)
[![Django](https://img.shields.io/badge/Backend-Django%204.2-success)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/Frontend-React%2FVite-blue)](https://reactjs.org/)

![BeefChain Architecture](https://raw.githubusercontent.com/vices1967-beep/GanadoChain/main/backend/static/images/architecture.png)  
*Hybrid Architecture: StarkNet for scalable operations + Bitcoin for immutable certification*

## 🏆 Hackathon Focus: Bitcoin Unleashed Track

This project demonstrates a novel hybrid approach for supply chain traceability:
- **StarkNet Layer:** Handles high-volume, low-cost operations (animal registration, IoT data, status changes).
- **Bitcoin Layer:** Provides ultimate immutability for final certification using the **Atomiq Protocol** and **Xverse wallets**.

## 🚀 Key Innovation: The Bitcoin Certification Flow

This is the core demo flow:

1. **Request Certification:** A producer requests Bitcoin certification for a batch (`request_btc_certification`).
2. **StarkNet Event:** The `GanadoRegistry` contract emits a `LoteCertified` event.
3. **Oracle Listens:** A Django-based oracle listens for the event.
4. **Mint on Bitcoin:** The oracle mints a certification NFT on Bitcoin testnet using Atomiq.
5. **Anchor Proof:** The Bitcoin transaction hash is recorded back on StarkNet.
6. **Consumer Verification:** End-users scan a QR code to verify the entire history, capped by the Bitcoin proof.

## 🛠️ Project Structure


## ⚡ Quick Start: Experience the Demo

### Prerequisites

### 1. Clone and Setup

### 2. Run the Oracle & Demo

### 3. Experience the Bitcoin Flow

## 📱 Demo Video

## 🔮 Future Vision

This project focuses on the certification flow. The full vision includes:
- Automatic revenue sharing between supply chain participants
- Token-based governance for standards
- Zero-knowledge proofs for private data verification
- Decentralized IoT data oracles

Explore the feature-rich branch for work-in-progress on these features.

## 👨‍💻 Team
- **Victor Viceconti** - Industrial Eng / Full Stack Dev ([GitHub](https://github.com/vices1967-beep)) 

## 🎯 Technical Implementation

This project utilizes:
- ✅ StarkNet for scalable operations
- ✅ Atomiq Protocol for Bitcoin-based assets
- ✅ Xverse for Bitcoin wallet integration
- ✅ React for mobile-first experience

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

# 🥩 BeefChain - Trazabilidad Anclada en Bitcoin

**Una arquitectura blockchain híbrida (StarkNet + Bitcoin) para trazabilidad de carne premium.**

[![StarkNet](https://img.shields.io/badge/StarkNet-%5E0.9.0-ff69b4)](https://starknet.io/)
[![Bitcoin](https://img.shields.io/badge/Bitcoin-Atomiq%20Protocol-orange)](https://atomiq.xyz/)
[![Xverse](https://img.shields.io/badge/Wallet-Xverse-green)](https://www.xverse.app/)
[![Django](https://img.shields.io/badge/Backend-Django%204.2-success)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/Frontend-React%2FVite-blue)](https://reactjs.org/)

![Arquitectura BeefChain](https://raw.githubusercontent.com/vices1967-beep/GanadoChain/main/backend/static/images/architecture.png)  
*Arquitectura Híbrida: StarkNet para operaciones escalables + Bitcoin para certificación inmutable*

## 🏆 Enfoque Técnico: Bitcoin Unleashed

Este proyecto demuestra un enfoque híbrido novedoso para trazabilidad de cadena de suministro:
- **Capa StarkNet:** Maneja operaciones de alto volumen y bajo costo (registro de animales, datos IoT, cambios de estado).
- **Capa Bitcoin:** Provee inmutabilidad definitiva para certificación final usando el **Protocolo Atomiq** y **billeteras Xverse**.

## 🚀 Innovación Principal: El Flujo de Certificación Bitcoin

Este es el flujo central de demostración:

1. **Solicitud de Certificación:** Un productor solicita certificación Bitcoin para un lote (`request_btc_certification`).
2. **Evento StarkNet:** El contrato `GanadoRegistry` emite un evento `LoteCertified`.
3. **Oracle Escucha:** Un oráculo basado en Django escucha el evento.
4. **Acuñación en Bitcoin:** El oráculo acuña un NFT de certificación en Bitcoin testnet usando Atomiq.
5. **Prueba de Anclaje:** El hash de la transacción Bitcoin se registra de vuelta en StarkNet.
6. **Verificación del Consumidor:** Usuarios finales escanean un código QR para verificar todo el historial, culminando con la prueba Bitcoin.

## 🛠️ Estructura del Proyecto
GanadoChain/
├── backend/                 # API REST Django + Oracle
│   ├── analytics/          # Módulos de análisis de datos
│   ├── blockchain/         # Capa de integración blockchain
│   ├── cattle/             # App de gestión de ganado
│   ├── core/               # Configuración principal
│   ├── governance/         # DAO y gobernanza de tokens
│   ├── iot/                # Procesamiento de datos IoT
│   ├── market/             # Funcionalidad de marketplace
│   ├── reports/            # Reportes y analytics
│   ├── rewards/            # Sistema de recompensas con tokens
│   ├── users/              # Gestión de usuarios
│   ├── requirements.txt    # Dependencias Python
│   └── manage.py           # Script de gestión Django
├── frontend/               # Aplicación frontend React/Vite
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── pages/         # Páginas de la aplicación
│   │   ├── hooks/         # Custom hooks de React
│   │   └── utils/         # Funciones utilitarias
│   ├── package.json       # Dependencias Node.js
│   └── vite.config.js     # Configuración Vite
├── starknet/               # Contratos inteligentes StarkNet (Cairo)
│   ├── src/
│   │   ├── AnimalNFT.cairo      # ERC-721 para tokens de animales
│   │   ├── GanadoRegistry.cairo # Contrato principal de registro
│   │   └── lib.cairo            # Funciones de librería
│   ├── Scarb.toml         # Configuración del proyecto
│   ├── Scarb.lock         # Archivo de bloqueo de dependencias
│   └── target/            # Artefactos compilados (ignorado)
└── hardhat/               # Contratos legacy de Ethereum
    ├── contracts/         # Contratos inteligentes Solidity
    ├── scripts/           # Scripts de despliegue
    └── test/              # Tests de contratos
## ⚡ Inicio Rápido: Experimenta la Demostración

### Prerrequisitos

### 1. Clonar y Configurar
# Clonar el repositorio
git clone https://github.com/vices1967-beep/GanadoChain
cd GanadoChain

# Configurar entorno virtual Python
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar dependencias Node.js
cd ../frontend
npm install

# Compilar contratos StarkNet
cd ../starknet
scarb build

### 2. Ejecutar el Oracle y la Demostración
#### Terminal 1 - Iniciar backend Django
cd backend
python manage.py migrate
python manage.py runserver

#### Terminal 2 - Iniciar listener de eventos para certificación Bitcoin
python manage.py listen_btc

#### Terminal 3 - Iniciar frontend React
cd frontend
npm run dev

#### Terminal 4 - (Opcional) Iniciar blockchain local para testing
docker-compose up -d
### 3. Experimenta el Flujo Bitcoin
Accede a la aplicación en http://localhost:3000

Navega a la pestaña Admin Demo

Selecciona un lote de ganado de las opciones disponibles

Haz clic en "Certify on Bitcoin" para iniciar el proceso de certificación

Monitorea las terminales para ver el Oracle procesando y acuñando el NFT en Bitcoin

Escanea el código QR generado en la pestaña Verify para ver la prueba Bitcoin

Verifica la transacción en el explorador de Bitcoin testnet usando el hash TX 
## 📱 Video de Demostración

## 🔮 Visión Futura

Este proyecto se enfoca en el flujo de certificación. La visión completa incluye:
- Distribución automática de ingresos entre participantes de la cadena
- Gobernanza basada en tokens para estándares
- Pruebas de conocimiento cero para verificación de datos privados
- Oracles descentralizados para datos IoT

Explora la rama con más funciones para ver el trabajo en progreso de estas características.

## 👨‍💻 Equipo
- **Victor Viceconti** - Ingeniero Industrial / Desarrollador Full Stack ([GitHub](https://github.com/vices1967-beep))

## 🎯 Implementación Técnica

Este proyecto utiliza:
- ✅ StarkNet para operaciones escalables
- ✅ Protocolo Atomiq para activos basados en Bitcoin
- ✅ Xverse para integración con billeteras Bitcoin
- ✅ React para experiencia mobile-first

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para detalles.