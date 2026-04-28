import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';


@Component({
  selector: 'app-top-queries',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './top-queries.html',
  styleUrl: './top-queries.scss'
})

export class TopQueries {
  private http = inject(HttpClient);
  private base = 'http://127.0.0.1:8000';
  subjects = signal<any[]>([]);
  predicates = signal<any[]>([]);
  triplets = signal<any[]>([]);

  ngOnInit() {
    this.load();
  }

  load() {
    this.http.get<any[]>(`${this.base}/top-subjects`)
      .subscribe(r => this.subjects.set(r));
    this.http.get<any[]>(`${this.base}/top-predicates`)
      .subscribe(r => this.predicates.set(r));
    this.http.get<any[]>(`${this.base}/top-triplets`)
      .subscribe(r => this.triplets.set(r));
  }

  goQuery(id: string) {
    window.location.href = `/query/${id}`;
  }
}