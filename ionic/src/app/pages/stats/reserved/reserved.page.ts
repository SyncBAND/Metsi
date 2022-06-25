import { Component, OnInit } from '@angular/core';

import { AuthService } from '../../../shared/service/auth/auth.service';
import { ToastService } from '../../../shared/service/toast/toast.service';
import { UtilsService } from '../../../shared/service/utils/utils.service';

import { ActionSheetController } from '@ionic/angular';

import { Router } from '@angular/router';

@Component({
  selector: 'app-reserved',
  templateUrl: './reserved.page.html',
  styleUrls: ['./reserved.page.scss'],
})
export class ReservedPage implements OnInit {

  page_number = 1
  num_pages = 1
  
  bookings = []

  constructor(private _ACTION : ActionSheetController, public toast: ToastService, public authService: AuthService, public utils: UtilsService, private router: Router
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
    this.getReserved(true, event);
  }

  getReserved(isFirstLoad, event){

    let url = 'enquiries/reserved'

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
    this.getReserved(false, "");
  }

  resolve(data){
    localStorage.setItem('resolving', JSON.stringify(data))
    this.router.navigateByUrl('/resolving');
  }

  chat(id){
    localStorage.setItem('chat_list_object_id', id)
    localStorage.setItem('chat_list_content_type', 'enquiries')
    this.router.navigateByUrl('/chat-list');
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
              formData.append('mode', (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'agent').toUpperCase())

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

  /**
   * @public
   * @method launchCancelSheet
   * @description               Mobile only - Uses the ActionSheet component to present the 
   *                            user with options to select an image using the device camera 
   *                            or photolibrary
   * @return {none}
   */
  async launchCancelSheet(id) : Promise<void>
  {
     let action  	= this._ACTION.create({
        header 		: 'Cancel',
        buttons 	: [
           {
              text 	: 'Continue',
              handler 	: () =>
              {
                const formData = new FormData();
                formData.append('id', id);
                formData.append('mode', (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'agent').toUpperCase())

                this.authService.request_logged_in(`applications/cancel`, "put", formData).then(()=>{
                  this.refresh()
                },(err)=>{
                  this.authService.handleError(err);
                });
              }
           },
           {
              text 	: 'Cancel',
              handler 	: () =>
              {
                 console.log('Cancelled');
              }
           }
        ]
     });
    (await action).present();
  }

}
