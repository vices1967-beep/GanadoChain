export interface BaseUser {
  id: number;
  name: string;
  email: string;
  walletAddress?: string;
  createdAt: Date;
  updatedAt: Date;
}