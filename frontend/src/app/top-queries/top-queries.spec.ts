import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TopQueries } from './top-queries';

describe('TopQueries', () => {
  let component: TopQueries;
  let fixture: ComponentFixture<TopQueries>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TopQueries],
    }).compileComponents();

    fixture = TestBed.createComponent(TopQueries);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
