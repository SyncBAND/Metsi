import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { IonicModule } from '@ionic/angular';

import { ModalLocationPage } from './modal-location.page';

describe('ModalLocationPage', () => {
  let component: ModalLocationPage;
  let fixture: ComponentFixture<ModalLocationPage>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ModalLocationPage ],
      imports: [IonicModule.forRoot()]
    }).compileComponents();

    fixture = TestBed.createComponent(ModalLocationPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }));

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
