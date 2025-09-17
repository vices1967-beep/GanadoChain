import { BaseUser } from './common';

export interface ProducerUser extends BaseUser {
  role: 'producer';
  farmName: string;
  location: string;
  cattleCount: number;
}