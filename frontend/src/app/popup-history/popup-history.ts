import { Component, EventEmitter, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-popup-history',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './popup-history.html',
  styleUrl: './popup-history.scss'
})
export class PopupHistory {

  @Output() close = new EventEmitter<void>();

  private router = inject(Router);

  go(path: string) {
    // 👇 fecha primeiro (evita glitch visual)
    this.close.emit();

    // 👇 pequena garantia de timing
    setTimeout(() => {
      this.router.navigate([path]);
    }, 0);
  }

  closeModal() {
    this.close.emit();
  }
}