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
  formText = '';
  formModel: 'spacy' | 'bert' | 'rel' | 'all' = 'spacy';
  inputMode: 'text' | 'file' = 'text';
  fileName = '';
  response = signal('');
  error = signal('');

  ngOnInit() {
    this.http.get<any>('http://127.0.0.1:8000/settings')
      .subscribe(res => {
        this.hops.set(res.default_hops);
        this.top_n.set(res.default_top_n);
        this.formHops = res.default_hops;
        this.formTopN = res.default_top_n;
      });
  }

  setInputMode(mode: 'text' | 'file') {
    this.inputMode = mode;
    this.formText = '';
    this.fileName = '';
  }

  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.txt')) {
      this.error.set('Only .txt files are allowed');
      return;
    }

    this.fileName = file.name;
    this.error.set('');

    const reader = new FileReader();
    reader.onload = (e) => {
      this.formText = e.target?.result as string;
    };
    reader.readAsText(file);
  }

  submitQuery() {
    if (!this.formText.trim()) {
      this.error.set('Please enter a text or upload a .txt file');
      return;
    }

    this.hops.set(this.formHops);
    this.top_n.set(this.formTopN);

    const data = {
      text: this.formText,
      hops: this.hops(),
      top_n: this.top_n(),
      model: this.formModel
    };

    this.error.set('');
    this.service.sendQuery(data)
      .subscribe({
        next: res => {
          const queryId = res.query_id;
          this.router.navigate(['/query-generated'], {
            state: { query_id: queryId }
          });
        },
        error: err => {
          this.error.set(err.error?.message || 'An error occurred');
        }
      });
  }

  goBack() {
    this.router.navigate(['']);
  }
}