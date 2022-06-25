import { Component, OnInit } from '@angular/core';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";

import { Router } from '@angular/router';

import { ToastService } from '../../shared/service/toast/toast.service';
import { AuthService } from '../../shared/service/auth/auth.service';

@Component({
  selector: 'app-edit-profile',
  templateUrl: './edit-profile.page.html',
  styleUrls: ['./edit-profile.page.scss'],
})
export class EditProfilePage implements OnInit {

  updateProfileForm: FormGroup;
  isSubmitted = false;

  constructor(public authService: AuthService, public formBuilder: FormBuilder, public router: Router, public toast: ToastService) { }

  ngOnInit() {

    let res = localStorage.getItem('profile_info')
    let name = '', last = '', cell = ''

    if(res){
      res = JSON.parse(res)
      name = res['first_name']
      last = res['last_name']
      cell = res['cell']
    }

    this.updateProfileForm = this.formBuilder.group({
      first_name: [name, [Validators.required, Validators.minLength(2)]],
      last_name: [last, [Validators.required, Validators.minLength(2)]],
      cell: [cell, [Validators.required, Validators.pattern('^[0-9]+$')]],
    })

  }

  get errorControl() {
      return this.updateProfileForm.controls;
  }

  back(){
    this.router.navigateByUrl( localStorage.getItem('current_url') != null ? `/`+localStorage.getItem('current_url') : '/tabs-enduser/enduser-profile' );
  }
  
  moveFocus(nextElement) {
      nextElement.setFocus();
  }

  edit() {

    this.isSubmitted = true;
    if (!this.updateProfileForm.valid) {
      return false;
    } else {
      this.isSubmitted = false;

      let id = this.authService.getUserId()
      
      this.authService.request_logged_in(`update-profile/${id}`, 'patch', this.updateProfileForm.value).then((res) => {
        localStorage.setItem('profile_info', JSON.stringify(res))
        this.toast.presentToast("Details updated.")
        this.back()
      }, (err)=>{
        
        this.authService.handleError(err)

      })

    }
    
  }

}

