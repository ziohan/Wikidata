import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SearchEntities } from './search-entities';

describe('SearchEntities', () => {
  let component: SearchEntities;
  let fixture: ComponentFixture<SearchEntities>;
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SearchEntities],
    }).compileComponents();

    fixture = TestBed.createComponent(SearchEntities);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
