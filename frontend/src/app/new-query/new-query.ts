import { Component, signal, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { NewQueryService } from '../services/new-query';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-new-query',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './new-query.html',
  styleUrl: './new-query.scss'
})

export class NewQuery{
  private service = inject(NewQueryService);
  private router = inject(Router);
  hops = signal(1);
  triplesCount = signal(10);
  response = signal('');
  error = signal('');
  file: File | null = null;

  onFileSelected(event: any) {
    this.file = event.target.files[0];
  }
  submitQuery() {
    const data = {
      hops: this.hops(),
      top_n: this.triplesCount()
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