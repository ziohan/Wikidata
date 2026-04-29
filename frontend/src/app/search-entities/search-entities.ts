import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
interface Entity {
  qid: string;
  label: string;
  occurrences: number;
  favorite: boolean;
}
@Component({
  selector: 'app-search-entities',
  standalone: true,
  templateUrl: './search-entities.html',
  styleUrl: './search-entities.scss',
  imports: [CommonModule, FormsModule]
})
export class SearchEntities {
  private http = inject(HttpClient);
  private router = inject(Router);
  entities = signal<Entity[]>([]);
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
    }).subscribe((res: any) => {
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
    this.http.patch<any>(
      `http://127.0.0.1:8000/entities/${qid}/favorite`,
      {}
    ).subscribe(res => {

      const updated = this.entities().map(e => {
        if (e.qid === qid) {
          return {
            ...e,
            favorite: res.favorite
          };
        }
        return e;
      });

      this.entities.set(updated);
    });
  }
  toggleFavoritesFilter() {
    this.favorite = !this.favorite;
    this.page = 1;
    this.load();
  }

  visualize(qid: string) {
    this.router.navigate([`/entity/${qid}`]);
  }
}