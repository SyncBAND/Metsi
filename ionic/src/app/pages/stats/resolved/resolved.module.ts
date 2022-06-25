import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { ResolvedPageRoutingModule } from './resolved-routing.module';

import { ResolvedPage } from './resolved.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ResolvedPageRoutingModule
  ],
  declarations: [ResolvedPage]
})
export class ResolvedPageModule {}
