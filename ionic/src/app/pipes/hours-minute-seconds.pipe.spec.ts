import { HoursMinuteSecondsPipe } from './hours-minute-seconds.pipe';

describe('HoursMinuteSecondsPipe', () => {
  it('create an instance', () => {
    const pipe = new HoursMinuteSecondsPipe();
    expect(pipe).toBeTruthy();
  });
});
