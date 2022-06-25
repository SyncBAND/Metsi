import { Component, OnInit } from '@angular/core';

import { AuthService } from '../../../shared/service/auth/auth.service';
import { ToastService } from '../../../shared/service/toast/toast.service';
import { UtilsService } from '../../../shared/service/utils/utils.service';

import { Router } from '@angular/router';

@Component({
  selector: 'app-pending',
  templateUrl: './pending.page.html',
  styleUrls: ['./pending.page.scss'],
})
export class PendingPage implements OnInit {

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

	SlideDidChange() {
    
	}

  back(){
    this.router.navigateByUrl( localStorage.getItem('current_url') != null ? `/`+localStorage.getItem('current_url') : '/tabs-enduser/enduser-profile' );
  }

  doInfinite(event) {
    this.getPending(true, event);
  }

  getPending(isFirstLoad, event){

    let url = 'enquiries/pending'

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

  chat(id){
    localStorage.setItem('chat_list_object_id', id)
    localStorage.setItem('chat_list_content_type', 'enquiries')
    this.router.navigateByUrl('/chat-list');
  }

	calculate(datetime){
		let past_seconds = Math.abs(Math.round( ( new Date().getTime() - new Date(datetime).getTime() ) / 1000));
		let current_seconds = 0;
		if(past_seconds < (12 * 60 * 60))
			current_seconds = (12 * 60 * 60) - past_seconds;
		
		return current_seconds;
	}

  interested(id){
    localStorage.setItem('enquiry_id', id)
    this.router.navigateByUrl('/interests');
  }

  cancel(id){
    this.utils.openModal(id, "Cancel").then((data) => {
      if (data != undefined) {
        
          if(data.success){
              
              let formData = new FormData();

              formData.append('enquiry_id', id)
              formData.append('user', '1')
              formData.append('status_details', data.description)
              formData.append('current_status', 'Cancelled')
              formData.append('previous_skill_needed', '1')
              formData.append('mode', (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'enduser').toUpperCase())

              this.authService.request_logged_in(`enquiries-activity`, "post", formData).then(()=>{
                  this.refresh()
                  this.toast.presentToast('Cancelled')
              },(err)=>{
                  this.authService.handleError(err);
              });

          }
          else
              this.toast.presentToast('Dismissed')

      }
    });
  }

  refresh(){
    this.bookings = []
    this.num_pages = 1
    this.page_number = 1
    this.getPending(false, "");
  }

}
