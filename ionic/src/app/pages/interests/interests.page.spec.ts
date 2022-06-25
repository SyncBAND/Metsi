import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { IonicModule } from '@ionic/angular';

import { InterestsPage } from './interests.page';

describe('InterestsPage', () => {
  let component: InterestsPage;
  let fixture: ComponentFixture<InterestsPage>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ InterestsPage ],
      imports: [IonicModule.forRoot()]
    }).compileComponents();

    fixture = TestBed.createComponent(InterestsPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }));

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
