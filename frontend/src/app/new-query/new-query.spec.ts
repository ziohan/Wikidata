import { TestBed } from '@angular/core/testing';
import { NewQuery } from './new-query';

describe('NewQuery', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewQuery]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(NewQuery);
    const component = fixture.componentInstance;
    expect(component).toBeTruthy();
  });
});