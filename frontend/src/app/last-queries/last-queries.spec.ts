import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LastQueries } from './last-queries';

describe('LastQueries', () => {
  let component: LastQueries;
  let fixture: ComponentFixture<LastQueries>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LastQueries],
    }).compileComponents();

    fixture = TestBed.createComponent(LastQueries);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
