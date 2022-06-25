import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { EnduserPageRoutingModule } from './enduser-routing.module';

import { EnduserPage } from './enduser.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    EnduserPageRoutingModule
  ],
  declarations: [EnduserPage]
})
export class EnduserPageModule {}
