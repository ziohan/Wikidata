import { TestBed } from '@angular/core/testing';

import { SearchEntities } from './search-entities';

describe('SearchEntities', () => {
  let service: SearchEntities;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SearchEntities);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
