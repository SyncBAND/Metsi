import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ResolvedPage } from './resolved.page';

const routes: Routes = [
  {
    path: '',
    component: ResolvedPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ResolvedPageRoutingModule {}
