import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { ReferredPageRoutingModule } from './referred-routing.module';

import { ReferredPage } from './referred.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ReferredPageRoutingModule
  ],
  declarations: [ReferredPage]
})
export class ReferredPageModule {}
