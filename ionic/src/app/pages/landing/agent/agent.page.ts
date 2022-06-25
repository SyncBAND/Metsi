import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { NavController } from '@ionic/angular';

import { ToastService } from '../../../shared/service/toast/toast.service';
import { AuthService } from '../../../shared/service/auth/auth.service';

import { Router } from '@angular/router';
import { } from '@angular/core';


@Component({
  selector: 'app-agent',
  templateUrl: './agent.page.html',
  styleUrls: ['./agent.page.scss'],
})
export class AgentPage implements OnInit {

  options = {}

  services = []
  _services = []

  list = []

  constructor(private cdref: ChangeDetectorRef, public router: Router, public authService: AuthService, public nav: NavController, public toast: ToastService) { }

  ngOnInit() {
    
  }

  ngAfterContentChecked() {
    // https://stackoverflow.com/questions/45467881/expressionchangedafterithasbeencheckederror-expression-has-changed-after-it-was#answer-45467987
    this.cdref.detectChanges();
  }

  selected(data) {

    this.services = []
    if(data)
      this.services = data
    
    this._services = []
    for(let i in data){
      this._services.push(parseInt(data[i].split(': ')[0]))
    }

  }

  set_mode() {
    if(this._services.length == 0)
      return this.toast.presentToast('Please select a service')

    localStorage.setItem('mode', 'agent')
    localStorage.setItem('agent', JSON.stringify(this._services))

    return this.nav.navigateRoot('/tabs-agent');
  }

  ionViewWillEnter() {
    localStorage.setItem('current_url', this.router.url)
    this.get('agent-skills', 'get', {'agent_id': this.authService.getUserId()})
  }

  get(url, method, profile) {
    return this.authService.request(url, method, profile).then((res)=>{
      
      this.list = res

      if(res.length > 0){

        this._services = []

        this.services = res[0]['selected_skills']
        
        for(let i in this.services)
          this._services.push(parseInt(this.services[i].split(': ')[0]))
        
      }

    }, (err)=>{

    })
  }

}
