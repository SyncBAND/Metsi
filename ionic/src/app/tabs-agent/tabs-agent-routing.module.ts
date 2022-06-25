import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { TabsAgentPage } from './tabs-agent.page';

const routes: Routes = [
  {
    path: '',
    component: TabsAgentPage,
    children: [
      {
        path: 'agent-profile',
        loadChildren: () => import('../pages/agent/tabs-agent/profile/profile.module').then( m => m.ProfilePageModule)
      },
      {
        path: 'work',
        loadChildren: () => import('../pages/agent/tabs-agent/work/work.module').then( m => m.WorkPageModule)
      },
      {
        path: 'agent-search',
        loadChildren: () => import('../pages/agent/tabs-agent/search/search.module').then( m => m.SearchPageModule)
      },
      {
        path: 'tutorials',
        loadChildren: () => import('../pages/agent/tabs-agent/extra-content/extra-content.module').then( m => m.ExtraContentPageModule)
      },
      {
        path: 'agent-support',
        loadChildren: () => import('../pages/agent/tabs-agent/support/support.module').then( m => m.SupportPageModule)
      },
      {
        path: '',
        redirectTo: '/tabs-agent/agent-search',
        pathMatch: 'full'
      }
    ]
  },
  {
    path: '',
    redirectTo: '/tabs-agent/agent-search',
    pathMatch: 'full'
  }
];
 
@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class TabsAgentPageRoutingModule {}
