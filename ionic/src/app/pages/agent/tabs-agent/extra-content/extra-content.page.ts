import { Component, OnInit } from '@angular/core';

import { Router } from '@angular/router';

import { AuthService } from '../../../../shared/service/auth/auth.service';
import { ToastService } from '../../../../shared/service/toast/toast.service';
import { UtilsService } from '../../../../shared/service/utils/utils.service';

import { Plugins } from '@capacitor/core';

const { Browser } = Plugins;

@Component({
  selector: 'app-extra-content',
  templateUrl: './extra-content.page.html',
  styleUrls: ['./extra-content.page.scss'],
})
export class ExtraContentPage implements OnInit {

  tutorials = []
  agent = '[]'
  page_number = 1
  num_pages = 1

  constructor(public toast: ToastService, public authService: AuthService, public utils: UtilsService, private router: Router
    ) {
      
  }

  ngOnInit() {
    
  }

  ionViewWillEnter(){
    this.agent = localStorage.getItem('agent')
    localStorage.setItem('current_url', this.router.url)
    this.refresh()
  }

  async ExtraContent(url: string, method: string, profile: any): Promise <any>  {
    if(this.authService.isLoggedIn)
      return this.authService.request_logged_in(url, method, profile)
    else{
      profile['no_auth'] = true
      return this.authService.request(url, method, profile)
    }
  }

	SlideDidChange() {
    
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

                    formData.append('extra_content', id)
                    formData.append('previous_skill_needed', '1')
                    formData.append('rating', rating.toString())
                    formData.append('review', data.description)
                    formData.append('mode', (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'agent').toUpperCase())
                    
                    this.authService.request_logged_in(`enquiries-activity`, "post", formData).then(()=>{
                        this.refresh()
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

  doInfinite(event) {
    this.getExtraContent(true, event);
  }

  getExtraContent(isFirstLoad, event){

    let url = 'extra-content/tutorials'

    if(isFirstLoad)
      url = url + '?page=' + this.page_number + '&_limit=' + this.num_pages;

    this.ExtraContent(url, 'get', {'agent': this.agent}).then((results:any)=>{

      this.num_pages = results.paginator.num_pages
      if(isFirstLoad)
        event.target.complete();
        
      this.page_number++;

      results.results.map((res)=>{
        res['created'] = new Date(res['created'])
        res['modified'] = new Date(res['modified'])
        this.tutorials.push(res)
      })

    },(err)=>{

        this.authService.handleError(err)
          
    })

  }

  async visit(id, url) {

      this.ExtraContent(`extra-content/${id}/interact`, 'get', {'agent': this.agent}).then((results:any)=>{
        Browser.open({ url: url });
      },(err)=>{
        Browser.open({ url: url });
      })

  }

  refresh(){
    this.tutorials = []
    this.num_pages = 1
    this.page_number = 1
    this.getExtraContent(false, "");
  }

}
 