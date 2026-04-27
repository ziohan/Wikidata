import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Search_Entities } from '../services/search-entities';

@Component({
  selector: 'app-search-entities',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './search-entities.html',
  styleUrl: './search-entities.scss'
})
export class SearchEntities {

  private service = inject(Search_Entities);
  private router = inject(Router);

  search = '';
  favorite = false;

  sort_by = 'occurrences';
  order: 'asc' | 'desc' = 'desc';

  page = 1;
  page_size = 10;

  entities = signal<any[]>([]);
  pagination = signal<any>({});

  ngOnInit() {
    this.load();
  }

  load() {
    this.service.getEntities({
      search: this.search,
      favorite: this.favorite,
      page: this.page,
      page_size: this.page_size,
      sort_by: this.sort_by,
      order: this.order
    }).subscribe(res => {
      this.entities.set(res.data || []);
      this.pagination.set(res.pagination || {});
    });
  }

  toggleFavorite(qid: string) {
    this.service.toggleFavorite(qid).subscribe(res => {
      this.entities.update(list =>
        list.map(e =>
          e.qid === qid
            ? { ...e, favorite: res.favorite }
            : e
        )
      );
    });
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

  changePage(p: number) {
    this.page = p;
    this.load();
  }

  visualize(qid: string) {
    this.router.navigate([`/entity/${qid}`]);
  }
}