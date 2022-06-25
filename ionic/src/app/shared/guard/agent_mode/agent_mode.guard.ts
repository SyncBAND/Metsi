import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';

import { NavController } from '@ionic/angular';

import { ToastService } from '../../../shared/service/toast/toast.service';

@Injectable({
  providedIn: 'root'
})
export class AgentModeGuard implements CanActivate {

  constructor(
      public nav: NavController,
      public toast: ToastService, 
  ) { }

  canActivate(
    next: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    
    let agent_mode = localStorage.getItem('agent_mode')
    if(agent_mode == null || agent_mode != 'set'){
      localStorage.removeItem('mode')
      this.toast.presentToast("Please enter your agent pin code")
      return this.nav.navigateRoot('home');
    }

    return true;
  }
  
}
