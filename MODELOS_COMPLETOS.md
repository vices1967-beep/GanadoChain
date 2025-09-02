1. Descripción de clases y actores
Producción

Productor (P1)

Actor humano con PRODUCER_ROLE.

Registra animales individualmente (NFTs) y lotes (ERC20) en la blockchain.

También interactúa con el backend para CRUD de animales y lotes.

Responsable de la trazabilidad inicial.

AnimalNFTUpgradeable (NFT)

Smart contract que representa cada animal con un NFT único.

Permite mint, transferencia y actualización de estado.

Controlado por roles como PRODUCER_ROLE, DAO_ROLE, UPGRADER_ROLE.

GanadoTokenUpgradeable (ERC20)

Smart contract tipo ERC20 para representar lotes de ganado.

Soporta emisión (mintBatch) y transferencias en grupo.

Administrado por MINTER_ROLE y DAO_ROLE.

Backend CRUD

Aplicación fuera de la blockchain.

Guarda registros administrativos (animales, lotes, vacunas, cortes, etc.).

Se sincroniza con la blockchain vía updateRegistry.

IoT y Sensores

Caravanas Inteligentes / Sensores IoT

Dispositivos físicos que generan datos en tiempo real: ubicación, temperatura, movimiento.

Reportan alertas tempranas (ej. enfermedades).

Envían datos al Backend y pueden actualizar la blockchain con IOT_ROLE.

GanadoRegistryUpgradeable (Registry)

Smart contract que guarda los hashes de trazabilidad.

Recibe actualizaciones del Backend, IoT y otros actores mediante distintos roles (DAO_ROLE, IOT_ROLE, VET_ROLE, etc.).

Salud

Veterinario (Vet)

Actor con VET_ROLE.

Registra tratamientos, vacunas y diagnósticos en el Backend.

Estos datos se sincronizan al Registry para garantizar trazabilidad sanitaria.

Procesamiento

Frigorífico (Frio)

Actor con FRIGORIFICO_ROLE.

Registra cortes, empaques y genera QR de trazabilidad.

Todo se sube al Backend y se vincula al Registry.

Auditoría

Auditor

Actor con AUDITOR_ROLE.

Solo puede consultar registros en el Registry, sin modificarlos.

Función clave para transparencia e inspecciones regulatorias.

Control y Gobernanza

Admin / DAO

Usuario con DAO_ROLE y privilegios especiales.

Puede pausar contratos (PAUSER_ROLE) o actualizarlos (UPGRADER_ROLE).

Gestiona upgrades y asegura continuidad del sistema.

Safe Multisig

Bóveda de seguridad (multifirma).

Todas las operaciones críticas (mint, transferencias, upgrades, actualizaciones) pasan por aprobación multisig.

Evita acciones unilaterales riesgosas.

Consumidor Final

QR de Corte

Código QR generado en el proceso de faena.

El consumidor lo escanea para ver la trazabilidad del producto.

Frontend

Aplicación web/móvil para consumidores.

Consulta datos tanto en el Registry (on-chain) como en el Backend (off-chain).


```mermaid
erDiagram
    %% ======================================================
    %% USERS (users/models.py)
    %% ======================================================
    USER {
        bigint id PK
        string username UK
        string email UK
        string password
        boolean is_active
        datetime date_joined
    }

    USERACTIVITYLOG {
        bigint id PK
        bigint user_id FK
        string action
        text details
        string ip_address
        datetime timestamp
    }

    USERPREFERENCE {
        bigint id PK
        bigint user_id FK
        boolean email_notifications
        boolean push_notifications
        string language
    }

    APITOKEN {
        bigint id PK
        bigint user_id FK
        string name
        string key UK
        datetime created_at
        datetime expires_at
        boolean is_active
    }

    %% ======================================================
    %% USERS/REPUTATION (users/reputation_models.py)
    %% ======================================================
    USERROLE {
        bigint id PK
        bigint user_id FK
        string role_type
        string scope_type
        string scope_id
        bigint granted_by FK
        datetime granted_at
        datetime expires_at
        boolean is_active
    }

    REPUTATIONSCORE {
        bigint id PK
        bigint user_id FK
        string reputation_type
        decimal score
        int total_actions
        int positive_actions
        datetime last_calculated
        json metrics
    }

    %% ======================================================
    %% USERS/NOTIFICATIONS (users/notification_models.py)
    %% ======================================================
    NOTIFICATION {
        bigint id PK
        bigint user_id FK
        string notification_type
        string title
        text message
        string related_object_id
        string related_content_type
        boolean is_read
        string priority
        datetime created_at
    }

    %% ======================================================
    %% CATTLE (cattle/models.py)
    %% ======================================================
    ANIMAL {
        bigint id PK
        string ear_tag UK
        string breed
        date birth_date
        string sex
        string status
        datetime created_at
        datetime updated_at
    }

    ANIMALHEALTHRECORD {
        bigint id PK
        bigint animal_id FK
        string health_status
        string treatment
        string veterinarian
        datetime recorded_at
    }

    BATCH {
        bigint id PK
        string name
        string description
        datetime created_at
    }

    %% ======================================================
    %% CATTLE/BLOCKCHAIN (cattle/blockchain_models.py)
    %% ======================================================
    BLOCKCHAINEVENTSTATE {
        bigint id PK
        bigint event_id FK UK
        string state
        int confirmation_blocks
        bigint block_confirmed
        datetime created_at
        datetime updated_at
    }

    %% ======================================================
    %% CATTLE/AUDIT (cattle/audit_models.py)
    %% ======================================================
    CATTLEAUDITTRAIL {
        bigint id PK
        string object_type
        string object_id
        string action_type
        bigint user_id FK
        json previous_state
        json new_state
        json changes
        string ip_address
        string blockchain_tx_hash
        datetime timestamp
    }

    %% ======================================================
    %% IOT (iot/models.py)
    %% ======================================================
    IOTDEVICE {
        bigint id PK
        string device_id UK
        string device_type
        string status
        datetime registered_at
    }

    GPSDATA {
        bigint id PK
        bigint device_id FK
        float latitude
        float longitude
        datetime timestamp
    }

    HEALTHSENSORDATA {
        bigint id PK
        bigint device_id FK
        float temperature
        float heart_rate
        float movement
        datetime timestamp
    }

    DEVICEEVENT {
        bigint id PK
        bigint device_id FK
        string event_type
        json payload
        datetime timestamp
    }

    DEVICECONFIGURATION {
        bigint id PK
        bigint device_id FK UK
        int sampling_interval
        int transmission_power
        float battery_threshold
        datetime updated_at
    }

    %% ======================================================
    %% IOT/ANALYTICS (iot/analytics_models.py)
    %% ======================================================
    DEVICEANALYTICS {
        bigint id PK
        bigint device_id FK
        date date
        int total_readings
        float avg_battery_level
        float connectivity_uptime
        float data_quality_score
        int alerts_triggered
        datetime created_at
    }

    %% ======================================================
    %% BLOCKCHAIN (blockchain/models.py)
    %% ======================================================
    BLOCKCHAINEVENT {
        bigint id PK
        string event_type
        string transaction_hash
        datetime block_timestamp
    }

    CONTRACTINTERACTION {
        bigint id PK
        string contract_type
        string method
        json parameters
        datetime called_at
    }

    NETWORKSTATE {
        bigint id PK
        string network_name
        int chain_id
        boolean is_active
        datetime updated_at
    }

    SMARTCONTRACT {
        bigint id PK
        string name
        string address
        string version
    }

    GASPRICEHISTORY {
        bigint id PK
        int gas_price
        datetime timestamp
    }

    TRANSACTIONPOOL {
        bigint id PK
        string transaction_hash UK
        string status
        datetime created_at
    }

    %% ======================================================
    %% CORE/METRICS (core/metrics_models.py)
    %% ======================================================
    SYSTEMMETRICS {
        bigint id PK
        date date UK
        int total_animals
        int total_users
        int total_transactions
        int active_devices
        float average_gas_price
        int blockchain_events
        int health_alerts
        int producer_count
        int vet_count
        int frigorifico_count
        int auditor_count
        float avg_response_time
        float error_rate
        float system_uptime
        datetime created_at
    }

    %% ======================================================
    %% RELACIONES
    %% ======================================================
    USER ||--o{ USERACTIVITYLOG : performs
    USER ||--|| USERPREFERENCE : has
    USER ||--o{ APITOKEN : has
    USER ||--o{ USERROLE : has_roles
    USER ||--o{ REPUTATIONSCORE : reputation
    USER ||--o{ NOTIFICATION : notified
    USER ||--o{ CATTLEAUDITTRAIL : actions

    ANIMAL ||--o{ ANIMALHEALTHRECORD : health
    ANIMAL }o--o{ BATCH : grouped
    ANIMAL ||--o{ IOTDEVICE : monitored

    IOTDEVICE ||--o{ GPSDATA : generates
    IOTDEVICE ||--o{ HEALTHSENSORDATA : generates
    IOTDEVICE ||--o{ DEVICEEVENT : events
    IOTDEVICE ||--|| DEVICECONFIGURATION : configured
    IOTDEVICE ||--o{ DEVICEANALYTICS : metrics

    BLOCKCHAINEVENT ||--|| BLOCKCHAINEVENTSTATE : state
    CONTRACTINTERACTION }|--|| SMARTCONTRACT : interacts

    %% ======================================================
    %% ESTILOS POR ARCHIVO
    %% ======================================================
    classDef users fill:#cce5ff,stroke:#004085,stroke-width:2px;
    classDef reputation fill:#b3e6cc,stroke:#006644,stroke-width:2px;
    classDef notifications fill:#ffe6cc,stroke:#b36b00,stroke-width:2px;
    classDef cattle fill:#e6ffe6,stroke:#267326,stroke-width:2px;
    classDef cattle_blockchain fill:#ffd6cc,stroke:#b32400,stroke-width:2px;
    classDef cattle_audit fill:#f2ccff,stroke:#7300b3,stroke-width:2px;
    classDef iot fill:#ffffcc,stroke:#999900,stroke-width:2px;
    classDef iot_analytics fill:#d9f2ff,stroke:#005580,stroke-width:2px;
    classDef blockchain fill:#ffcccc,stroke:#990000,stroke-width:2px;
    classDef core fill:#e2e3e5,stroke:#383d41,stroke-width:2px;

    class USER,USERACTIVITYLOG,USERPREFERENCE,APITOKEN users;
    class USERROLE,REPUTATIONSCORE reputation;
    class NOTIFICATION notifications;
    class ANIMAL,ANIMALHEALTHRECORD,BATCH cattle;
    class BLOCKCHAINEVENTSTATE cattle_blockchain;
    class CATTLEAUDITTRAIL cattle_audit;
    class IOTDEVICE,GPSDATA,HEALTHSENSORDATA,DEVICEEVENT,DEVICECONFIGURATION iot;
    class DEVICEANALYTICS iot_analytics;
    class BLOCKCHAINEVENT,CONTRACTINTERACTION,NETWORKSTATE,SMARTCONTRACT,GASPRICEHISTORY,TRANSACTIONPOOL blockchain;
    class SYSTEMMETRICS core;


```
2. Diagrama simplificado para presentación

```mermaid
flowchart LR
    %% Bloques principales
    subgraph Producción
        P1[Productor] --> NFT[AnimalNFT]
        P1 --> ERC20[GanadoToken]
        P1 --> Backend[Backend CRUD]
    end

    subgraph IoT
        IoT[Sensores IoT] --> Backend
        IoT --> Registry[Registry]
    end

    subgraph Salud
        Vet[Veterinario] --> Backend
    end

    subgraph Procesamiento
        Frio[Frigorífico] --> Backend
    end

    subgraph Auditoría
        Auditor[Auditor] --> Registry
    end

    subgraph Control
        Admin[DAO / Admin] -->|Gobernanza| Registry
        Admin -->|Pausar / Upgrade| NFT
        Admin --> ERC20
    end

    subgraph Safe
        Safe[Safe Multisig] -->|Aprueba operaciones| Admin
        Safe --> Registry
        Safe --> NFT
        Safe --> ERC20
    end

    subgraph Consumidor
        QR[QR Corte] --> Frontend[Frontend]
        Frontend --> Registry
        Frontend --> Backend
    end
