import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class Search_Entities {
  private http = inject(HttpClient);
  private base = 'http://127.0.0.1:8000';
  getEntities(filters: any) {
    const params: any = {
      page: filters.page,
      page_size: filters.page_size,
      sort_by: filters.sort_by || 'occurrences',
      order: filters.order || 'desc'
    };

    if (filters.search) params.search = filters.search;
    if (filters.favorite) params.favorite = true;
    return this.http.get<any>(`${this.base}/search-entities`, { params });
  
  }
  toggleFavorite(qid: string) {
    return this.http.patch<any>(`${this.base}/entities/${qid}/favorite`, {});
  }
}