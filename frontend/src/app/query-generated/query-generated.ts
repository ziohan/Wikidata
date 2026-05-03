import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-query-generated',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './query-generated.html',
  styleUrl: './query-generated.scss'
})
export class QueryGenerated {
  private router = inject(Router);
  private http = inject(HttpClient);
  title = signal('');
  graph = signal('');
  pdf = signal('');
  groupedTriples = signal<any>({});

  constructor() {
    const queryId = history.state?.query_id;
    if (!queryId) {
      console.error("query_id não encontrado");
      return;
    }
    this.http.get<any>(`http://127.0.0.1:8000/query-generated/${queryId}`)
      .subscribe(res => {
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

  next() {
    this.router.navigate(['/']);
  }
}