import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-search-entities',
  standalone: true,
  templateUrl: './search-entities.html'
})
export class SearchEntities {

  private http = inject(HttpClient);

  entities = signal<any[]>([]);

  page = 1;
  page_size = 10;
  total_pages = 1;

  search = '';
  favorite = false;

  sort_by = 'occurrences';
  order = 'desc';

  ngOnInit() {
    this.load();
  }

  load() {
    this.http.get<any>('http://127.0.0.1:8000/search-entities', {
      params: {
        page: this.page,
        page_size: this.page_size,
        search: this.search,
        favorite: this.favorite,
        sort_by: this.sort_by,
        order: this.order
      }
    }).subscribe(res => {
      this.entities.set(res.data);
      this.total_pages = res.pagination.total_pages;
    });
  }

  changePage(p: number) {
    this.page = p;
    this.load();
  }

  toggleSort(field: string) {
    if (this.sort_by === field) {
      this.order = this.order === 'asc' ? 'desc' : 'asc';
    } else {
      this.sort_by = field;
      this.order = 'desc';
    }
    this.load();
  }

  toggleFavorite(qid: string) {
    this.http.patch(`http://127.0.0.1:8000/entities/${qid}/favorite`, {})
      .subscribe(() => this.load());
  }

  visualize(qid: string) {
    this.http.get<any>(`http://127.0.0.1:8000/entity-graph/${qid}`)
      .subscribe(res => {
        window.open(`http://127.0.0.1:8000${res.image_url}`, '_blank');
      });
  }
}