import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { TabsEnduserPageRoutingModule } from './tabs-enduser-routing.module';

import { TabsEnduserPage } from './tabs-enduser.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    TabsEnduserPageRoutingModule
  ],
  declarations: [TabsEnduserPage]
})
export class TabsEnduserPageModule {}
