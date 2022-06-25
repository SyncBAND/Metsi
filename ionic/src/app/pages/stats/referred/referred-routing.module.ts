import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ReferredPage } from './referred.page';

const routes: Routes = [
  {
    path: '',
    component: ReferredPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ReferredPageRoutingModule {}
