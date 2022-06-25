import { Component, ViewChild, OnInit, ElementRef } from '@angular/core';
import { ModalController, NavController } from '@ionic/angular';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";

import { AuthService } from '../../shared/service/auth/auth.service';
import { AutocompleteService } from '../../shared/service/autocomplete/autocomplete.service';
import { ToastService } from '../../shared/service/toast/toast.service';
import { UtilsService } from '../../shared/service/utils/utils.service';

import { Geolocation, Plugins } from '@capacitor/core';
import { Observable } from 'rxjs';

import { CameraResultType, CameraSource } from '@capacitor/core';

import { Router } from '@angular/router';

import { ModalLocationPage } from '../modals/modal-location/modal-location.page';

const { Camera } = Plugins;

declare var google;

@Component({
  selector: 'app-enquire',
  templateUrl: './enquire.page.html',
  styleUrls: ['./enquire.page.scss'],
})
export class EnquirePage implements OnInit {
  
  @ViewChild('filechooser') fileInput: ElementRef<HTMLInputElement>;

  enquiryForm: FormGroup;
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
    
  }

  dismiss() {
    this.items = [];
    this.enquiryForm.controls.location.setValue('')
    this.selectedItem = undefined
  }

  validDestination() {
    if (this.selectedItem == undefined) {
      this.toast.presentToast("Enter a destination")
    }
    else {
      let latitude = this.selectedItem.latitude;
      let longitude = this.selectedItem.longitude;
      this.enquiryForm.controls['latitude'].setValue(latitude.toString());
      this.enquiryForm.controls['longitude'].setValue(longitude.toString());
    }
  }

  chooseItem(item: any) {
    
    this.selectedItem = item;
    this.items = [];
    this.enquiryForm.controls.location.setValue(item.structured_formatting.main_text + " - " + item.structured_formatting.secondary_text);
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

  skills = [
    "Inspection",
    "Maintenance",
    "Repair",
    "Contractor",
    "Artesan"
  ]

  minDate = new Date().toISOString();
  
  ngOnInit() {
    
    this.enquiryForm = this.formBuilder.group({
      severity: ['', [Validators.required]],
      description: [''],
      problem: ['', [Validators.required]],
      area: ['', [Validators.required]],
      position: ['', [Validators.required]],
      skill_needed: ['', [Validators.required]],
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
    return this.enquiryForm.controls;
  }

  updateSearch() {
    
    if (this.enquiryForm.controls.location.value == '') {
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
        input: this.enquiryForm.controls.location.value,
        sessionToken: this.sessionToken,
        language: "EN",
        location: myLatLng,
        radius: 500 * 100 
      }
    }
    else {
      config = {
        types: ['geocode'], 
        input: this.enquiryForm.controls.location.value,
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

  async getLocation() {
    this.enquiryForm.controls['location'].setValue('');
    this.enquiryForm.controls['latitude'].setValue('');
    this.enquiryForm.controls['longitude'].setValue('');
    return new Promise(async (resolve, reject) => {

    if(localStorage.getItem('location_permission') == null)
      this.utils.showAlert('Location Permission', 'The reason why we need your location is to help the agents locate you for your bookings')
  
      this.watch = await Geolocation.watchPosition({ timeout: 5000, maximumAge: 0 }, pos => {
        
        if(localStorage.getItem('location_permission') == null)
          this.utils.showAlert('Location Permission', 'The reason why we need your location is to help the agents locate you for your bookings')

        Geolocation.clearWatch({id: this.watch});
        if(pos){
          localStorage.setItem('location_permission', 'set')
          this.enquiryForm.controls['latitude'].setValue(pos.coords.latitude.toString());
          this.enquiryForm.controls['longitude'].setValue(pos.coords.longitude.toString());
          this.getAddress(pos.coords.latitude, pos.coords.longitude)
          resolve(pos)
        }
        else{
          this.toast.presentToast("Not found. Your location permission might be off.")
        }
        this.watch = null; 

      })
    })
  }

  async getAddress(latitude, longitude) {
    // let options: NativeGeocoderOptions = {
    //   useLocale: true,
    //   maxResults: 5
    // };
    // this.nativeGeocoder.reverseGeocode(latitude, longitude, options)
    // .then((result: NativeGeocoderResult[]) => {
    //   this.enquiryForm.controls['location'].setValue(JSON.stringify(result[0]))
    //   this.toast.presentToast(JSON.stringify(result[0]))
    // })
    // .catch((error: any) => {});
    let latlng = {
      lat: latitude,
      lng: longitude
    } 

    this.showAddressModal(false, { latlng: latlng, lat:latitude, lng:longitude}).then((data)=>{
      if(data.success){
        this.enquiryForm.controls['location'].setValue(data.location);
        this.enquiryForm.controls['latitude'].setValue(data.latitude);
        this.enquiryForm.controls['longitude'].setValue(data.longitude);
        this.enquiryForm.controls['city'].setValue(data.city);
        this.enquiryForm.controls['province'].setValue(data.province);
        this.enquiryForm.controls['country'].setValue(data.country);
        this.enquiryForm.controls['suburb'].setValue(data.suburb);
      }
    })

  }

  getAddressModal () {
    this.enquiryForm.controls['location'].setValue('');
    this.enquiryForm.controls['latitude'].setValue('');
    this.enquiryForm.controls['longitude'].setValue('');
      this.showAddressModal(true, {}).then((data)=>{
        if(data.success){
          this.enquiryForm.controls['location'].setValue(data.location);
          this.enquiryForm.controls['latitude'].setValue(data.latitude);
          this.enquiryForm.controls['longitude'].setValue(data.longitude);
          this.enquiryForm.controls['city'].setValue(data.city);
          this.enquiryForm.controls['province'].setValue(data.province);
          this.enquiryForm.controls['country'].setValue(data.country);
          this.enquiryForm.controls['suburb'].setValue(data.suburb);
        }
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
                this.enquiryForm.addControl('image_1', this.formBuilder.control(''))
                this.enquiryForm.controls['image_1'].setValue(file)
              }
              else if(position == '2'){
                this.event['photo_2'] = reader.result.toString()
                this.enquiryForm.addControl('image_2', this.formBuilder.control(''))
                this.enquiryForm.controls['image_2'].setValue(file)
              }
              else if(position == '3'){
                this.event['photo_3'] = reader.result.toString()
                this.enquiryForm.addControl('image_3', this.formBuilder.control(''))
                this.enquiryForm.controls['image_3'].setValue(file)
              }
              else if(position == '4'){
                this.event['photo_4'] = reader.result.toString()
                this.enquiryForm.addControl('image_4', this.formBuilder.control(''))
                this.enquiryForm.controls['image_4'].setValue(file)
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
          this.enquiryForm.addControl('image_1', this.formBuilder.control(''))
          this.enquiryForm.controls['image_1'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
        else if(position == '2'){
          this.event['photo_2'] = imageUrl

          this.enquiryForm.addControl('image_2', this.formBuilder.control(''))
          this.enquiryForm.controls['image_2'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
        else if(position == '3'){
          this.event['photo_3'] = imageUrl
          this.enquiryForm.addControl('image_3', this.formBuilder.control(''))
          this.enquiryForm.controls['image_3'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
        else if(position == '4'){
          this.event['photo_4'] = imageUrl
          this.enquiryForm.addControl('image_4', this.formBuilder.control(''))
          this.enquiryForm.controls['image_4'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
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

    async sendEnquiry() {
      this.isSubmitted = true;
      if (!this.enquiryForm.valid)
        return false
      
      setTimeout(() => {
        let form = new FormData()
        
        form.append('severity', this.enquiryForm.controls.severity.value)
        form.append('description', this.enquiryForm.controls.description.value)
        form.append('problem', this.enquiryForm.controls.problem.value)
        form.append('area', this.enquiryForm.controls.area.value)
        form.append('position', this.enquiryForm.controls.position.value)
        form.append('skills_needed', this.enquiryForm.controls.skill_needed.value)
        form.append('user', '1')
        form.append('mode', this.enquiryForm.controls.mode.value)
        form.append('latitude', this.enquiryForm.controls.latitude.value)
        form.append('longitude', this.enquiryForm.controls.longitude.value)
        if(this.enquiryForm.controls.image_1)
          form.append('image_1', this.enquiryForm.controls.image_1.value, this.enquiryForm.controls.image_1.value.name)
        if(this.enquiryForm.controls.image_2)
          form.append('image_2', this.enquiryForm.controls.image_2.value, this.enquiryForm.controls.image_2.value.name)
        if(this.enquiryForm.controls.image_3)
          form.append('image_3', this.enquiryForm.controls.image_3.value, this.enquiryForm.controls.image_3.value.name)
        if(this.enquiryForm.controls.image_4)
          form.append('image_4', this.enquiryForm.controls.image_4.value, this.enquiryForm.controls.image_4.value.name)
        form.append('location', this.enquiryForm.controls.location.value)
        form.append('suburb', this.enquiryForm.controls.suburb.value)
        form.append('city', this.enquiryForm.controls.city.value)
        form.append('province', this.enquiryForm.controls.province.value)
        form.append('country', this.enquiryForm.controls.country.value)
        // should be POINT(lng, lat) but coordinates:[lat, lng] works
        let destination = JSON.stringify({"coordinates":[this.enquiryForm.controls.latitude.value, this.enquiryForm.controls.longitude.value], "type":"Point"})
        form.append('destination', destination)
        
        if(this.enquiryForm.controls.latitude.value == '' && this.enquiryForm.controls.longitude.value == '' && this.enquiryForm.controls.location.value == '')
          return this.toast.presentToast('Please enter location')

        this.authService.request_logged_in('enquiries', 'post', form).then((res)=>{
          this.reset()
          this.toast.presentToast("We will be in touch shortly")
          this.isSubmitted = false;
          return this.nav.navigateRoot( localStorage.getItem('current_url') != null ? `/`+ localStorage.getItem('current_url') : '/tabs-enduser/enduser-profile' );
        },
        (err)=>{
          this.isSubmitted = false;
          return this.authService.handleError(err)
        })
      });
      
    }

    reset(){
      
      this.enquiryForm.controls.severity.reset()
      this.enquiryForm.controls.description.reset()
      this.enquiryForm.controls.problem.reset()
      this.enquiryForm.controls.area.reset()
      this.enquiryForm.controls.position.reset()
      this.enquiryForm.controls.skill_needed.reset()
      this.enquiryForm.controls.latitude.reset()
      this.enquiryForm.controls.longitude.reset()
      this.enquiryForm.controls.location.reset()
      this.enquiryForm.controls.suburb.reset()
      this.enquiryForm.controls.city.reset()
      this.enquiryForm.controls.province.reset()
      this.enquiryForm.controls.country.reset()

      if(this.enquiryForm.controls.image_1)
        this.enquiryForm.removeControl('image_1')
      if(this.enquiryForm.controls.image_2)
        this.enquiryForm.removeControl('image_2')
      if(this.enquiryForm.controls.image_3)
        this.enquiryForm.removeControl('image_3')
      if(this.enquiryForm.controls.image_4)
        this.enquiryForm.removeControl('image_4')

    }
    
    getVehicleName(event) {
      this.data = this.autocomplete.getData(event.target.value, this.authService.endpoint+"/vehicle/");
    }

    back(){
      this.router.navigateByUrl( localStorage.getItem('current_url') != null ? `/`+localStorage.getItem('current_url') : '/tabs-enduser/enduser-profile' );
    }

}
