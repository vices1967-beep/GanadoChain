Relaciones Principales

    Usuario-Animal: Un usuario puede tener múltiples animales (relación de propiedad)

    Animal-Registros de Salud: Un animal puede tener múltiples registros de salud

    Dispositivo IoT-Datos: Un dispositivo puede generar múltiples datos GPS y de salud

    Lote-Animales: Un lote puede contener múltiples animales (relación muchos-a-muchos)

    Eventos Blockchain-Animales/Lotes: Los eventos blockchain pueden referenciar animales o lotes

    Interacciones con Contratos: Registran todas las operaciones con contratos inteligentes

Características Blockchain

    Tokens NFT: Cada animal tiene un token NFT único con metadatos en IPFS

    Eventos: Registro inmutable de todas las operaciones en la blockchain

    Roles: Sistema de permisos basado en roles en contratos inteligentes

    Trazabilidad: Historial completo desde el nacimiento hasta el consumidor final

Este diagrama muestra la estructura completa del sistema de trazabilidad con integración blockchain, incluyendo los modelos de usuarios, ganado, dispositivos IoT y todos los componentes blockchain.

```mermaid
erDiagram
    USER ||--o{ ANIMAL : owns
    USER ||--o{ BATCH : creates
    USER ||--o{ IOT_DEVICE : owns
    USER ||--o{ USER_ACTIVITY_LOG : performs
    USER ||--|| USER_PREFERENCE : has
    USER ||--o{ API_TOKEN : has
    
    ANIMAL ||--o{ ANIMAL_HEALTH_RECORD : has
    ANIMAL ||--o{ IOT_DEVICE : monitored_by
    ANIMAL ||--o{ GPS_DATA : has
    ANIMAL ||--o{ HEALTH_SENSOR_DATA : has
    ANIMAL }o--o{ BATCH : belongs_to
    
    IOT_DEVICE ||--o{ GPS_DATA : generates
    IOT_DEVICE ||--o{ HEALTH_SENSOR_DATA : generates
    IOT_DEVICE ||--o{ DEVICE_EVENT : generates
    IOT_DEVICE ||--|| DEVICE_CONFIGURATION : configured_by
    
    BLOCKCHAIN_EVENT }|--|| ANIMAL : references
    BLOCKCHAIN_EVENT }|--|| BATCH : references
    
    CONTRACT_INTERACTION }|--|| SMART_CONTRACT : interacts_with
    
    USER {
        bigint id PK
        string username
        string email
        string wallet_address
        string role
        json blockchain_roles
        boolean is_verified
        boolean is_blockchain_active
        datetime created_at
        datetime updated_at
    }
    
    USER_ACTIVITY_LOG {
        bigint id PK
        bigint user_id FK
        string action
        string ip_address
        text user_agent
        json metadata
        string blockchain_tx_hash
        datetime timestamp
    }
    
    USER_PREFERENCE {
        bigint id PK
        bigint user_id FK
        boolean email_notifications
        boolean push_notifications
        string language
        string theme
        integer animals_per_page
        boolean enable_animations
        datetime created_at
        datetime updated_at
    }
    
    API_TOKEN {
        bigint id PK
        bigint user_id FK
        string name
        string token
        string token_type
        boolean is_active
        datetime expires_at
        datetime last_used
        datetime created_at
    }
    
    ANIMAL {
        bigint id PK
        string ear_tag
        string breed
        date birth_date
        decimal weight
        string health_status
        string location
        bigint owner_id FK
        string ipfs_hash
        bigint token_id
        string mint_transaction_hash
        string nft_owner_wallet
        datetime created_at
        datetime updated_at
    }
    
    ANIMAL_HEALTH_RECORD {
        bigint id PK
        bigint animal_id FK
        string health_status
        string source
        bigint veterinarian_id FK
        string iot_device_id
        text notes
        decimal temperature
        integer heart_rate
        decimal movement_activity
        string ipfs_hash
        string transaction_hash
        string blockchain_hash
        datetime created_at
    }
    
    BATCH {
        bigint id PK
        string name
        string origin
        string destination
        string status
        string ipfs_hash
        string blockchain_tx
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    
    IOT_DEVICE {
        bigint id PK
        string device_id
        string device_type
        string name
        string description
        string status
        bigint animal_id FK
        bigint owner_id FK
        string firmware_version
        integer battery_level
        datetime last_reading
        string location
        string ip_address
        string mac_address
        datetime created_at
        datetime updated_at
    }
    
    GPS_DATA {
        bigint id PK
        bigint device_id FK
        bigint animal_id FK
        decimal latitude
        decimal longitude
        decimal altitude
        decimal accuracy
        decimal speed
        decimal heading
        integer satellites
        decimal hdop
        datetime timestamp
        datetime recorded_at
        string blockchain_hash
    }
    
    HEALTH_SENSOR_DATA {
        bigint id PK
        bigint device_id FK
        bigint animal_id FK
        integer heart_rate
        decimal temperature
        decimal movement_activity
        integer rumination_time
        decimal feeding_activity
        integer respiratory_rate
        string posture
        decimal ambient_temperature
        decimal humidity
        datetime timestamp
        datetime recorded_at
        string blockchain_hash
        boolean processed
        boolean health_alert
    }
    
    DEVICE_EVENT {
        bigint id PK
        bigint device_id FK
        string event_type
        string severity
        text message
        json data
        boolean resolved
        datetime resolved_at
        bigint resolved_by_id FK
        datetime timestamp
        datetime created_at
    }
    
    DEVICE_CONFIGURATION {
        bigint id PK
        bigint device_id FK
        integer sampling_interval
        integer data_retention
        json alert_thresholds
        boolean gps_enabled
        boolean health_monitoring
        boolean low_power_mode
        boolean firmware_auto_update
        datetime created_at
        datetime updated_at
    }
    
    BLOCKCHAIN_EVENT {
        bigint id PK
        string event_type
        string transaction_hash
        bigint block_number
        bigint animal_id FK
        bigint batch_id FK
        string from_address
        string to_address
        json metadata
        datetime created_at
    }
    
    CONTRACT_INTERACTION {
        bigint id PK
        string contract_type
        string action_type
        string transaction_hash
        bigint block_number
        string caller_address
        string target_address
        json parameters
        bigint gas_used
        bigint gas_price
        string status
        text error_message
        datetime created_at
        datetime updated_at
    }
    
    NETWORK_STATE {
        bigint id PK
        bigint last_block_number
        datetime last_sync_time
        bigint average_gas_price
        integer active_nodes
        integer chain_id
        boolean sync_enabled
        datetime created_at
        string network_name
        string rpc_url
        float block_time
        string native_currency
        boolean is_testnet
    }
    
    SMART_CONTRACT {
        bigint id PK
        string name
        string contract_type
        string address
        json abi
        string version
        boolean is_active
        bigint deployment_block
        string deployment_tx_hash
        string deployer_address
        datetime created_at
        datetime updated_at
        string implementation_address
        string proxy_address
        boolean is_upgradeable
        string admin_address
    }
    
    GAS_PRICE_HISTORY {
        bigint id PK
        bigint gas_price
        float gas_price_gwei
        bigint block_number
        datetime timestamp
    }
    
    TRANSACTION_POOL {
        bigint id PK
        string transaction_hash
        text raw_transaction
        string status
        integer retry_count
        datetime last_retry
        datetime created_at
        datetime updated_at
    }