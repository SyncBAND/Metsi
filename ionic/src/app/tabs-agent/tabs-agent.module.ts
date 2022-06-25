import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { TabsAgentPageRoutingModule } from './tabs-agent-routing.module';

import { TabsAgentPage } from './tabs-agent.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    TabsAgentPageRoutingModule
  ],
  declarations: [TabsAgentPage]
})
export class TabsAgentPageModule {}
