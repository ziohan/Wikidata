import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.html',
  styleUrl: './home.scss'
})
export class Home {
  private router = inject(Router);
  goToSettings() {
    this.router.navigate(['/settings']);
  }
  goToNewQuery() {
    this.router.navigate(['/new-query']);
  }
  goToHistory(){
    this.router.navigate(['/history']);
  }
}