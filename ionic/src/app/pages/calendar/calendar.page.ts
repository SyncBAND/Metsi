import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from '../../shared/service/auth/auth.service';
import { ToastService } from '../../shared/service/toast/toast.service';
import { UtilsService } from '../../shared/service/utils/utils.service';

import { CalendarOptions, FullCalendarComponent } from '@fullcalendar/angular'; // useful for typechecking

@Component({
  selector: 'app-calendar',
  templateUrl: './calendar.page.html',
  styleUrls: ['./calendar.page.scss'],
})
export class CalendarPage implements OnInit {

  @ViewChild('calendar') calendarComponent: FullCalendarComponent;

  mode = (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'agent').toUpperCase()

  calendarOptions: CalendarOptions;
  calendarApi;

  currentDate = new Date()

  constructor(public toast: ToastService, public utils: UtilsService, public authService: AuthService, private router: Router) { }

  ngOnInit() {
  }

  ionViewWillEnter() {
    this.calendarApi = this.calendarComponent.getApi();
    this.calendar()
    this.refresh()
  }

  calendar(){

    this.calendarOptions = {
      height: 'auto',
      expandRows: true,
      //dateClick: this.handleDateClick.bind(this),
      headerToolbar: {
        left: 'prev,next',
        right: 'dayGridMonth,listWeek,timeGridWeek'
      },
      footerToolbar:{
          left: '',
          center: 'title',
          right: ''
      },
      views: {
          dayGridMonth: { buttonText: 'Month' },
          listWeek: { buttonText: 'Week' },
          timeGridWeek: { buttonText: 'Time' },
      },
      initialView: 'dayGridMonth',
      initialDate: new Date(),
      navLinks: true,
      editable: false,
      nowIndicator: true,
      dayMaxEvents: true,
      events: [],
      selectable: true,
      displayEventTime: false,
      eventClick: this.handleEvent.bind(this),
    };
    
  }

  handleDateClick(arg) {
    alert('date click! ' + arg.dateStr)
  }

  handleEvent(arg){
    let data = arg.event._def.extendedProps.data
    data['name'] = data.title
    delete data['title']
    this.utils.openModal(1, 'Calendar', arg.event._def.extendedProps.data).then((res)=>{
      if(res.success){
        this.rate(data.enquiry_id)
      }
    })
  }

  init(){

    this.authService.request_logged_in('enquiry-interest/getmonthdata', 'get', {'mode':this.mode, 'month': this.currentDate.getMonth()+1, 'year': this.currentDate.getFullYear()}).then((results:any)=>{
      
      results.map((res)=>{
        
        let ev = this.calendarApi.getEventById(res.id)
        if(ev != null)
          ev.remove()

        this.calendarApi.addEvent({
          start:res.starttime, 
          //end:res.endtime,
          title: res.title,
          id: res.id,
          data: res
        })
          
      })

    },(err)=>{

      this.authService.handleError(err)

    })

  }

  refresh(){
    this.currentDate = this.calendarApi.view.currentStart;
    this.init()
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
                    data['rating'] = rating;

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
                        this.refresh()
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

  back(){
    this.router.navigateByUrl( localStorage.getItem('current_url') != null ? `/`+localStorage.getItem('current_url') : '/tabs-enduser/enduser-profile' );
  }

}
