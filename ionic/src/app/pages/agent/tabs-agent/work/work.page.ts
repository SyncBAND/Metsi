import { Component, OnInit } from '@angular/core';

import { AuthService } from '../../../../shared/service/auth/auth.service';
import { FcmService } from '../../../../shared/service/push/fcm.service';
import { ToastService } from '../../../../shared/service/toast/toast.service';

import { Router } from '@angular/router';

@Component({
  selector: 'app-work',
  templateUrl: './work.page.html',
  styleUrls: ['./work.page.scss'],
})
export class WorkPage implements OnInit {

  work = []
  stats = []

  constructor(public fcmService: FcmService, public toast: ToastService, public authService: AuthService, private router: Router) { 
      
  }

  ngOnInit() {
    
  }

  ionViewWillEnter(){
    localStorage.setItem('current_url', this.router.url)
    
    if(this.authService.isLoggedIn)
      this.refresh()

  }

  reserved(){
    this.router.navigateByUrl('/reserved');
  }
  referred(){
    this.router.navigateByUrl('/referred');
  }
  resolved(){
    this.router.navigateByUrl('/resolved');
  }
  cancelled(){
    this.router.navigateByUrl('/cancelled');
  }

  view(view) {
    if(view == 'Reserved')
      this.reserved()
    else if(view == 'Referred')
      this.referred()
    else if(view == 'Resolved')
      this.resolved()
    else if(view == 'Cancelled')
      this.cancelled()
  }

  refresh(){
    this.stats = []
    this.fcmService.initPush();
    this.getStats();
  }

  getStats(){

    let id = this.authService.getUserId()
    let skills = localStorage.getItem('agent')
    if(skills == null || skills == undefined)
      skills = '[]'

    this.authService.request_logged_in(`user-profile/stats`, 'get', {'id':id, 'agent': skills}).then((res: any) => {
      this.stats = res.detail
    },
    (err: any)=>{
      
      this.authService.handleError(err)

    })

  }

}
