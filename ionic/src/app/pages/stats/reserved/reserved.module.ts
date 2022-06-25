import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { ReservedPageRoutingModule } from './reserved-routing.module';

import { ReservedPage } from './reserved.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ReservedPageRoutingModule
  ],
  declarations: [ReservedPage]
})
export class ReservedPageModule {}
