import { Component, OnInit } from '@angular/core';

import { AuthService } from '../../../shared/service/auth/auth.service';
import { ToastService } from '../../../shared/service/toast/toast.service';

import { ActionSheetController } from '@ionic/angular';

import { Router } from '@angular/router';

@Component({
  selector: 'app-payments',
  templateUrl: './payments.page.html',
  styleUrls: ['./payments.page.scss'],
})
export class PaymentsPage implements OnInit {

  page_number = 1
  num_pages = 1
  
  invoices = []

  constructor(private _ACTION : ActionSheetController, public toast: ToastService, public authService: AuthService, private router: Router
    ) { 
      
  }


  ngOnInit() {
    
  }

  ionViewWillEnter(){
    localStorage.setItem('current_url', this.router.url)
    if(this.authService.isLoggedIn)
      this.refresh()
  }

  back(){
    this.router.navigateByUrl( localStorage.getItem('current_url') != null ? `/`+localStorage.getItem('current_url') : '/tabs-enduser/enduser-profile' );
  }

  doInfinite(event) {
    this.getInvoices(true, event);
  }

	SlideDidChange() {
    
	}

  getInvoices(isFirstLoad, event){

    let url = 'invoices'

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
        this.invoices.push(res)
      })

    },(err)=>{

      this.authService.handleError(err)

    })

  }

  refresh(){
    this.invoices = []
    this.num_pages = 1
    this.page_number = 1
    this.getInvoices(false, "");
  }

  chat(id){
    this.router.navigateByUrl('/chat-list');
  }

  cancel(id){
    this.launchCancelSheet(id)
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
                this.authService.request_logged_in(`applications/cancel`, "put", formData).then(()=>{
                  this.refresh()
                  this.toast.presentToast('Cancelled')
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
