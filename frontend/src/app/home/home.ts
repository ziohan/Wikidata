import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { PopupHistory } from '../popup-history/popup-history';


@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, PopupHistory],
  templateUrl: './home.html',
  styleUrl: './home.scss'
})
export class Home {
  private router = inject(Router);
  showHistory = signal(false);
  goToSettings() {
    this.router.navigate(['/settings']);
  }
  goToNewQuery() {
    this.router.navigate(['/new-query']);
  }
  openHistory() {
    this.showHistory.set(true);
  }
  closeHistory() {
    this.showHistory.set(false);
  }
}