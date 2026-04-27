import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { LastQueriesService } from '../services/last-queries';

@Component({
  selector: 'app-last-queries',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './last-queries.html',
  styleUrl: './last-queries.scss'
})
export class LastQueries {
  private service = inject(LastQueriesService);
  private router = inject(Router);
  search = '';
  favorite = false;
  start_date = '';
  end_date = '';
  page = 1;
  page_size = 10;
  queries = signal<any[]>([]);
  pagination = signal<any>({});

  ngOnInit() {
    this.load();
  }

  load() {
    this.service.getQueries({
      search: this.search,
      favorite: this.favorite,
      start_date: this.start_date,
      end_date: this.end_date,
      page: this.page,
      page_size: this.page_size
    }).subscribe({
      next: (res) => {
        this.queries.set(res.data || []);
        this.pagination.set(res.pagination || {});
      }
    });
  }

  toggleFavorite(id: string) {
    this.service.toggleFavorite(id).subscribe(() => this.load());
  }

  deleteQuery(id: string) {
    if (!confirm('Delete this query?')) return;

    this.service.deleteQuery(id).subscribe(() => this.load());
  }

  visualize(id: string) {
    this.router.navigate([`/query/${id}`]);
  }

  changePage(p: number) {
    this.page = p;
    this.load();
  }
}