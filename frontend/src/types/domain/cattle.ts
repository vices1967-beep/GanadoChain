// src/types/domain/cattle.ts
export interface Animal {
  id: number;
  ear_tag: string;
  name: string;
  breed: string;
  birth_date: string;
  gender: 'M' | 'F';
  weight: number;
  health_status: 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR' | 'CRITICAL';
  status: 'ACTIVE' | 'SOLD' | 'DECEASED' | 'QUARANTINED';
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
}

export interface Batch {
  id: number;
  name: string;
  description: string;
  animals: number[];
  created_by: number;
  status: string;
  on_blockchain: boolean;
  created_at: string;
  updated_at: string;
}

export interface CertificationStandard {
  id: number;
  name: string;
  description: string;
  requirements: string[];
  validity_period: number;
  is_active: boolean;
  created_at: string;
}

export interface AnimalCertification {
  id: number;
  animal: number;
  standard: number;
  certification_date: string;
  expiration_date: string;
  certifying_body: string;
  certificate_number: string;
  documents: string[];
  status: 'ACTIVE' | 'EXPIRED' | 'REVOKED';
  revoked: boolean;
  revocation_reason?: string;
  created_at: string;
}

export interface AnimalCreateRequest {
  ear_tag: string;
  name: string;
  breed: string;
  birth_date: string;
  gender: 'M' | 'F';
  weight: number;
  health_status: 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR' | 'CRITICAL';
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

// Añadir al final de src/types/domain/cattle.ts
export interface CertificationCreateRequest {
  animal: number;
  standard: number;
  certification_date: string;
  certifying_body: string;
  certificate_number: string;
  documents?: string[];
}

export interface CertificationUpdateRequest extends Partial<CertificationCreateRequest> {
  id: number;
}