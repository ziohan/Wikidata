import { Component, signal, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { NewQueryService } from '../services/new-query';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
@Component({
  selector: 'app-new-query',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './new-query.html',
  styleUrl: './new-query.scss'
})

export class NewQuery {
  private service = inject(NewQueryService);
  private router = inject(Router);
  private http = inject(HttpClient);
  hops = signal(1);
  top_n = signal(10);
  formHops = 1;
  formTopN = 10;
  response = signal('');
  error = signal('');
  file: File | null = null;

  ngOnInit() {
    this.http.get<any>('http://127.0.0.1:8000/settings')
      .subscribe(res => {
        this.hops.set(res.default_hops);
        this.top_n.set(res.default_top_n);

        this.formHops = res.default_hops;
        this.formTopN = res.default_top_n;
      });
  }

  onFileSelected(event: any) {
    this.file = event.target.files[0];
  }

  submitQuery() {
    this.hops.set(this.formHops);
    this.top_n.set(this.formTopN);
    
    const data = {
      hops: this.hops(),
      top_n: this.top_n()
    };

    this.service.sendQuery(data, this.file)
      .subscribe(res => {
        const queryId = res.query_id;
        this.router.navigate(['/query-generated'], {
          state: { query_id: queryId }
        });
      });
  }

  goBack() {
    this.router.navigate(['']);
  }
}