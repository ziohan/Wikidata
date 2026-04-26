import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PopupHistory } from './popup-history';

describe('PopupHistory', () => {
  let component: PopupHistory;
  let fixture: ComponentFixture<PopupHistory>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PopupHistory],
    }).compileComponents();
    fixture = TestBed.createComponent(PopupHistory);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
