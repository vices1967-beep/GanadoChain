

GanadoChain/
 ├─ contracts/                  # Tus contratos Solidity ya existentes
 ├─ scripts/                     # Scripts Hardhat
 │    ├─ deploy_safe_multisig_prod.ts
 │    └─ create_safe_multisig.ts  <- Script para crear la Safe real
 ├─ backend/                     # Servidor Node.js / Express
 │    ├─ index.ts
 │    ├─ contracts.ts
 │    ├─ routes/
 │    │    ├─ animals.ts
 │    │    ├─ batches.ts
 │    │    └─ registry.ts
 │    └─ utils/
 │         └─ ipfs.ts
 ├─ frontend/                    # React app
 │    ├─ package.json
 │    └─ src/
 │         ├─ App.jsx
 │         └─ components/
 ├─ deployed_addresses.json      # Direcciones de tus contratos
 ├─ hardhat.config.ts
 └─ package.json


Explicación:

Productores crean tokens y NFTs de animales/lotes y envían datos crudos al backend.

Veterinarios y frigoríficos actualizan datos autorizados.

Backend calcula hashes y los guarda en GanadoRegistryUpgradeable.

Safe Multisig controla todas las operaciones críticas (mint de tokens, transferencias, updates).

Consumidores finales acceden solo a datos de trazabilidad vía QR.

```mermaid
flowchart LR
    subgraph Producción
        P1[Productor] -->|Crea Animal/Lote| NFT[AnimalNFTUpgradeable]
        P1 -->|Crea/Transfiere Lotes| ERC20[GanadoTokenUpgradeable]
        P1 -->|Registra datos GPS/IoT| Backend
    end

    subgraph Salud
        Vet[Veterinario] -->|Registra vacunas y tratamientos| Backend
    end

    subgraph Procesamiento
        Frio[Frigorífico] -->|Registra cortes, lotes, QR| Backend
    end

    Backend -->|Genera hash| Registry[GanadoRegistryUpgradeable]
    ERC20 --> Registry
    NFT --> Registry

    subgraph Safe Multisig
        Safe[Safe Multisig]
        ERC20 -.->|Transacciones aprobadas| Safe
        NFT -.->|Mint/Transferencias aprobadas| Safe
        Registry -.->|Updates aprobadas| Safe
    end

    subgraph Consumidor
        QR[QR Corte] -->|Consulta trazabilidad| Frontend
        Frontend --> Registry
        Frontend --> Backend
    end
