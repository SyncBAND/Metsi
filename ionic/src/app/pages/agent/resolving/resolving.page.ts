import { Component, ViewChild, OnInit, ElementRef } from '@angular/core';
import { ModalController, NavController } from '@ionic/angular';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";

import { AuthService } from '../../../shared/service/auth/auth.service';
import { AutocompleteService } from '../../../shared/service/autocomplete/autocomplete.service';
import { ToastService } from '../../../shared/service/toast/toast.service';
import { UtilsService } from '../../../shared/service/utils/utils.service';

import { Geolocation, Plugins } from '@capacitor/core';
import { Observable } from 'rxjs';

import { CameraResultType, CameraSource } from '@capacitor/core';

import { Router } from '@angular/router';

import { ModalLocationPage } from '../../modals/modal-location/modal-location.page';

const { Browser } = Plugins;
const { Camera } = Plugins;

declare var google;

@Component({
  selector: 'app-resolving',
  templateUrl: './resolving.page.html',
  styleUrls: ['./resolving.page.scss'],
})
export class ResolvingPage implements OnInit {

  @ViewChild('filechooser') fileInput: ElementRef<HTMLInputElement>;

  resolvingForm: FormGroup;
  isSubmitted = false;

  items: any;
  acService: any;
  placesService: any;
  selectedItem: any;
  buttonDisabled = true;
  sessionToken: any;
  currentLon: any;
  currentLat: any;
  destinationCity : string;
  zipCode : string="";

  enquiry: any;

  data: Observable<string[]>;
  
  constructor(public authService: AuthService,
    public nav: NavController,
    public autocomplete: AutocompleteService,
    public toast: ToastService,
    public formBuilder: FormBuilder,
    private modalCtrl:ModalController,
    private router: Router,
    public utils: UtilsService) {
      
  }

  ionViewWillEnter(){
    this.enquiry = JSON.parse(localStorage.getItem('resolving'))
  }

  dismiss() {
    this.items = [];
    this.resolvingForm.controls.location.setValue('')
    this.selectedItem = undefined
  }

  validDestination() {
    if (this.selectedItem == undefined) {
      this.toast.presentToast("Enter a destination")
    }
    else {
      let latitude = this.selectedItem.latitude;
      let longitude = this.selectedItem.longitude;
      this.resolvingForm.controls['latitude'].setValue(latitude.toString());
      this.resolvingForm.controls['longitude'].setValue(longitude.toString());
    }
  }

  chooseItem(item: any) {
    
    this.selectedItem = item;
    this.items = [];
    this.resolvingForm.controls.location.setValue(item.structured_formatting.main_text + " - " + item.structured_formatting.secondary_text);
    this.buttonDisabled = false;
    if (item.structured_formatting.secondary_text.indexOf(",")>0){
      let lieuSplitted = item.structured_formatting.secondary_text.split(",",1); 
      this.destinationCity  = lieuSplitted[0]
    }
    else{
      this.destinationCity  = item.structured_formatting.main_text
    }
    this.validDestination()

  }

  severity = [
    "Excessive",
    "Worsening",
    "Moderate",
    "None",
  ]

  problems = [
    "Burst pipe",
    "Accident",
    "I am not sure"
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
 
  minDate = new Date().toISOString();
  
  ngOnInit() {
    
    this.resolvingForm = this.formBuilder.group({
      severity: ['', [Validators.required]],
      area: ['', [Validators.required]],
      position: ['', [Validators.required]],
      description: ['', [Validators.required, Validators.minLength(10)]],
      problem: ['', [Validators.required]],
      mode: localStorage.getItem('mode'),
      latitude: [''],
      longitude: [''],
      location: [''],
      suburb: [''],
      city: [''],
      province: [''],
      country: [''],
    })

    try{
      this.sessionToken = new google.maps.places.AutocompleteSessionToken();
      this.acService = new google.maps.places.AutocompleteService();
      this.items = [];
    }
    catch {
      this.toast.presentToast('Location error: Data network might be down')
    }
    
  }

  get errorControl() {
    return this.resolvingForm.controls;
  }

  refer(){
    this.utils.openModal(this.enquiry.id, 'Refer').then((data) => {
      if (data != undefined) {
        
          if(data.success){
            
              let formData = new FormData();

              formData.append('enquiry_id', this.enquiry.id)
              formData.append('user', '1')
              formData.append('status_details', data.details)
              formData.append('severity', data.severity)
              formData.append('previous_skill_needed', data.skill)
              formData.append('skill_needed', data.skill)
              formData.append('area', data.area)
              formData.append('position', data.position)
              formData.append('current_status', 'Referred')
              formData.append('agent', localStorage.getItem('agent'))
              formData.append('mode', 'AGENT')
              if(data.image_1)
                formData.append('image_1', data.image_1, data.image_1_name)
              if(data.image_2)
                formData.append('image_2', data.image_2, data.image_2_name)
              if(data.image_3)
                formData.append('image_3', data.image_3, data.image_3_name)
              if(data.image_4)
                formData.append('image_4', data.image_4, data.image_4_name)
        

              this.authService.request_logged_in(`enquiries-activity`, "post", formData).then(()=>{
                  this.toast.presentToast('Referred')
                  this.back()
              },(err)=>{
                  this.authService.handleError(err);
              });
              
          }
          else
              this.toast.presentToast('Dismissed')

      }
    });
  }

  updateSearch() {
    
    if (this.resolvingForm.controls.location.value == '') {
      this.items = [];
      this.buttonDisabled = true
      return;
    }

    let self = this;
    let config: any;

    if (this.currentLat) {
      let myLatLng = new google.maps.LatLng({lat: this.currentLat, lng: this.currentLon}); 
      config = {
        types: ['geocode'], 
        input: this.resolvingForm.controls.location.value,
        sessionToken: this.sessionToken,
        language: "EN",
        location: myLatLng,
        radius: 500 * 100 
      }
    }
    else {
      config = {
        types: ['geocode'], 
        input: this.resolvingForm.controls.location.value,
        sessionToken: this.sessionToken,
        language:"EN"
      }
    }
    
    this.acService.getPlacePredictions(config, function (predictions, status) {
      self.items = [];
      
      if (predictions) {
        predictions.forEach(function (prediction) {
          self.items.push(prediction);
        });
      }
    });
  }

  event = {
    photo_1: '../../../assets/camera.png',
    photo_2: '../../../assets/camera.png',
    photo_3: '../../../assets/camera.png',
    photo_4: '../../../assets/camera.png',
  }

  image: any;
  start: any;
  watch: any;

  async goToLocation(){
    return new Promise(async (resolve, reject) => {

      if(localStorage.getItem('location_permission') == null)
        this.utils.showAlert('Location Permission', 'The reason why we need your location is to help the agents locate you for your bookings')

      this.watch = await Geolocation.watchPosition({ timeout: 5000, maximumAge: 0 }, pos => {
        
        Geolocation.clearWatch({id: this.watch});
        if(pos){
          localStorage.setItem('location_permission', 'set')
          Browser.open({ url: "https://www.google.com/maps/dir/?api=1&origin=" + pos.coords.latitude.toString() + "," + pos.coords.longitude.toString() + "&destination=" + this.enquiry.latitude + "," + this.enquiry.longitude + "&travelmode=driving"});
        }
        else{
          this.toast.presentToast("Not found. Your location permission might be off.")
        }
        this.watch = null; 

      })
    })
    
  }

  async getLocation() {
    this.isSubmitted = false;
    this.resolvingForm.controls['location'].setValue('');
    this.resolvingForm.controls['latitude'].setValue('');
    this.resolvingForm.controls['longitude'].setValue('');

    return new Promise(async (resolve, reject) => {

      if(localStorage.getItem('location_permission') == null)
        this.utils.showAlert('Location Permission', 'The reason why we need your location is to help the agents locate you for your bookings')

      this.watch = await Geolocation.watchPosition({ timeout: 5000, maximumAge: 0 }, pos => {
        
        Geolocation.clearWatch({id: this.watch});
        if(pos){
          localStorage.setItem('location_permission', 'set')
          this.resolvingForm.controls['latitude'].setValue(pos.coords.latitude.toString());
          this.resolvingForm.controls['longitude'].setValue(pos.coords.longitude.toString());
          this.watch = null; 
          resolve(pos)
        }
        else{
          this.toast.presentToast("Not found. Your location permission might be off.")
          this.watch = null; 
          reject(pos)
        }
        this.watch = null; 

      })
    }).then((pos: any)=>{
      
      if(pos.coords){
          console.log(pos)
          this.resolved()
      }
      else  
        this.toast.presentToast("Try again")
      
    }, (err)=>{
      this.toast.presentToast(err.responseText)
    })
  }

  async showAddressModal(show, object) {
    const modal = await this.modalCtrl.create({
      component: ModalLocationPage,
      componentProps: {
        'show': show,
        'object': object
      }
    });

    await modal.present();
    const { data } = await modal.onWillDismiss();
    return data
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
                this.resolvingForm.addControl('image_1', this.formBuilder.control(''))
                this.resolvingForm.controls['image_1'].setValue(file)
              }
              else if(position == '2'){
                this.event['photo_2'] = reader.result.toString()
                this.resolvingForm.addControl('image_2', this.formBuilder.control(''))
                this.resolvingForm.controls['image_2'].setValue(file)
              }
              else if(position == '3'){
                this.event['photo_3'] = reader.result.toString()
                this.resolvingForm.addControl('image_3', this.formBuilder.control(''))
                this.resolvingForm.controls['image_3'].setValue(file)
              }
              else if(position == '4'){
                this.event['photo_4'] = reader.result.toString()
                this.resolvingForm.addControl('image_4', this.formBuilder.control(''))
                this.resolvingForm.controls['image_4'].setValue(file)
              }
            };
            reader.readAsDataURL(file);

        }, false);
      
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
          this.resolvingForm.addControl('image_1', this.formBuilder.control(''))
          this.resolvingForm.controls['image_1'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
        else if(position == '2'){
          this.event['photo_2'] = imageUrl

          this.resolvingForm.addControl('image_2', this.formBuilder.control(''))
          this.resolvingForm.controls['image_2'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
        else if(position == '3'){
          this.event['photo_3'] = imageUrl
          this.resolvingForm.addControl('image_3', this.formBuilder.control(''))
          this.resolvingForm.controls['image_3'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
        else if(position == '4'){
          this.event['photo_4'] = imageUrl
          this.resolvingForm.addControl('image_4', this.formBuilder.control(''))
          this.resolvingForm.controls['image_4'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
      }
      catch{
        this.selectImage(position);
      }
    }

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

    moveFocus(nextElement) {
        nextElement.setFocus();
    }

    async resolved() {
      this.isSubmitted = true;
          
      if (!this.resolvingForm.valid)
        return false
      
      setTimeout(() => {
        let form = new FormData()
        
        form.append('agent', localStorage.getItem('agent'))
        form.append('mode', 'AGENT')
        form.append('enquiry_id', this.enquiry.id)
        form.append('severity', this.resolvingForm.controls.severity.value)
        form.append('area', this.resolvingForm.controls.area.value)
        form.append('position', this.resolvingForm.controls.position.value)
        form.append('description', this.resolvingForm.controls.description.value)
        form.append('problem', this.resolvingForm.controls.problem.value)
        form.append('current_status', 'Resolved')
        form.append('status_details', this.resolvingForm.controls.description.value)
        form.append('user', '1')
        form.append('previous_skill_needed', '1')
        form.append('mode', this.resolvingForm.controls.mode.value)
        form.append('latitude', this.resolvingForm.controls.latitude.value)
        form.append('longitude', this.resolvingForm.controls.longitude.value)
        if(this.resolvingForm.controls.image_1)
          form.append('image_1', this.resolvingForm.controls.image_1.value, this.resolvingForm.controls.image_1.value.name)
        if(this.resolvingForm.controls.image_2)
          form.append('image_2', this.resolvingForm.controls.image_2.value, this.resolvingForm.controls.image_2.value.name)
        if(this.resolvingForm.controls.image_3)
          form.append('image_3', this.resolvingForm.controls.image_3.value, this.resolvingForm.controls.image_3.value.name)
        if(this.resolvingForm.controls.image_4)
          form.append('image_4', this.resolvingForm.controls.image_4.value, this.resolvingForm.controls.image_4.value.name)
        // should be POINT(lng, lat) but POINT(lat, lng) works
        let destination = "POINT("+this.resolvingForm.controls.latitude.value + " " + this.resolvingForm.controls.longitude.value + ")"
        form.append('destination', destination)

        if(this.resolvingForm.controls.latitude.value == '' && this.resolvingForm.controls.longitude.value == '' && this.resolvingForm.controls.location.value == '')
          return this.toast.presentToast('Please enter location')

        this.authService.request_logged_in('enquiries-activity', 'post', form).then((res)=>{

          this.reset()
          this.toast.presentToast("Issue Resolved")
          this.isSubmitted = false;

          return this.nav.navigateRoot('/resolved')
        },
        (err)=>{
          this.isSubmitted = false;
          return this.authService.handleError(err)
        })
      });
      
    }

    reset(){
      
      this.resolvingForm.controls.severity.reset()
      this.resolvingForm.controls.area.reset()
      this.resolvingForm.controls.position.reset()
      this.resolvingForm.controls.description.reset()
      this.resolvingForm.controls.problem.reset()
      this.resolvingForm.controls.latitude.reset()
      this.resolvingForm.controls.longitude.reset()
      this.resolvingForm.controls.location.reset()
      this.resolvingForm.controls.suburb.reset()
      this.resolvingForm.controls.city.reset()
      this.resolvingForm.controls.province.reset()
      this.resolvingForm.controls.country.reset()

      if(this.resolvingForm.controls.image_1)
        this.resolvingForm.removeControl('image_1')
      if(this.resolvingForm.controls.image_2)
        this.resolvingForm.removeControl('image_2')
      if(this.resolvingForm.controls.image_3)
        this.resolvingForm.removeControl('image_3')
      if(this.resolvingForm.controls.image_4)
        this.resolvingForm.removeControl('image_4')

    }

    back(){
      this.router.navigateByUrl( localStorage.getItem('current_first_level_url') != null ? `/`+localStorage.getItem('current_first_level_url') : '/tabs-enduser/enduser-profile' );
    }

}
