import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})

export class NewQueryService {
  private http = inject(HttpClient);
  sendQuery(data: any, file: File | null) {
    const formData = new FormData();
    formData.append('hops', data.hops);
    formData.append('top_n', data.top_n);

    if (file) {
      formData.append('file', file);
    }

    return this.http.post<any>(
      'http://127.0.0.1:8000/new-query',
      formData
    );
  }
}