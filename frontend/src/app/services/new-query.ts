import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})

export class NewQueryService {
  private http = inject(HttpClient);

  sendQuery(data: any) {
    return this.http.post<any>(
      'http://127.0.0.1:8000/new-query',
      data
    );
  }
}