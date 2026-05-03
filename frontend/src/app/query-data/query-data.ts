import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-query-data',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './query-data.html',
  styleUrl: './query-data.scss'
})
export class QueryData {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private http = inject(HttpClient);
  title = signal('');
  graph = signal('');
  pdf = signal('');
  groupedTriples = signal<any>({});
  queryId = '';

  constructor() {
    this.queryId = this.route.snapshot.paramMap.get('id') || '';
    if (!this.queryId) return;
    this.load();
  }

  load() {
    this.http.get<any>(
      `http://127.0.0.1:8000/query-generated/${this.queryId}`
    ).subscribe(res => {
      this.title.set(res.title);
      this.graph.set(`http://127.0.0.1:8000${res.image_url}`);
      this.pdf.set(`http://127.0.0.1:8000${res.download_pdf}`);
      this.groupedTriples.set(res.grouped_triples);
    });
  }

  downloadTriples() {
    let content = '';
    const grouped = this.groupedTriples();
    for (const entity in grouped) {
      content += `${entity}:\n`;
      grouped[entity].forEach((t: any) => {
        content += `${t.triple}\n`;
      });
      content += '\n';
    }
    const blob = new Blob([content], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'triples.txt';
    a.click();
  }
  back() {
    this.router.navigate(['/last-queries']);
  }
}