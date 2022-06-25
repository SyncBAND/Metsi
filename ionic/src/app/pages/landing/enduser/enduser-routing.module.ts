import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { EnduserPage } from './enduser.page';

const routes: Routes = [
  {
    path: '',
    component: EnduserPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class EnduserPageRoutingModule {}
