import { Component, OnInit } from '@angular/core';

import { AuthService } from '../shared/service/auth/auth.service';

@Component({
  selector: 'app-tabs-agent',
  templateUrl: './tabs-agent.page.html',
  styleUrls: ['./tabs-agent.page.scss'],
})
export class TabsAgentPage implements OnInit {

  constructor(public authService: AuthService) { }

  ngOnInit() {
    
  }

  ionViewWillEnter() {
    return this.authService.check_mode('agent')
  }

}
