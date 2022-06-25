import { Component, OnInit } from '@angular/core';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";
import { AuthService } from '../../../shared/service/auth/auth.service';
import { ToastService } from '../../../shared/service/toast/toast.service';
import { UtilsService } from '../../../shared/service/utils/utils.service';

import { Router } from '@angular/router';
 
import { ModalController, NavParams } from '@ionic/angular';

import { Plugins } from '@capacitor/core';
import { CameraResultType, CameraSource } from '@capacitor/core';
const { Camera } = Plugins;

@Component({
  selector: 'app-modal-popup',
  templateUrl: './modal-popup.page.html',
  styleUrls: ['./modal-popup.page.scss'],
})
export class ModalPopupPage implements OnInit {

  modalForm: FormGroup;
  rateForm: FormGroup;
  interestedForm: FormGroup;
  referredForm: FormGroup;

  isSubmitted = false;

  platform = "ios"

  id: number;
  rating: number;
  title: string;

  agent_pin = '';

  calendar_data = {}
  mindate;

  mode = (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'agent').toUpperCase()

  list_of_skills = []

  constructor(
    private modalController: ModalController,
    private navParams: NavParams,
    public formBuilder: FormBuilder,
    public authService: AuthService,
    public toast: ToastService,
    public router: Router,
    public utils: UtilsService) { }

  ngOnInit() {
    this.id = this.navParams.data.id;
    this.title = this.navParams.data.title;
    this.rating = this.navParams.data.rating;

    this.calendar_data = this.navParams.data;

    this.modalForm = this.formBuilder.group({
        description: ['', [Validators.required, Validators.minLength(6)]],
    })

    this.rateForm = this.formBuilder.group({
        details: ['']
    })

    this.referredForm = this.formBuilder.group({
        details: ['', [Validators.required, Validators.minLength(6)]],
        skill: ['', [Validators.required]],
        area: ['', [Validators.required]],
        position: ['', [Validators.required]],
        severity: ['', [Validators.required]]
    })

    if(this.title == 'Interested'){
        let starttime = this.navParams.data.starttime;
        let endtime= this.navParams.data.endtime;
        this.mindate = new Date().toISOString()
        this.interestedForm = this.formBuilder.group({
            callout_fee: ['', [Validators.required, Validators.pattern('^[0-9]+$')]],
            starttime: [new Date(starttime).toISOString()],
            endtime: [new Date(endtime).toISOString()]
        })
    }

    if(this.title == 'Refer'){
      this.get_skills('agent-skills', 'get', {'mode': this.mode})
    }
  }

  get errorControl() {
      return this.modalForm.controls;
  }

  ratings(data){
    if( data['total_number'] == 0)
      return 0
    return ( ((data['total_sum'] / 5)/data['total_number']) * 100 ).toFixed(2)
  }

  closeModal() {
    this.modalController.dismiss({'success':false});
  }

  submit() {

      this.isSubmitted = true;

      if (!this.modalForm.valid) {
        return false;
      } else {
        this.isSubmitted = false;

        let data = this.modalForm.value
        data['success'] = true
        data['rating'] = false

        this.modalForm.controls.description.reset()
        this.modalController.dismiss(data);
      }
      
  }

  rate(){
    let data = this.rateForm.value
    data['success'] = true
    data['rating'] = true

    this.rateForm.controls.details.reset()
    this.modalController.dismiss(data);
  }

  interested(){
    if( isNaN(this.interestedForm.controls.callout_fee.value) )
      return this.toast.presentToast("Call out is incorrect.")
      
    if( this.interestedForm.controls.callout_fee.value < 0)
          return this.toast.presentToast("Call out is incorrect.")
    if( this.interestedForm.controls.endtime.value < this.interestedForm.controls.starttime.value)
          return this.toast.presentToast("Start time is after the end time. Please correct.")
    
    let data = this.interestedForm.value
    data['success'] = true

    this.rateForm.controls.details.reset()
    this.modalController.dismiss(data);
  }

  get_activation_pin(){

    let agent = localStorage.getItem('agent')
    
    this.authService.request_logged_in('agent/get_activation_key', 'get', {'agent': agent}).then((result)=>{
      
      this.toast.presentToast(result.detail)
      if(!result.email){
        this.modalController.dismiss();
        this.router.navigateByUrl(`/tabs-agent/agent-profile`);
      }

    }, (err)=>{
      this.authService.handleError(err)
    })
    
  }

  get_skills(url, method, profile) {
    return this.authService.request(url, method, profile).then((res)=>{
      
      this.list_of_skills = res

    }, (err)=>{

    })
  }

  refer(){
    if(this.referredForm.controls.details.value == '')
      return this.toast.presentToast('Details is needed')
    else if(this.referredForm.controls.details.value.length < 10)
      return this.toast.presentToast('Details is too short')
      else if(this.referredForm.controls.area.value == '')
        return this.toast.presentToast('Area is empty')
    else if(this.referredForm.controls.position.value == '')
      return this.toast.presentToast('Position is empty')
    else if(this.referredForm.controls.severity.value == '')
      return this.toast.presentToast('Severity is needed')
    else if(this.referredForm.controls.skill.value == '')
      return this.toast.presentToast('Skill is needed')

    let data = this.referredForm.value
    data['success'] = true

    if(this.referredForm.controls.image_1){
      data['image_1'] = this.referredForm.controls.image_1.value
      data['image_1_name'] = this.referredForm.controls.image_1.value.name
    }
    if(this.referredForm.controls.image_2){
      data['image_2'] = this.referredForm.controls.image_2.value
      data['image_2_name'] = this.referredForm.controls.image_2.value.name
    }
    if(this.referredForm.controls.image_3){
      data['image_3'] = this.referredForm.controls.image_3.value
      data['image_3_name'] = this.referredForm.controls.image_3.value.name
    }
    if(this.referredForm.controls.image_4){
      data['image_4'] = this.referredForm.controls.image_4.value
      data['image_4_name'] = this.referredForm.controls.image_4.value.name
    }

    this.referredForm.controls.details.reset()
    this.referredForm.controls.skill.reset()
    this.referredForm.controls.area.reset()
    this.referredForm.controls.position.reset()
    this.referredForm.controls.severity.reset()

    if(this.referredForm.controls.image_1)
      this.referredForm.removeControl('image_1')
    if(this.referredForm.controls.image_2)
      this.referredForm.removeControl('image_2')
    if(this.referredForm.controls.image_3)
      this.referredForm.removeControl('image_3')
    if(this.referredForm.controls.image_4)
      this.referredForm.removeControl('image_4')

    this.modalController.dismiss(data);
  }

  event = {
    photo_1: '../../../../assets/camera.png',
    photo_2: '../../../../assets/camera.png',
    photo_3: '../../../../assets/camera.png',
    photo_4: '../../../../assets/camera.png',
  }

  severity = [
    "Excessive",
    "Worsening",
    "Moderate",
    "None",
  ]

  positions = [
    "Busy road",
    "Not so busy road",
    "Pavement"
  ]

  areas = [
    "Residential area",
    "Business district",
    "Isolated area",
    "Other",
  ]

  getRndInteger(min, max) {
    return Math.floor(Math.random() * (max - min) ) + min;
  }

  dataURLtoFile(dataurl, filename) {
    let arr = dataurl.split(','),
        mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]),
        n = bstr.length,
        u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, {type: mime});
  }

  async capture(position){

    if(localStorage.getItem('camera_permission') == null)
      this.utils.showAlert('Camera and storage Permission', 'The reason why we need your camera is for you take images for your bookings')
      
     try{
       localStorage.setItem('camera_permission', 'set')

       const image = await Camera.getPhoto({
         quality: 50,
         allowEditing: true,
         resultType: CameraResultType.DataUrl,
         source: CameraSource.Prompt,
       });
       
       // image.webPath will contain a path that can be set as an image src.
       // You can access the original file using image.path, which can be
       // passed to the Filesystem API to read the raw data of the image,
       // if desired (or pass resultType: CameraResultType.Base64 to getPhoto)
       
       // Can be set to the src of an image now
       let imageUrl = image.dataUrl;
       
       if(position == '1'){
         this.event['photo_1'] = imageUrl
         this.referredForm.addControl('image_1', this.formBuilder.control(''))
         this.referredForm.controls['image_1'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
       }
       else if(position == '2'){
         this.event['photo_2'] = imageUrl

         this.referredForm.addControl('image_2', this.formBuilder.control(''))
         this.referredForm.controls['image_2'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
       }
       else if(position == '3'){
         this.event['photo_3'] = imageUrl
         this.referredForm.addControl('image_3', this.formBuilder.control(''))
         this.referredForm.controls['image_3'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
       }
       else if(position == '4'){
         this.event['photo_4'] = imageUrl
         this.referredForm.addControl('image_4', this.formBuilder.control(''))
         this.referredForm.controls['image_4'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
       }
     }
     catch{
       this.selectImage(position);
     }
   }

   /**
   * @public
   * @method selectImage
   * @param event  {any}        The DOM event that we are capturing from the File input field
   * @description               Web only - Returns the image selected by the user and renders 
   *                            this to the component view
   * @return {none}
   */
  selectImage(position: string) : void
  {

    const a = document.createElement("input");
    const event = document.createEvent('MouseEvents');
    event.initEvent('click', true, true);
    a['type'] = 'file' ;
    a.dispatchEvent(event);
    
    localStorage.setItem('camera_permission', 'set')
      
    a.addEventListener('change', (evt: any) => {
        const files = evt.target.files as File[];
        // for (let i = 0; i < files.length; i++) {
        //    this.items.push(files[i]);
        // }
        const file = (evt.target as HTMLInputElement).files[0];
        const pattern = /image-*/;
        const reader = new FileReader();
        
        if (!file.type.match(pattern)) {
          this.toast.presentToast('File format not supported');
          return;
        }

        reader.onload = () => {
          if(position == '1'){
            this.event['photo_1'] = reader.result.toString()
            this.referredForm.addControl('image_1', this.formBuilder.control(''))
            this.referredForm.controls['image_1'].setValue(file)
          }
          else if(position == '2'){
            this.event['photo_2'] = reader.result.toString()
            this.referredForm.addControl('image_2', this.formBuilder.control(''))
            this.referredForm.controls['image_2'].setValue(file)
          }
          else if(position == '3'){
            this.event['photo_3'] = reader.result.toString()
            this.referredForm.addControl('image_3', this.formBuilder.control(''))
            this.referredForm.controls['image_3'].setValue(file)
          }
          else if(position == '4'){
            this.event['photo_4'] = reader.result.toString()
            this.referredForm.addControl('image_4', this.formBuilder.control(''))
            this.referredForm.controls['image_4'].setValue(file)
          }
        };
        reader.readAsDataURL(file);

    }, false);
      
  }

  activate_agent(){
    if(this.agent_pin == '')
      return this.toast.presentToast('Pin is empty')

    this.modalController.dismiss({'success': true, 'pin': this.agent_pin});
  }

  moveFocus(nextElement) {
    nextElement.setFocus();
  }
  logRatingChange(rating){
    console.log("changed rating: ", rating);
  }

}
