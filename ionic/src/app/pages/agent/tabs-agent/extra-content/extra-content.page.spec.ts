import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { IonicModule } from '@ionic/angular';

import { ExtraContentPage } from './extra-content.page';

describe('ExtraContentPage', () => {
  let component: ExtraContentPage;
  let fixture: ComponentFixture<ExtraContentPage>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ExtraContentPage ],
      imports: [IonicModule.forRoot()]
    }).compileComponents();

    fixture = TestBed.createComponent(ExtraContentPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }));

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
