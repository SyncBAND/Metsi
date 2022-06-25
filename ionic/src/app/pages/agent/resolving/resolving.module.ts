import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { ResolvingPageRoutingModule } from './resolving-routing.module';

import { ResolvingPage } from './resolving.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ResolvingPageRoutingModule,
    ReactiveFormsModule
  ],
  declarations: [ResolvingPage]
})
export class ResolvingPageModule {}
