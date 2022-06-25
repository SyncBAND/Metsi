import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { IonicModule } from '@ionic/angular';

import { TimerProgress } from './timer-progress.component';

describe('TimerProgress', () => {
  let component: TimerProgress;
  let fixture: ComponentFixture<TimerProgress>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TimerProgress ],
      imports: [IonicModule.forRoot()]
    }).compileComponents();

    fixture = TestBed.createComponent(TimerProgress);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }));

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
