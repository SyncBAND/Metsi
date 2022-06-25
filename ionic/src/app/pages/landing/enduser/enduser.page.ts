import { Component, OnInit } from '@angular/core';
import { NavController } from '@ionic/angular';

import { Router } from '@angular/router';

@Component({
  selector: 'app-enduser',
  templateUrl: './enduser.page.html',
  styleUrls: ['./enduser.page.scss'],
})
export class EnduserPage implements OnInit {

  constructor(public router: Router, public nav: NavController) { }

  ngOnInit() {
  }

  set_mode(option){
    localStorage.setItem('mode', 'enduser')
    localStorage.setItem('enduser_mode', option)
    return this.nav.navigateRoot('/tabs-enduser');
  }

  ionViewWillEnter() {
    localStorage.setItem('current_url', this.router.url)
  }

}
