import { Component, OnInit } from '@angular/core';

import { Router } from '@angular/router';

@Component({
  selector: 'app-payment',
  templateUrl: './payment.page.html',
  styleUrls: ['./payment.page.scss'],
})
export class PaymentPage implements OnInit {

  constructor(public router: Router) { }

  ngOnInit() {
  }

  ionViewWillEnter() {
    localStorage.setItem('current_url', this.router.url)
  }

}
