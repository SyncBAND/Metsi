import { TestBed } from '@angular/core/testing';

import { AgentModeGuard } from './agent_mode.guard';

describe('AgentModeGuard', () => {
  let guard: AgentModeGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(AgentModeGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
