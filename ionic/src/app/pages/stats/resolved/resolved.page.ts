import { Component, OnInit } from '@angular/core';

import { AuthService } from '../../../shared/service/auth/auth.service';
import { ToastService } from '../../../shared/service/toast/toast.service';
import { UtilsService } from '../../../shared/service/utils/utils.service';

import { Router } from '@angular/router';

import { Plugins } from '@capacitor/core';

const { Browser } = Plugins;

@Component({
  selector: 'app-resolved',
  templateUrl: './resolved.page.html',
  styleUrls: ['./resolved.page.scss'],
})
export class ResolvedPage implements OnInit {

  page_number = 1
  num_pages = 1
  
  bookings = []

  mode = (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'agent').toUpperCase()

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
    this.getResolved(true, event);
  }

  chat(id){
    localStorage.setItem('chat_list_object_id', id)
    localStorage.setItem('chat_list_content_type', 'enquiries')
    this.router.navigateByUrl('/chat-list');
  }

  async rate(id){

    this.utils.openModal(id, "Rate").then((data) => {
      if (data != undefined) {
        
          if(data.success){
              if(data.rating){
                  let rating = parseInt(localStorage.getItem('rating'))
                  if( rating == 0 )
                      this.toast.presentToast("Rating was not set")
                  else{
                    let formData = new FormData();

                    formData.append('object_id', id)
                    formData.append('content_type', 'enquiry')
                    formData.append('rating', rating.toString())
                    formData.append('review', data.details)
                    formData.append('mode', this.mode)
                    
                    let url = ''
                    if(this.mode == 'ENDUSER')
                      url = 'agent/rate'
                    else
                      url = 'enduser/rate'
                    
                    this.authService.request_logged_in(url, "post", formData).then(()=>{
                        this.toast.presentToast('Rating was successful')
                    },(err)=>{
                        this.authService.handleError(err);
                    });
                  }
              }
              else
                this.toast.presentToast("No rating")
          }
          else
              this.toast.presentToast('Dismissed')

      }
    });

  }

  async location(lat, lng){
    await Browser.open({ url: "https://www.google.com/maps/dir/?api=1&origin=" + lat + "," + lng + "&destination=" + lat+ "," + lng + "&travelmode=driving"});
  }

  getResolved(isFirstLoad, event){

    let url = 'enquiries/resolved'

    if(isFirstLoad)
      url = url + '?page=' + this.page_number + '&_limit=' + this.num_pages;

    this.authService.request_logged_in(url, 'get', {'contractor': '10'}).then((results:any)=>{

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
    this.getResolved(false, "");
  }

}
