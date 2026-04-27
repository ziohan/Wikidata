import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class LastQueriesService {

  private http = inject(HttpClient);
  private base = 'http://127.0.0.1:8000';

  getQueries(filters: any) {
    const params: any = {
      page: filters.page,
      page_size: filters.page_size
    };

    if (filters.search) params.search = filters.search;
    if (filters.favorite) params.favorite = true;
    if (filters.start_date) params.start_date = filters.start_date;
    if (filters.end_date) params.end_date = filters.end_date;

    return this.http.get<any>(`${this.base}/last-queries`, { params });
  }

  toggleFavorite(id: string) {
    return this.http.patch(`${this.base}/queries/${id}/favorite`, {});
  }

  deleteQuery(id: string) {
    return this.http.delete(`${this.base}/queries/${id}`);
  }
}