import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { ModalLocationPageRoutingModule } from './modal-location-routing.module';

import { ModalLocationPage } from './modal-location.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ModalLocationPageRoutingModule
  ],
  declarations: [ModalLocationPage]
})
export class ModalLocationPageModule {}
