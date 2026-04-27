import { TestBed } from '@angular/core/testing';

import { LastQueries } from './last-queries';

describe('LastQueries', () => {
  let service: LastQueries;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LastQueries);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
