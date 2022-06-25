import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ModalLocationPage } from './modal-location.page';

const routes: Routes = [
  {
    path: '',
    component: ModalLocationPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ModalLocationPageRoutingModule {}
