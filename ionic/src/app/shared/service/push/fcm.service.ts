import { Injectable } from '@angular/core';
import {
  Plugins,
  PushNotification,
  PushNotificationToken,
  PushNotificationActionPerformed
} from '@capacitor/core';
import { Router } from '@angular/router';

import { Platform } from '@ionic/angular';
 
import { AuthService } from '../../../shared/service/auth/auth.service';
import { ToastService } from '../../../shared/service/toast/toast.service';
import { UtilsService } from '../../../shared/service/utils/utils.service';

const { PushNotifications } = Plugins;
const { LocalNotifications } = Plugins;
 
@Injectable({
  providedIn: 'root'
})
export class FcmService {
 
  constructor(private authService: AuthService, public platform: Platform, private router: Router, public toast: ToastService, public utils: UtilsService) { }
 
  initPush() {
    
      if (this.utils.platformIs !== 'browser') {

        let permission_notifications = localStorage.getItem('push_notification')

        // if(permission_notifications == null || permission_notifications == 'set'){

        //   if(permission_notifications == 'set'){
        //     PushNotifications.register();
        //     this.registerPush();
        //   }
        //   else{
        //     this.utils.showAlert('Push Notifications', 'The reason why we send notifications is to make you aware of upcoming bookings and messages sent').then(()=>{
        //         // Register with Apple / Google to receive push via APNS/FCM
        //         localStorage.setItem('push_notification', 'set')
        //         PushNotifications.register();
        //         // this.registerPush();
        //     })
        //   }
        // }

      }
  }
 
  private registerPush() {

    PushNotifications.addListener(
      'registration',
      (token: PushNotificationToken) => {
        let os = ''
        if (this.platform.is('android')) {
          os = 'android'.toUpperCase();
        } else if (this.platform.is('ios')) {
          os = 'ios'.toUpperCase();
        }
        else
          return

        if( localStorage.getItem('push_notification_registered') != 'true' ){

          let data = {'registration_id': token.value, 'platform': os, 'name': os, 'user': 1}
          this.authService.request_logged_in('register-device', 'post', data).then(()=>{
            localStorage.setItem('push_notification_registered', 'true')
          })

        }
        
      }
    );
 
    PushNotifications.addListener('registrationError', (error: any) => {
      //this.utils.showAlert("err", 'Error: ' + JSON.stringify(error));
    });
 
    PushNotifications.addListener(
      'pushNotificationReceived',
      async (notification: PushNotification) => {
        
        const data = notification.data;

        if(data.message_id != null || data.message_id != undefined){
          this.authService.request_logged_in(`message-recieved/delivered`, 'patch', {'type': 'PUSH_NOTIFICATION', 'api_message_id': data.message_id})
        }

        if(data.type == 'chat'){
          if(this.router.url == '/chat'){
            this.router.navigateByUrl('/home');
          }
          localStorage.setItem('mode', data.mode.toLowerCase())
          localStorage.setItem('chat_list_id', data.chat_list_id)
          localStorage.setItem('respondent', data.respondent)
          localStorage.setItem('creator', data.creator)
          this.router.navigateByUrl('/chat');
        }
        else if(data.type == 'reserved'){
          localStorage.setItem('mode', data.mode.toLowerCase())
          this.router.navigateByUrl('/reserved');
        }
        else if(data.type == 'interest'){
          localStorage.setItem('mode', data.mode.toLowerCase())
          localStorage.setItem('enquiry_id', data.id)
          this.router.navigateByUrl('/interests');
        }
        else if(data.type == 'calender'){
          localStorage.setItem('mode', data.mode.toLowerCase())
          this.router.navigateByUrl('/calendar');
        }
        else{
          this.utils.showAlert('Note', data.message)
        }

        await LocalNotifications.schedule({
          notifications: [
            {
              title: "",
              body: data.message,
              id: data.message_id,
              sound: null,
              attachments: null,
              actionTypeId: "",
              extra: null
            }
          ]
        });

      }
    );
 
    PushNotifications.addListener(
      'pushNotificationActionPerformed',
      async (notification: PushNotificationActionPerformed) => {

        const data = notification.notification.data;
        
        if(data.message_id != null || data.message_id != undefined){
          this.authService.request_logged_in(`message-recieved/delivered`, 'patch', {'type': 'PUSH_NOTIFICATION', 'api_message_id': data.message_id})
        }

        //this.utils.showAlert('Action performed', JSON.stringify(notification.notification))
        if(data.type == 'chat'){
          if(this.router.url == '/chat'){
            this.router.navigateByUrl('/home');
          }
          localStorage.setItem('mode', data.mode.toLowerCase())
          localStorage.setItem('chat_list_id', data.chat_list_id)
          localStorage.setItem('respondent', data.respondent)
          localStorage.setItem('creator', data.creator)
          this.router.navigateByUrl('/chat');
        }
        else if(data.type == 'reserved'){
          localStorage.setItem('mode', data.mode.toLowerCase())
          this.router.navigateByUrl('/reserved');
        }
        else if(data.type == 'interest'){
          localStorage.setItem('mode', data.mode.toLowerCase())
          localStorage.setItem('enquiry_id', data.id)
          this.router.navigateByUrl('/interests');
        }
        else if(data.type == 'calender'){
          localStorage.setItem('mode', data.mode.toLowerCase())
          this.router.navigateByUrl('/calendar');
        }
        else{
          this.utils.showAlert('Note', data.message)
        }

      }
    );
  }
}
