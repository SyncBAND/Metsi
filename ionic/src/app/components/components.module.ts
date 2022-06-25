import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { RatingsComponent } from './ratings/ratings.component';
import { LoginOrRegisterComponent } from './login-or-register/login-or-register.component';
import { TimerProgress } from './timer-progress/timer-progress.component';


@NgModule({
  declarations: [
    [LoginOrRegisterComponent, RatingsComponent, TimerProgress]
  ],
  exports: [
    LoginOrRegisterComponent,
    RatingsComponent,
    TimerProgress
  ],
  imports: [
    CommonModule,
  ]
})
export class ComponentsModule { }
