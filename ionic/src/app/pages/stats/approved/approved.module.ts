import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { ApprovedPageRoutingModule } from './approved-routing.module';

import { ApprovedPage } from './approved.page';

import { ComponentsModule } from 'src/app/components/components.module';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ApprovedPageRoutingModule,
    ComponentsModule
  ],
  declarations: [ApprovedPage]
})
export class ApprovedPageModule {}
