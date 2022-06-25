import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ResolvingPage } from './resolving.page';

const routes: Routes = [
  {
    path: '',
    component: ResolvingPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ResolvingPageRoutingModule {}
