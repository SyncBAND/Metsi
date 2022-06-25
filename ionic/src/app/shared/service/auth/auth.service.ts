import { Injectable } from '@angular/core';
import { User } from '../../user';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { ToastService } from '../../../shared/service/toast/toast.service';

import { NavController } from '@ionic/angular';

@Injectable({
  providedIn: 'root'
})

export class AuthService {

    //endpoint: string = 'http://102.130.117.220/api';
    endpoint: string = 'https://metsiapp.co.za/api';
    //endpoint: string = 'http://102.130.112.252:8001/api';
    
    headers = new HttpHeaders();
    currentUser = {};

    constructor(
        public http: HttpClient,
        private nav: NavController,
        public router: Router,
        public toast: ToastService
    ) {
        this.headers['Content-Type'] = "application/json; charset=UTF-8"
        this.headers["Access-Control-Allow-Origin"] = "*"
        this.headers["Access-Control-Allow-Methods"] = "POST, PUT, OPTIONS, DELETE, GET"
        this.headers['Access-Control-Allow-Headers'] = "Origin, X-Requested-With, Content-Type, Authorization, Accept, x-access-token"
        this.headers['Access-Control-Allow-Credentials'] = "true"
        
        this.headers['Accept'] = 'application/json';

    }

    // Sign-up
    signUp(user: User): Observable<any> {
        let api = `${this.endpoint}/auth/register-user/`;

        let agent = localStorage.getItem('agent');
        if(agent != undefined){
            user['agent'] = agent
            user['mode'] = 'AGENT'
        }

        return this.http.post(api, user)
          .pipe(
            catchError((err)=>{
                this.handleError(err);
                return throwError(err);
            })
          )
    }

    resetPassword(user: User): Observable<any> {
        let api = `${this.endpoint}/auth/reset-password/`;
        return this.http.post(api, user)
          .pipe(
            catchError((err)=>{
                this.handleError(err);
                return throwError(err);
            })
          )
    }
  
    parseJwt (token: string) {
        let base64Url = token.split('.')[1];
        let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        let jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));

        return JSON.parse(jsonPayload);
    };

    getValues(object) {
        let values = '';
        
        if (object.constructor !== Object) 
          return JSON.stringify(object)

        let count = Object.keys(object).length;
        for (var key in object) { 
            if (object.hasOwnProperty(key)) {
                if (count > 1)
                    values = values + key + ': ' + object[key] + '\n' ;
                else
                    values = values + key + ': ' + object[key] ;
            } 
            count--;
        } 

        return values
    } 

    // Sign-in
    signIn(user: User) {
        return this.http.post<any>(`${this.endpoint}/auth/login/`, user)
          .subscribe((res: any) => {
              this.setItems(res);
              this.nav.navigateRoot(localStorage.getItem('current_url') != null ? "/"+localStorage.getItem('current_url') : '/home');
          },
          (err: any)=>{
              this.handleError(err)
          })
    }

    getToken() {
        return localStorage.getItem('access_token');
    }

    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    }

    getUserId() {
        return localStorage.getItem('user_id');
    }

    get isLoggedIn(): boolean {
        let authToken = this.getToken();
        let authRefreshToken = this.getRefreshToken();
        let authUserId = this.getUserId();
        return (authToken !== null && authRefreshToken !== null && authUserId !== null) ? true : false;
    }

    async logout(path: string) {
      
        if (this.isLoggedIn) {
          
          this.refreshToken().subscribe(()=>{

            return this.http.post<any>(`${this.endpoint}/${path}/${this.getUserId()}/`, {'refresh': this.getRefreshToken(), 'access': this.getToken()}, { headers: this.headers })
              .subscribe((res: any) => {
                  this.removeItems()
              },
              (err: any)=>{
                  return this.removeItems()
              })
            },
            (err)=>{
                return this.removeItems()
            }

          )

        }
        else{
            return this.removeItems()
        }
      
    }

    // Error 
    handleError(error: HttpErrorResponse) {
        let msg = '';
        
        if (error.error.messages) {
            // client-side error
            msg = error.error.messages[0]['message'];
        }
        else if(error.error.detail) {
            msg = error.error.detail
        }
        else if(error.error) {
            msg = this.getValues(error.error)
        }
        else {
            // server-side error
            msg = `Error Code: ${error.status}\nMessage: ${error.message}`;
        }

        if(msg == "Token is blacklisted" || msg == "User not found"){
            return this.logout('logout')
        }
        else if(msg == "Token is invalid or expired" || msg == "Token 'exp' claim has expired"){
          return this.logout('logout')
        }
        this.toast.presentToast(msg)
        //this.toast.presentToast(JSON.stringify(error))
        
    }

    refreshToken(): Observable<any> {
        return this.http.post<any>(`${this.endpoint}/auth/login/refresh/`, {'refresh': this.getRefreshToken()})
          .pipe(
            map((res)=>{
                // console.log(res)
                this.setItems(res);

                this.headers['Content-Type'] = "application/json"
                this.headers['Authorization'] = "Bearer " + this.getToken()
            }),
            catchError((err)=>{
                // console.log("1: "+ JSON.stringify(err))
                this.handleError(err);
                return throwError(err);
            })
          )
    }

    setItems(res: any) {

        let user_id = this.parseJwt(res.access)['user_id']

        if(res.refresh)
            localStorage.setItem('refresh_token', res.refresh)

        localStorage.setItem('access_token', res.access)
        localStorage.setItem('refresh_counter', "0")
        localStorage.setItem('user_id', user_id)

        return user_id

    }

    async request_logged_in(url: string, method: string, profile: any): Promise <any>  {
        
        return await new Promise<any>((resolve, reject) => {
            this.refreshToken().subscribe((res: any) => {
                resolve(this.request(url, method, profile))
            }, (err)=> {
                reject(err);
            })
        });

    }

    async request(url: string, method: string, profile: any): Promise <any>  {

        profile['mode'] = (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'agent').toUpperCase()
    
        return await new Promise<any>((resolve, reject) => {
              
            let api = `${this.endpoint}/${url}/`;
            
            if(method == 'get')
                this.http[method](api, { headers: this.headers, params: profile }).subscribe(
                    (res: any) => {
                        resolve(res|| {})
                    },(err)=>{
                        reject(err);
                    }
                )
            else
                this.http[method](api, profile, { headers: this.headers }).subscribe(
                    (res: any) => {
                        resolve(res|| {})
                    },(err)=>{
                        reject(err);
                    }
                )
    
        });
    
    }

    removeItems() {

        localStorage.removeItem('access_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('refresh_counter');
        
        localStorage.removeItem('mode');
        localStorage.removeItem('agent');
        localStorage.removeItem('agent_mode')

        localStorage.removeItem('email')
        localStorage.removeItem('email_verified')

        localStorage.removeItem('rating')
        
        localStorage.removeItem('current_url');
        localStorage.removeItem('current_first_level_url')
        localStorage.removeItem('current_second_level_url')

        // chalist_object_id | could be support or enquiry id
        localStorage.removeItem('chat_list_object_id')
        localStorage.removeItem('chat_list_content_type')
        // -- //

        localStorage.removeItem('profile_loaded')

        // chat
        localStorage.removeItem('chat_list_id')
        localStorage.removeItem('respondent')
        localStorage.removeItem('creator')
        // -- //

        localStorage.removeItem('resolving')

        localStorage.removeItem('push_notification')
        localStorage.removeItem('camera_permission')
        localStorage.removeItem('location_permission')

        localStorage.removeItem('push_notification_registered')
        
        this.nav.navigateRoot('/home');

    }

    check_mode(data){
        let mode = localStorage.getItem('mode')
        if(data != null)
            if(mode == data)
                return

        if(mode != null){
            return this.nav.navigateRoot('/tabs-' + mode);
        }
        else{
            return this.nav.navigateRoot('/home');
        }
    }
    
}