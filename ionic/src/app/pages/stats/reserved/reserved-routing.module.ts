import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ReservedPage } from './reserved.page';

const routes: Routes = [
  {
    path: '',
    component: ReservedPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ReservedPageRoutingModule {}
