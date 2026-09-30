import { Injectable } from '@nestjs/common';
// Use dynamic import or loose typing if meilisearch isn't in package.json yet
// import { MeiliSearch } from 'meilisearch';

@Injectable()
export class SearchService {
  private client: any; // MeiliSearch client

  constructor() {
    try {
      const { MeiliSearch } = require('meilisearch');
      this.client = new MeiliSearch({
        host: process.env.MEILISEARCH_HOST || 'http://localhost:7700',
        apiKey: process.env.MEILISEARCH_API_KEY,
      });
    } catch (e) {
      // Meilisearch not installed yet, gracefully fallback
    }
  }


  async search(query: string, page: number, limit: number) {
    const offset = (page - 1) * limit;
    
    if (!this.client) return { hits: [], total: 0 };

    try {
      const index = this.client.index('opportunities');
      const results = await index.search(query, {
        limit,
        offset,
      });
      return results;
    } catch (e) {
      console.warn("Meilisearch not ready or index missing", e);
      return { hits: [], total: 0 };
    }
  }

  async syncOpportunityToIndex(opportunity: any) {
    if (!this.client) return;
    const index = this.client.index('opportunities');
    await index.addDocuments([opportunity]);
  }
}
