import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';

import { NavController } from '@ionic/angular';

@Injectable({
  providedIn: 'root'
})
export class ModeGuard implements CanActivate {

  constructor(
      public nav: NavController
  ) { }

  canActivate(
    next: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    
    let mode = localStorage.getItem('mode')
    if(mode != null){
      if(mode == 'agent' || mode == 'enduser')
        return this.nav.navigateRoot('/tabs-' + mode);
      else{
        localStorage.removeItem('mode')
        return this.nav.navigateRoot('/home' );
      }
    }

    return true;
  }
  
}
