import { Component, OnInit } from '@angular/core';

import { AuthService } from '../../shared/service/auth/auth.service';
import { ToastService } from '../../shared/service/toast/toast.service';
import { UtilsService } from '../../shared/service/utils/utils.service';

import { ActionSheetController } from '@ionic/angular';

import { Router } from '@angular/router';

@Component({
  selector: 'app-interests',
  templateUrl: './interests.page.html',
  styleUrls: ['./interests.page.scss'],
})
export class InterestsPage implements OnInit {

  page_number = 1
  num_pages = 1
  mode = (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'agent').toUpperCase()
  
  interests = []

  constructor(private _ACTION : ActionSheetController, public toast: ToastService, public utils: UtilsService, public authService: AuthService, private router: Router) { 
      
  }

  ngOnInit() {
    
  }

  ionViewWillEnter(){

    if(this.authService.isLoggedIn)
      this.refresh()
  }

  back(){
    this.router.navigateByUrl( localStorage.getItem('current_first_level_url') != null ? `/`+localStorage.getItem('current_first_level_url') : '/tabs-enduser/enduser-profile' );
  }

  doInfinite(event) {
    this.getInterests(true, event);
  }

  getInterests(isFirstLoad, event){

    let url = 'enquiry-interest'

    if(isFirstLoad)
      url = url + '?page=' + this.page_number + '&_limit=' + this.num_pages;

    let enquiry_id = localStorage.getItem('enquiry_id')
    if(enquiry_id == undefined)
      enquiry_id = '0'

    this.authService.request_logged_in(url, 'get', {'enquiry_id': enquiry_id}).then((results:any)=>{
      
      this.num_pages = results.paginator.num_pages
      if(isFirstLoad)
        event.target.complete();
        
      this.page_number++;

      results.results.map((res)=>{
        // res['created'] = new Date(res['created'])
        // res['modified'] = new Date(res['modified'])
        this.interests.push(res)
      })

    },(err)=>{

      this.authService.handleError(err)

    })

  }

  refresh(){
    this.interests = []
    this.num_pages = 1
    this.page_number = 1
    this.getInterests(false, "");
  }

  approve(id, enquiry_id){
    if(this.mode=='ENDUSER'){
            
      let formData = new FormData();

      formData.append('enquiry_id', enquiry_id)
      formData.append('current_status', 'Approved')
      formData.append('mode', this.mode)

      this.authService.request_logged_in(`enquiry-interest/${id}/approve`, "patch", formData).then(()=>{
          this.toast.presentToast('Approved')
          this.router.navigateByUrl('/approved');
      },(err)=>{
          this.authService.handleError(err);
      });
      
    }
    else
        this.toast.presentToast('Not permitted')
  }

  decline(id, enquiry_id){
    this.utils.openModal(id, 'Cancel').then((data) => {
      if (data != undefined) {
        
          if(data.success && this.mode=='ENDUSER'){
            
              let formData = new FormData();

              formData.append('enquiry_id', enquiry_id)
              formData.append('status_details', data.description)
              formData.append('current_status', 'Declined')
              formData.append('mode', this.mode)

              this.authService.request_logged_in(`enquiry-interest/${id}/decline`, "patch", formData).then(()=>{
                  this.toast.presentToast('Declined')
                  this.refresh()
              },(err)=>{
                  this.authService.handleError(err);
              });
              
          }
          else
              this.toast.presentToast('Dismissed')

      }
    });
  }

  rating(data){
    if( data['total_number'] == 0)
      return 0
    return ( ((data['total_sum'] / 5)/data['total_number']) * 100 ).toFixed(2)
  }

}
