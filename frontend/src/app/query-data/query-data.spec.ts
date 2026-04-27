import { ComponentFixture, TestBed } from '@angular/core/testing';
import { QueryData } from './query-data';

describe('QueryData', () => {
  let component: QueryData;
  let fixture: ComponentFixture<QueryData>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [QueryData],
    }).compileComponents();
    fixture = TestBed.createComponent(QueryData);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
