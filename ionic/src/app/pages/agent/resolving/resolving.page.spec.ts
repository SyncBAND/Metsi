import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { IonicModule } from '@ionic/angular';

import { ResolvingPage } from './resolving.page';

describe('ResolvingPage', () => {
  let component: ResolvingPage;
  let fixture: ComponentFixture<ResolvingPage>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ResolvingPage ],
      imports: [IonicModule.forRoot()]
    }).compileComponents();

    fixture = TestBed.createComponent(ResolvingPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }));

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
