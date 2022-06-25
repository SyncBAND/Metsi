import { Component, OnInit } from '@angular/core';

import { AuthService } from '../shared/service/auth/auth.service';

@Component({
  selector: 'app-tabs-enduser',
  templateUrl: './tabs-enduser.page.html',
  styleUrls: ['./tabs-enduser.page.scss'],
})
export class TabsEnduserPage implements OnInit {

  constructor(public authService: AuthService) { }

  ngOnInit() {
    return this.authService.check_mode('enduser')
  }

  ionViewWillEnter() {
    return this.authService.check_mode('enduser')
  }

}
