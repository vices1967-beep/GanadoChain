// src/types/domain/cattle.ts

// HealthStatus alineado con backend Django
export type HealthStatus = 
  | 'HEALTHY' 
  | 'SICK' 
  | 'RECOVERING' 
  | 'UNDER_OBSERVATION' 
  | 'QUARANTINED';

// AnimalStatus alineado con backend
export type AnimalStatus = 
  | 'ACTIVE' 
  | 'SOLD' 
  | 'DECEASED' 
  | 'QUARANTINED';

export interface Animal {
  id: number;
  ear_tag: string;
  name: string;
  breed: string;
  birth_date: string;
  gender: 'M' | 'F';
  weight: number;
  health_status: HealthStatus;
  status: AnimalStatus;
  location: string;
  owner: number;
  mother?: number;
  father?: number;
  token_id?: string;
  blockchain_token_id?: string;
  ipfs_hash?: string;
  nft_owner_wallet?: string;
  mint_transaction_hash?: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
  batches?: number[];
  on_blockchain?: boolean;
  current_batch?: number; // Añadido para alinear con backend
}

export interface AnimalHealthRecord {
  id: number;
  animal: number;
  veterinarian?: number;
  examination_date: string;
  diagnosis: string;
  treatment: string;
  medication: string;
  notes: string;
  temperature?: number;
  heart_rate?: number;
  respiratory_rate?: number;
  weight?: number;
  source: 'FARMER' | 'VETERINARIAN' | 'IOT' | 'SYSTEM';
  iot_device?: string;
  created_at: string;
  ipfs_hash?: string; // Añadido para alinear con backend
  transaction_hash?: string; // Añadido para alinear con backend
  blockchain_hash?: string; // Añadido para alinear con backend
}

export interface Batch {
  id: number;
  name: string;
  description: string;
  animals: number[];
  origin: string; // Añadido para alinear con backend
  destination: string; // Añadido para alinear con backend
  status: string;
  created_by: number;
  on_blockchain: boolean;
  ipfs_hash?: string; // Añadido para alinear con backend
  blockchain_tx?: string; // Añadido para alinear con backend
  created_at: string;
  updated_at: string;
}

export interface CertificationStandard {
  id: number;
  name: string;
  description: string;
  issuing_authority: string; // Cambiado de requirements a issuing_authority
  validity_days: number; // Cambiado de validity_period
  requirements?: string[]; // Mantenido por compatibilidad
  is_active: boolean;
  created_at: string;
  updated_at: string; // Añadido para alinear con backend
}

export interface AnimalCertification {
  id: number;
  animal: number;
  standard: number;
  certification_date: string;
  expiration_date: string;
  certifying_authority: string; // Cambiado de certifying_body
  certificate_number: string;
  evidence?: Record<string, any>; // Cambiado de documents
  documents?: string[]; // Mantenido por compatibilidad
  status: 'ACTIVE' | 'EXPIRED' | 'REVOKED';
  revoked: boolean;
  revocation_reason?: string;
  blockchain_hash?: string; // Añadido para alinear con backend
  created_at: string;
  updated_at: string; // Añadido para alinear con backend
}

export interface AnimalCreateRequest {
  ear_tag: string;
  name: string;
  breed: string;
  birth_date: string;
  gender: 'M' | 'F';
  weight: number;
  health_status: HealthStatus;
  location: string;
  owner?: number;
  mother?: number;
  father?: number;
  metadata?: Record<string, any>;
}

export interface AnimalUpdateRequest extends Partial<AnimalCreateRequest> {
  id: number;
}

export interface AnimalSearchParams {
  ear_tag?: string;
  breed?: string;
  health_status?: string;
  minted?: 'true' | 'false';
  batch_id?: number;
  page?: number;
  page_size?: number;
}

export interface AnimalMintRequest {
  wallet_address: string;
  operational_ipfs?: string;
}

export interface AnimalTransferRequest {
  new_owner_wallet: string;
  notes?: string;
}

export interface AnimalHealthUpdateRequest {
  new_health_status: string;
  notes?: string;
  temperature?: number;
  heart_rate?: number;
}

export interface BatchCreateRequest {
  name: string;
  description: string;
  animals: number[];
  origin?: string; // Añadido para alinear con backend
  destination?: string; // Añadido para alinear con backend
  status?: string;
}

export interface BatchStatusUpdateRequest {
  new_status: string;
  notes?: string;
}

export interface BatchAnimalsUpdateRequest {
  animal_ids: number[];
}

export interface CattleStats {
  total_animals: number;
  minted_animals: number;
  total_batches: number;
  animals_by_health_status: Record<string, number>;
  batches_by_status: Record<string, number>;
  animals_by_breed: Record<string, number>;
}

export interface BlockchainEvent {
  id: number;
  event_type: string;
  transaction_hash: string;
  block_number: number;
  status: 'PENDING' | 'CONFIRMED' | 'FAILED';
  created_at: string;
}

export interface AuditTrail {
  id: number;
  user: number;
  username: string;
  object_type: string;
  object_id: string;
  action_type: string;
  ip_address: string;
  user_agent?: string;
  blockchain_tx_hash?: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface AuditExportRequest {
  format: 'json' | 'csv';
  days?: number;
  object_type?: string;
  object_id?: string;
  action_type?: string;
}

export interface AuditStats {
  total_actions: number;
  actions_by_type: Record<string, number>;
  actions_by_user: Record<string, number>;
  recent_activity: AuditTrail[];
}

export interface NFTVerification {
  exists: boolean;
  owner_matches: boolean;
  metadata_valid: boolean;
  token_id: string;
  owner: string;
}

export interface NFTInfo {
  token_id: string;
  owner: string;
  token_uri: string;
  metadata: Record<string, any>;
  created_at: string;
}

export interface CertificationCreateRequest {
  animal: number;
  standard: number;
  certification_date: string;
  certifying_authority: string; // Cambiado de certifying_body
  certificate_number: string;
  evidence?: Record<string, any>; // Cambiado de documents
  documents?: string[]; // Mantenido por compatibilidad
}

export interface CertificationUpdateRequest extends Partial<CertificationCreateRequest> {
  id: number;
}

// Nuevos tipos para alinear completamente con backend
export interface BatchStatus {
  CREATED: 'Creado';
  IN_TRANSIT: 'En Tránsito';
  DELIVERED: 'Entregado';
  CANCELLED: 'Cancelado';
  PROCESSING: 'Procesando';
  QUALITY_CHECK: 'Control de Calidad';
}

export interface HealthRecordSource {
  VETERINARIAN: 'Veterinario';
  IOT_SENSOR: 'Sensor IoT';
  FARMER: 'Granjero';
  SYSTEM: 'Sistema Automático';
}

// Tipos para respuestas de API
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Tipos para operaciones blockchain
export interface MintResult {
  success: boolean;
  message: string;
  animal_id: number;
  ear_tag: string;
  token_id?: string;
  transaction_hash?: string;
  owner_wallet?: string;
  nft_owner_wallet?: string;
  mint_transaction_hash?: string;
  error?: string;
}

export interface TransferResult {
  success: boolean;
  message: string;
  transaction_hash?: string;
  error?: string;
}

export interface HealthUpdateResult {
  success: boolean;
  message: string;
  health_record_id?: number;
  error?: string;
}