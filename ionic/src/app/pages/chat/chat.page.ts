import { Component, OnInit,  ViewChild } from '@angular/core';
import { IonContent, IonInfiniteScroll } from '@ionic/angular';
import { AuthService } from '../../shared/service/auth/auth.service';
import { ToastService } from '../../shared/service/toast/toast.service';
import { UtilsService } from '../../shared/service/utils/utils.service';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.page.html',
  styleUrls: ['./chat.page.scss'],
})
export class ChatPage implements OnInit {

  @ViewChild(IonContent, {read: IonContent, static: false}) content: IonContent;
  @ViewChild(IonInfiniteScroll, { static: true }) infiniteScroll: IonInfiniteScroll;

  chat_list_id: any;
  notifications = []
  data: any;

  mode = (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'agent').toUpperCase()

  creator_id: any;
  respondent_id: any;

  page_number = 1
  num_pages = 1

  newmessage = "";

  ids = {}

  private delay = (time: number) => new Promise(res => setTimeout(() => res, time));

  constructor(public toast: ToastService, public authService: AuthService, public utils: UtilsService, private router: Router, private route: ActivatedRoute,
    ) { 
      
    }

  ngOnInit() {
    
  }
  footerHidden: boolean;

  onScroll(event) {
    // used a couple of "guards" to prevent unnecessary assignments if scrolling in a direction and the var is set already:
    if (event.detail.deltaY > 0 && this.footerHidden) return;
    if (event.detail.deltaY < 0 && !this.footerHidden) return;
    if (event.detail.deltaY > 0) {
      
      this.footerHidden = true;
    } else {
      
      this.footerHidden = false;
    };
  };
  
  scrollToBottomOnInit() {
    setTimeout(() => {
      this.content.scrollToBottom(0);
   }, 1000);
  }

  ionViewWillEnter(){


    this.chat_list_id = localStorage.getItem('chat_list_id')
    this.respondent_id = localStorage.getItem('respondent')
    this.creator_id = localStorage.getItem('creator')
      
    
    this.refresh()
  }

  back(){
    this.router.navigateByUrl( localStorage.getItem('current_second_level_url') != null ? `/`+localStorage.getItem('current_second_level_url') : '/tabs-enduser/enduser-profile' );
  }

  delete(id){
    this.utils.openModal(id, "Cancel").then((data) => {
      if (data != undefined) {
        
          if(data.success){
              
              let formData = new FormData();

              formData.append('id', id)
              formData.append('user', '1')
              formData.append('status_details', data.description)
              formData.append('current_status', 'Deleted')
              formData.append('mode', this.mode)
              
              this.authService.request_logged_in(`chat/delete`, "put", formData).then(()=>{
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

  send(){
    if(this.newmessage.length == 0)
      return this.toast.presentToast("Message is empty")

    const formData = new FormData();
    
    formData.append('chat_list', this.chat_list_id); 
    formData.append('mode', this.mode); 
    formData.append('message', this.newmessage); 
    formData.append('active_creator', 'true'); 
    formData.append('active_respondent', 'true'); 
    
    this.authService.request_logged_in(`chat`, "post", formData).then(()=>{
      this.refresh()
    });
  }

  doInfinite(event) {
    this.getNotifications(true, event, this.chat_list_id);
  }

  async getNotifications(isFirstLoad, event, chat_list_id){

    let url = 'chat'

    if(isFirstLoad)
      url = url + '?page=' + this.page_number + '&_limit=' + this.num_pages;

    await this.authService.request_logged_in(url, 'get', {'chat_list_id': chat_list_id, 'mode': this.mode}).then((results:any)=>{

      results.results = results.results.reverse()
      this.num_pages = results.paginator.num_pages
        
      this.page_number++;

      let more = []
      
      results.results.map((res)=>{
        if(this.ids[res.id] == undefined){
          this.ids[res.id] = ""
          if(isFirstLoad)
            more.push(res)
          else
            this.notifications.push(res);
        }
      })

      
      if(isFirstLoad){
        this.delay(2000);
        event.target.complete();
        this.notifications.unshift(...more);
      }
      else
        this.scrollToBottomOnInit()

    },(err)=>{
      this.authService.handleError(err)
    })

  }

  refresh(){
    this.num_pages = 1
    this.page_number = 1
    this.newmessage = ""
    this.notifications = []
    this.ids = {}
    this.getNotifications(false, "", this.chat_list_id);
  }

}

