import { TestBed } from '@angular/core/testing';

import { NewQuery } from './new-query';

describe('NewQuery', () => {
  let service: NewQuery;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(NewQuery);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
