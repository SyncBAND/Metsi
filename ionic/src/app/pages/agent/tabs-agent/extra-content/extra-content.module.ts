import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { ExtraContentPageRoutingModule } from './extra-content-routing.module';

import { ExtraContentPage } from './extra-content.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ExtraContentPageRoutingModule
  ],
  declarations: [ExtraContentPage]
})
export class ExtraContentPageModule {}