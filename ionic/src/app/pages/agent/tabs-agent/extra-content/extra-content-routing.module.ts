import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ExtraContentPage } from './extra-content.page';

const routes: Routes = [
  {
    path: '',
    component: ExtraContentPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ExtraContentPageRoutingModule {}
