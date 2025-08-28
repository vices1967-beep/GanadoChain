

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

GanadoTokenUpgradeable.sol

✅ Roles: DAO_ROLE, MINTER_ROLE, PAUSER_ROLE, UPGRADER_ROLE.

✅ Cap total y cap por minter implementados correctamente.

✅ Eventos BatchMinted y CapUpdated incluidos.

✅ Funciones mintByDAO y mintByMinter preparadas para registro de lotes (batchId) → coincide con el CRUD de backend.

✅ Pausable y UUPS correctamente implementados.

✅ No hay problemas de seguridad aparentes en esta versión.

AnimalNFTUpgradeable.sol (modificado para CRUD backend)

✅ Soporte completo para mint, transfer, burn si es necesario.

✅ Almacena metadatos relevantes para cada animal (puedes agregar batchId o info de lotes si quieres relacionarlo con GanadoToken).

✅ Funciones CRUD coinciden con endpoints /backend/routes/animals.ts.

✅ Roles y control de acceso listos (DAO_ROLE y MINTER_ROLE si se requiere).

GanadoRegistryUpgradeable.sol (modificado para backend CRUD)

✅ Almacena registros de operaciones del ganado.

✅ CRUD completo para lotes /batches y animales /registry.

✅ Interactúa con GanadoToken y AnimalNFT si necesitas.

✅ Funciones para obtener información de registros listas para los endpoints Express.

✅ Control de acceso con roles, pausado y upgradeable.

Explicación:

Productores crean tokens y NFTs de animales/lotes y envían datos crudos al backend.

Veterinarios y frigoríficos actualizan datos autorizados.

Backend calcula hashes y los guarda en GanadoRegistryUpgradeable.

Safe Multisig controla todas las operaciones críticas (mint de tokens, transferencias, updates).

Consumidores finales acceden solo a datos de trazabilidad vía QR.

```mermaid
flowchart LR
    %% Producción
    subgraph Producción
        P1[Productor] 
        P1 -->|"1. mintAnimal con PRODUCER_ROLE"| NFT[AnimalNFTUpgradeable]
        P1 -->|"2. mintBatch / transferBatch con MINTER_ROLE"| ERC20[GanadoTokenUpgradeable]
        P1 -->|"3. registrarAnimal / registrarLote en Backend CRUD"| Backend[Backend CRUD]
    end

    %% Salud
    subgraph Salud
        Vet[Veterinario] -->|"4. registrarVacuna / registrarTratamiento con VET_ROLE"| Backend
    end

    %% Procesamiento
    subgraph Procesamiento
        Frio[Frigorífico] -->|"5. registrarCorte / registrarQR con FRIGORIFICO_ROLE"| Backend
    end

    %% Auditoría
    subgraph Auditoria
        Auditor[Auditor] -->|"6. consultarRegistros con AUDITOR_ROLE"| Registry[GanadoRegistryUpgradeable]
    end

    %% Interacción con Registry
    Backend -->|"7. hashAnimal / hashLote -> updateRegistry usando DAO_ROLE"| Registry
    ERC20 -->|"8. mintByDAO / mintByMinter -> updateRegistry"| Registry
    NFT -->|"9. mintAnimal / transferAnimal -> updateRegistry usando DAO_ROLE / UPGRADER_ROLE"| Registry

    %% Pausa y Upgrade
    subgraph Control
        Admin[Admin / DAO_ROLE] 
        Admin -->|"10. pause / unpause con PAUSER_ROLE"| ERC20
        Admin -->|"11. pause / unpause con PAUSER_ROLE"| NFT
        Admin -->|"12. upgradeTo con UPGRADER_ROLE"| ERC20
        Admin -->|"13. upgradeTo con UPGRADER_ROLE"| NFT
        Admin -->|"14. upgradeTo con UPGRADER_ROLE"| Registry
    end

    %% Safe Multisig
    subgraph SafeMultisig
        Safe[Safe Multisig]
        ERC20 -.->|"15. mintByDAO / transferBatch aprobadas"| Safe
        NFT -.->|"16. mintAnimal / transferAnimal aprobadas"| Safe
        Registry -.->|"17. updateRegistry aprobadas"| Safe
        Backend -.->|"18. acciones críticas aprobadas"| Safe
        Admin -.->|"19. pause / upgrade críticas aprobadas"| Safe
    end

    %% Consumidor
    subgraph Consumidor
        QR[QR Corte] -->|"20. consultaTrazabilidad"| Frontend[Frontend]
        Frontend -->|"21. solicita datos"| Registry
        Frontend -->|"22. solicita datos"| Backend
    end

    %% Roles y estilo
    classDef dao fill:#f9f,stroke:#333,stroke-width:2px;
    classDef minter fill:#9f9,stroke:#333,stroke-width:2px;
    classDef producer fill:#ff9,stroke:#333,stroke-width:2px;
    classDef vet fill:#9ff,stroke:#333,stroke-width:2px;
    classDef frigorifico fill:#f9c,stroke:#333,stroke-width:2px;
    classDef auditor fill:#ccc,stroke:#333,stroke-width:2px;
    classDef admin fill:#fc9,stroke:#333,stroke-width:2px;

    class ERC20,NFT,Registry dao;
    class ERC20 minter;
    class P1 producer;
    class Vet vet;
    class Frio frigorifico;
    class Auditor auditor;
    class Admin admin;

