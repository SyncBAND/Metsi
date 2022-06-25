import { Component, OnInit } from '@angular/core';

import { AuthService } from '../../../shared/service/auth/auth.service';
import { ToastService } from '../../../shared/service/toast/toast.service';
import { UtilsService } from '../../../shared/service/utils/utils.service';

import { Router } from '@angular/router';

@Component({
  selector: 'app-approved',
  templateUrl: './approved.page.html',
  styleUrls: ['./approved.page.scss'],
})
export class ApprovedPage implements OnInit {

  page_number = 1
  num_pages = 1
  
  bookings = []

  constructor(public toast: ToastService, public authService: AuthService, public utils: UtilsService, private router: Router
    ) { 
      
  }


  ngOnInit() {
    
  }

  ionViewWillEnter(){
    localStorage.setItem('current_first_level_url', this.router.url)
    
    this.refresh()
  }

  back(){
    this.router.navigateByUrl( localStorage.getItem('current_url') != null ? `/`+localStorage.getItem('current_url') : '/tabs-enduser/enduser-profile' );
  }

  doInfinite(event) {
    this.getApproved(true, event);
  }

  getApproved(isFirstLoad, event){

    let url = 'enquiries/approved'

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

  calendar(id){
    this.router.navigateByUrl('/calendar');
  }

  chat(id){
    localStorage.setItem('chat_list_object_id', id)
    localStorage.setItem('chat_list_content_type', 'enquiries')
    this.router.navigateByUrl('/chat-list');
  }

	SlideDidChange() {
    
	}

	calculate(datetime){
		let past_seconds = Math.abs(Math.round( ( new Date().getTime() - new Date(datetime).getTime() ) / 1000));
		let current_seconds = 0;
		if(past_seconds < (12 * 60 * 60))
			current_seconds = (12 * 60 * 60) - past_seconds;
		
		return current_seconds;
	}

  refresh(){
    this.bookings = []
    this.num_pages = 1
    this.page_number = 1
    this.getApproved(false, "");
  }

}
