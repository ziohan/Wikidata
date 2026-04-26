import { ComponentFixture, TestBed } from '@angular/core/testing';

import { QueryGenerated } from './query-generated';

describe('QueryGenerated', () => {
  let component: QueryGenerated;
  let fixture: ComponentFixture<QueryGenerated>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [QueryGenerated],
    }).compileComponents();

    fixture = TestBed.createComponent(QueryGenerated);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
