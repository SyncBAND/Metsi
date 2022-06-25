import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { TabsEnduserPage } from './tabs-enduser.page';

const routes: Routes = [
  {
    path: '',
    component: TabsEnduserPage,
    children: [
      {
        path: 'enduser-profile',
        loadChildren: () => import('../pages/enduser/tabs-enduser/profile/profile.module').then( m => m.ProfilePageModule)
      },
      {
        path: 'enquiries',
        loadChildren: () => import('../pages/enduser/tabs-enduser/enquiries/enquiries.module').then( m => m.EnquiriesPageModule)
      },
      {
        path: 'enduser-support',
        loadChildren: () => import('../pages/enduser/tabs-enduser/support/support.module').then( m => m.SupportPageModule)
      },
      {
        path: '',
        redirectTo: '/tabs-enduser/enquiries',
        pathMatch: 'full'
      }
    ]
  },
  {
    path: '',
    redirectTo: '/tabs-enduser/enquiries',
    pathMatch: 'full'
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class TabsEnduserPageRoutingModule {}
