import { Component, OnInit } from '@angular/core';

import { AuthService } from '../../../../shared/service/auth/auth.service';
import { FcmService } from '../../../../shared/service/push/fcm.service';
import { ToastService } from '../../../../shared/service/toast/toast.service';

import { Router } from '@angular/router';

@Component({
  selector: 'app-enquiries',
  templateUrl: './enquiries.page.html',
  styleUrls: ['./enquiries.page.scss'],
})
export class EnquiriesPage implements OnInit {

  enquiries = []
  pin = '';
  stats = []

  constructor(public fcmService: FcmService, public toast: ToastService, public authService: AuthService, private router: Router
    ) { 
      
  }

  ngOnInit() {
    
  }

  ionViewWillEnter(){
    localStorage.setItem('current_url', this.router.url)
    
    if(this.authService.isLoggedIn)
      this.refresh()
  }

  pending(){
    this.router.navigateByUrl('/pending');
  }
  approved(){
    this.router.navigateByUrl('/approved');
  }
  resolved(){
    this.router.navigateByUrl('/resolved');
  }
  cancelled(){
    this.router.navigateByUrl('/cancelled');
  }

  view(view) {
    if(view == 'Pending')
      this.pending()
    else if(view == 'Approved')
      this.approved()
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

    this.authService.request_logged_in(`user-profile/stats`, 'get', {'id':id}).then((res: any) => {
      this.stats = res.detail
    },
    (err: any)=>{
      
      this.authService.handleError(err)

    })

  }

}
