import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { EnquirePage } from './enquire.page';

const routes: Routes = [
  {
    path: '',
    component: EnquirePage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class EnquirePageRoutingModule {}
