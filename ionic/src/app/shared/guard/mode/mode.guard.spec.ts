import { TestBed } from '@angular/core/testing';

import { ModeGuard } from './mode.guard';

describe('ModeGuard', () => {
  let guard: ModeGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(ModeGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
