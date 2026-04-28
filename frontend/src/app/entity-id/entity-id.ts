import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-entity-id',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './entity-id.html',
  styleUrl: './entity-id.scss'
})
export class EntityId {

  private route = inject(ActivatedRoute);
  private http = inject(HttpClient);
  private router = inject(Router);

  qid = '';
  occurrences = 0;

  queries = signal<any[]>([]);
  expanded = signal<{ [key: string]: boolean }>({});

  ngOnInit() {
    this.qid = this.route.snapshot.params['id'];
    this.load();
  }

  load() {
    this.http.get<any>(`http://127.0.0.1:8000/entity/${this.qid}`)
      .subscribe(res => {
        this.occurrences = res.occurrences;
        this.queries.set(res.queries);
      });
  }

  toggle(qid: string) {
    this.expanded.update(e => ({
      ...e,
      [qid]: !e[qid]
    }));
  }

  visualize(queryId: string) {
    this.router.navigate([`/query/${queryId}`]);
  }
}