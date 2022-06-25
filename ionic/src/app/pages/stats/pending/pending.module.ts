import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { PendingPageRoutingModule } from './pending-routing.module';
import { ComponentsModule } from 'src/app/components/components.module';

import { PendingPage } from './pending.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    PendingPageRoutingModule,
    ComponentsModule
  ],
  declarations: [PendingPage]
})
export class PendingPageModule {}
