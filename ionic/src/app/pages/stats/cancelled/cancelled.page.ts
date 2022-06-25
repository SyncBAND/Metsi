import { Component, OnInit } from '@angular/core';

import { AuthService } from '../../../shared/service/auth/auth.service';
import { ToastService } from '../../../shared/service/toast/toast.service';
import { UtilsService } from '../../../shared/service/utils/utils.service';

import { Router } from '@angular/router';

import { NavController } from '@ionic/angular';

@Component({
  selector: 'app-cancelled',
  templateUrl: './cancelled.page.html',
  styleUrls: ['./cancelled.page.scss'],
})
export class CancelledPage implements OnInit {

  page_number = 1
  num_pages = 1
  
  bookings = []

  constructor(public toast: ToastService, public nav: NavController, public authService: AuthService, public utils: UtilsService, private router: Router
    ) { 
      
  }


  ngOnInit() {
    
  }

  ionViewWillEnter(){
    localStorage.setItem('current_first_level_url', this.router.url)
    
    this.refresh()
  }

	SlideDidChange() {
    
	}

  back(){
    this.nav.navigateRoot( localStorage.getItem('current_url') != null ? `/`+localStorage.getItem('current_url') : '/tabs-enduser/enduser-profile' );
  }

  doInfinite(event) {
    this.getCancelled(true, event);
  }

  getCancelled(isFirstLoad, event){

    let url = 'enquiries/cancelled'

    if(isFirstLoad)
      url = url + '?page=' + this.page_number + '&_limit=' + this.num_pages;

    this.authService.request_logged_in(url, 'get', {}).then((results:any)=>{

      this.num_pages = results.paginator.num_pages
      if(isFirstLoad)
        event.target.complete();
        
      this.page_number++;

      results.results.map((res)=>{
        res['created'] = new Date(res['created'])
        res['modified'] = new Date(res['modified'])
        this.bookings.push(res)
      })

    },(err)=>{

      this.authService.handleError(err)

    })

  }

  refresh(){
    this.bookings = []
    this.num_pages = 1
    this.page_number = 1
    this.getCancelled(false, "");
  }

}
