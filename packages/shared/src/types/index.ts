export type ID = string;

export interface User {
  id: ID;
  email: string;
  fullName: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Company {
  id: ID;
  name: string;
  website: string;
  careersUrl: string;
  industry: string;
}

export interface Opportunity {
  id: ID;
  companyId: ID;
  title: string;
  location: string;
  applyUrl: string;
}
