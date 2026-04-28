import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './settings.html',
  styleUrl: './settings.scss'
})
export class Settings {
  private http = inject(HttpClient);
  hops = signal(1);
  top_n = signal(10);
  formHops = 1;
  formTopN = 10;
  ngOnInit() {
    this.load();
  }

  load() {
    this.http.get<any>('http://127.0.0.1:8000/settings')
      .subscribe(res => {
        this.hops.set(res.default_hops);
        this.top_n.set(res.default_top_n);
        this.formHops = res.default_hops;
        this.formTopN = res.default_top_n;
      });
  }

  save() {
    this.hops.set(this.formHops);
    this.top_n.set(this.formTopN);
    const data = {
      default_hops: this.hops(),
      default_top_n: this.top_n()
    };

    this.http.post('http://127.0.0.1:8000/settings', data)
      .subscribe(() => {
        alert('Settings saved!');
      });
  }

  clearQueries() {
    if (!confirm('Delete ALL queries?')) return;

    this.http.delete('http://127.0.0.1:8000/clear-queries')
      .subscribe(() => alert('All queries deleted'));
  }
}