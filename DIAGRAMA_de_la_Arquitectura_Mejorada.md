









```mermaid
graph TD
    A[Usuario] --> B[Animales]
    A --> C[Lotes]
    A --> D[Dispositivos IoT]
    
    B --> E[Registros de Salud]
    B --> F[Eventos Blockchain]
    
    D --> G[Datos GPS]
    D --> H[Datos de Salud]
    D --> I[Eventos IoT]
    
    F --> J[Contratos Inteligentes]
    J --> K[Blockchain Polygon]
    
    L[Sistema de Notificaciones] --> A
    M[Sistema de Reputación] --> A
    N[Auditoría y Trazabilidad] --> B
    N --> C
    N --> D
    
    O[Dashboard] --> P[Métricas del Sistema]
    
    style J fill:#e1f5fe
    style K fill:#f3e5f5
    style L fill:#fff3e0
    style M fill:#e8f5e9
    style N fill:#fce4ec