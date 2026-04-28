import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EntityId } from './entity-id';

describe('EntityId', () => {
  let component: EntityId;
  let fixture: ComponentFixture<EntityId>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EntityId],
    }).compileComponents();

    fixture = TestBed.createComponent(EntityId);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
