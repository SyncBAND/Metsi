import { Component, OnInit } from '@angular/core';

import { Router } from '@angular/router';

import { AuthService } from '../../../../shared/service/auth/auth.service';
import { ToastService } from '../../../../shared/service/toast/toast.service';
import { UtilsService } from '../../../../shared/service/utils/utils.service';

import { Geolocation} from '@capacitor/core';

@Component({
  selector: 'app-search',
  templateUrl: './search.page.html',
  styleUrls: ['./search.page.scss'],
})
export class SearchPage implements OnInit {

  enquiries = []
  agent = '[]'
  page_number = 1
  num_pages = 1
  watch: any;

  prev_distance = 2
  distance = 2

  agent_mode: string = localStorage.getItem('agent_mode')
  mode = (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'agent').toUpperCase()

  longitude = ''
  latitude = ''

  starttime: any;
  endtime: any;

  constructor(public toast: ToastService, public authService: AuthService, public utils: UtilsService, private router: Router) {
      
  }

  ngOnInit() {
    
  }

  ionViewWillEnter(){

    this.agent = localStorage.getItem('agent')
    this.agent_mode = localStorage.getItem('agent_mode')

    localStorage.setItem('current_url', this.router.url)
      
    this.enquiries = []
    
    if(this.agent == null || this.agent == undefined) {
      localStorage.removeItem('mode')
      this.router.navigateByUrl(`/agent`);
    }
    else
      this.getLocation()
    
  }

  async Enquiries(url: string, method: string, profile: any): Promise <any>  {
    if(this.authService.isLoggedIn)
      return this.authService.request_logged_in(url, method, profile)
    else{
      profile['no_auth'] = true
      return this.authService.request(url, method, profile)
    }
  }

  reserve(id){

    if(this.agent_mode != 'set')
      return this.activate(id)

    const formData = new FormData();

    formData.append('enquiry_id', id)
    formData.append('user', '1')
    formData.append('current_status', 'Reserved')
    formData.append('status_details', 'Reserved')
    formData.append('previous_skill_needed', '1')
    formData.append('agent', this.agent)
    formData.append('mode', this.mode)
              
    this.Enquiries('enquiries-activity', 'post', formData).then((results:any)=>{
      this.refresh()
      this.toast.presentToast('Reserved')
    },(err)=>{
      this.authService.handleError(err)
    })

  }

  interested(id, starttime, endtime){
    
    if(!this.authService.isLoggedIn)
      return this.router.navigateByUrl(`/login`);

    this.starttime = starttime;
    this.endtime = endtime;

    if(this.agent_mode != 'set')
      return this.activate(id)
      
    this.utils.openModal(id, 'Interested', {'starttime':starttime, 'endtime':endtime}).then((data)=>{
      
      if (data != undefined) {
        
        let formData = new FormData();
        if(data.success){
          formData.append('enquiry_id', id)
          formData.append('starttime', data['starttime'])
          formData.append('endtime', data['endtime'])
          formData.append('callout_fee', data['callout_fee'])
          formData.append('mode', this.mode)

          this.authService.request_logged_in('enquiry-interest', 'post', formData).then((res)=>{
            this.toast.presentToast("Interest shown")
          }, (err)=>{
            this.authService.handleError(err)
          })
        }
        else
          this.toast.presentToast('Dismissed')
      }

    }, (err)=>{
      this.authService.handleError(err)
    })
  }

  doInfinite(event) {
    this.getEnquiries(true, event);
  }

  search() {
    if(this.prev_distance != this.distance){
      this.prev_distance = this.distance
      this.enquiries = []
      this.refresh()
    }
  }

	SlideDidChange() {
    
	}
 

  async getLocation() {
    this.latitude = ''
    this.longitude = ''

    this.enquiries = []
    return new Promise(async (resolve, reject) => {
      this.watch = await Geolocation.watchPosition({ timeout: 5000, maximumAge: 0 }, pos => {
        
        Geolocation.clearWatch({id: this.watch});
        if(pos){
          this.latitude = pos.coords.latitude.toString();
          this.longitude = pos.coords.longitude.toString();
          this.refresh()
          resolve(pos)
        }
        else{
          this.toast.presentToast("Location is needed. Your location permission might be off.")
        }
        this.watch = null; 

      })
    })
  }

  getEnquiries(isFirstLoad, event){

    let url = 'enquiries'

    if(isFirstLoad)
      url = url + '?page=' + this.page_number + '&_limit=' + this.num_pages;
    
    if(this.latitude == '')
      return this.toast.presentToast('We couldn\'t get your location. Please try again')

    let location = "POINT("+this.latitude + " " + this.longitude + ")"
        
    this.Enquiries(url, 'get', {'agent': this.agent, 'location': location, 'distance': this.distance}).then((results:any)=>{

      this.num_pages = results.paginator.num_pages
      if(isFirstLoad)
        event.target.complete();
        
      this.page_number++;

      results.results.map((res)=>{
        res['created'] = new Date(res['created'])
        res['modified'] = new Date(res['modified'])
        this.enquiries.push(res)
      })

    },(err)=>{

        this.authService.handleError(err)
          
    })

  }

  // first implementation - requires use of agent pin 
  // activate(id){
        
  //   this.utils.openModal(id, 'Activate').then((data)=>{
      
  //     if (data != undefined) {
        
  //       let formData = new FormData();
  //       if(data.success){
  //         formData.append('enquiry_id', id)
  //         formData.append('pin', data['pin'])
  //         formData.append('agent', this.agent)
  //         formData.append('mode', this.mode)

  //         this.authService.request_logged_in('agent/activate', 'post', formData).then((res)=>{
  //           if(res.success){
  //             // localStorage.setItem('agent_mode', 'set')
  //             this.agent_mode = 'set'
  //             this.toast.presentToast(res.detail)
  //           }
  //           else{
  //             this.toast.presentToast('Incorrect pin')
  //           }
  //         }, (err)=>{
  //           this.authService.handleError(err)
  //         })
  //       }
  //       else
  //         this.toast.presentToast('Dismissed')
  //     }

  //   }, (err)=>{
  //     this.authService.handleError(err)
  //   })

  // }

  activate(id){
    
    this.authService.request_logged_in('agent/is_active', 'get', {'agent': this.agent}).then((result)=>{
      
      if(!result.success){
        this.toast.presentToast(result.detail)
        this.router.navigateByUrl(`/tabs-agent/agent-profile`);
      }
      else{
        // localStorage.setItem('agent_mode', 'set')
        this.agent_mode = 'set'
        this.reserve(id)
      }

    }, (err)=>{
      this.authService.handleError(err)
    })
    
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
              formData.append('agent', this.agent)
              formData.append('mode', this.mode)
              
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
    this.enquiries = []
    this.num_pages = 1
    this.page_number = 1
    setTimeout(()=>{
      this.getEnquiries(false, "");
    }, 500)
  }

}
 