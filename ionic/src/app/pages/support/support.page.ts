import { Component, ViewChild, OnInit, ElementRef } from '@angular/core';
import { ModalController, NavController } from '@ionic/angular';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";

import { AuthService } from '../../shared/service/auth/auth.service';
import { AutocompleteService } from '../../shared/service/autocomplete/autocomplete.service';
import { ToastService } from '../../shared/service/toast/toast.service';
import { UtilsService } from '../../shared/service/utils/utils.service';

import { Geolocation} from '@capacitor/core';
import { Observable } from 'rxjs';

import { CameraResultType, CameraSource } from '@capacitor/core';

import { Router } from '@angular/router';

import { ModalLocationPage } from '../modals/modal-location/modal-location.page';

import {
  Plugins,
} from '@capacitor/core';

const { Camera } = Plugins;

declare var google;

@Component({
  selector: 'app-support',
  templateUrl: './support.page.html',
  styleUrls: ['./support.page.scss'],
})
export class SupportPage implements OnInit {
  
  @ViewChild('filechooser') fileInput: ElementRef<HTMLInputElement>;

  supportForm: FormGroup;
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
    public utils: UtilsService,
    public toast: ToastService,
    public formBuilder: FormBuilder,
    private router: Router,
    private modalCtrl:ModalController) {
      
  }

  ionViewWillEnter(){
    
  }

  dismiss() {
    console.log("Clear search")
    this.items = [];
    this.supportForm.controls.location.setValue('')
    this.selectedItem = undefined
  }

  validDestination() {
    if (this.selectedItem == undefined) {
      // should display a message to the user
      this.toast.presentToast("Enter a destination")
    }
    else {
      let latitude = this.selectedItem.latitude;
      let longitude = this.selectedItem.longitude;
      this.supportForm.controls['latitude'].setValue(latitude.toString());
      this.supportForm.controls['longitude'].setValue(longitude.toString());
    }
  }

  chooseItem(item: any) {
    
    this.selectedItem = item;
    this.items = [];
    this.supportForm.controls.location.setValue(item.structured_formatting.main_text + " - " + item.structured_formatting.secondary_text);
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
  
  
  ngOnInit() {
    
    this.supportForm = this.formBuilder.group({
      title: ['', [Validators.required, Validators.minLength(2)]],
      problem: ['', [Validators.required]],
      description: [''],
      user: [1],
      mode: localStorage.getItem('mode'),
      latitude: [''],
      longitude: [''],
      location: [''],
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
    return this.supportForm.controls;
  }

  updateSearch() {
    
    if (this.supportForm.controls.location.value == '') {
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
        input: this.supportForm.controls.location.value,
        sessionToken: this.sessionToken,
        language: "EN",
        location: myLatLng,
        radius: 500 * 100 
      }
    }
    else {
      config = {
        types: ['geocode'], 
        input: this.supportForm.controls.location.value,
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
  title = '';
  
  minDate = new Date().toISOString();

  problem_and_estimated_hours = {
    "Support": 4,
    "Repair": 1,
    "Complaint": 3,
    "Compliment": 2,
    "Report": 2,
    "Other": 3
  }
  list = Object.keys(this.problem_and_estimated_hours)

  async getLocation() {
    return new Promise(async (resolve, reject) => {
      this.watch = await Geolocation.watchPosition({ timeout: 5000, maximumAge: 0 }, pos => {
        
        Geolocation.clearWatch({id: this.watch});
        if(pos){
          this.supportForm.controls['latitude'].setValue(pos.coords.latitude.toString());
          this.supportForm.controls['longitude'].setValue(pos.coords.longitude.toString());
          this.getAddress(pos.coords.latitude, pos.coords.longitude)
          resolve(pos)
        }
        else{
          reject(pos)
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
    //   this.supportForm.controls['location'].setValue(JSON.stringify(result[0]))
    //   console.log(JSON.stringify(result[0]))
    // })
    // .catch((error: any) => console.log(error));

    let latlng = {
      lat: latitude,
      lng: longitude
    } 

    this.showAddressModal(false, { latlng: latlng, lat:latitude, lng:longitude}).then((data)=>{
      if(data.success){
        this.supportForm.controls['location'].setValue(data.location);
        this.supportForm.controls['latitude'].setValue(data.latitude);
        this.supportForm.controls['longitude'].setValue(data.longitude);
        this.supportForm.controls['city'].setValue(data.city);
        this.supportForm.controls['province'].setValue(data.province);
        this.supportForm.controls['country'].setValue(data.country);
        this.supportForm.controls['suburb'].setValue(data.suburb);
      }
    })
  }

  getAddressModal () {
    this.supportForm.controls['location'].setValue('');
    this.supportForm.controls['latitude'].setValue('');
    this.supportForm.controls['longitude'].setValue('');
      this.showAddressModal(true, {}).then((data)=>{
        if(data.success){
          this.supportForm.controls['location'].setValue(data.location);
          this.supportForm.controls['latitude'].setValue(data.latitude);
          this.supportForm.controls['longitude'].setValue(data.longitude);
          this.supportForm.controls['city'].setValue(data.city);
          this.supportForm.controls['province'].setValue(data.province);
          this.supportForm.controls['country'].setValue(data.country);
          this.supportForm.controls['suburb'].setValue(data.suburb);
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
                this.supportForm.addControl('image_1', this.formBuilder.control(''))
                this.supportForm.controls['image_1'].setValue(file)
              }
              else if(position == '2'){
                this.event['photo_2'] = reader.result.toString()
                this.supportForm.addControl('image_2', this.formBuilder.control(''))
                this.supportForm.controls['image_2'].setValue(file)
              }
              else if(position == '3'){
                this.event['photo_3'] = reader.result.toString()
                this.supportForm.addControl('image_3', this.formBuilder.control(''))
                this.supportForm.controls['image_3'].setValue(file)
              }
              else if(position == '4'){
                this.event['photo_4'] = reader.result.toString()
                this.supportForm.addControl('image_4', this.formBuilder.control(''))
                this.supportForm.controls['image_4'].setValue(file)
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
          this.supportForm.addControl('image_1', this.formBuilder.control(''))
          this.supportForm.controls['image_1'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
        else if(position == '2'){
          this.event['photo_2'] = imageUrl

          this.supportForm.addControl('image_2', this.formBuilder.control(''))
          this.supportForm.controls['image_2'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
        else if(position == '3'){
          this.event['photo_3'] = imageUrl
          this.supportForm.addControl('image_3', this.formBuilder.control(''))
          this.supportForm.controls['image_3'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
        else if(position == '4'){
          this.event['photo_4'] = imageUrl
          this.supportForm.addControl('image_4', this.formBuilder.control(''))
          this.supportForm.controls['image_4'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
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

    async sendSupport() {
      this.isSubmitted = true;
      if (!this.supportForm.valid)
        return false;
      
      setTimeout(() => {
        let form = new FormData()
        
        form.append('title', this.supportForm.controls.title.value)
        form.append('problem', this.supportForm.controls.problem.value)
        form.append('description', this.supportForm.controls.description.value)
        form.append('user', '1')
        form.append('mode', this.supportForm.controls.mode.value)
        form.append('latitude', this.supportForm.controls.latitude.value)
        form.append('longitude', this.supportForm.controls.longitude.value)
        if(this.supportForm.controls.image_1)
          form.append('image_1', this.supportForm.controls.image_1.value, this.supportForm.controls.image_1.value.name)
        if(this.supportForm.controls.image_2)
          form.append('image_2', this.supportForm.controls.image_2.value, this.supportForm.controls.image_2.value.name)
        if(this.supportForm.controls.image_3)
          form.append('image_3', this.supportForm.controls.image_3.value, this.supportForm.controls.image_3.value.name)
        if(this.supportForm.controls.image_4)
          form.append('image_4', this.supportForm.controls.image_4.value, this.supportForm.controls.image_4.value.name)
        form.append('location', this.supportForm.controls.location.value)
        form.append('city', this.supportForm.controls.city.value)
        form.append('province', this.supportForm.controls.province.value)
        form.append('country', this.supportForm.controls.country.value)
        

        this.authService.request_logged_in('support', 'post', form).then((res)=>{
          this.reset()
          this.toast.presentToast("Support notified")
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
      this.supportForm.controls.title.reset()
      this.supportForm.controls.problem.reset()
      this.supportForm.controls.description.reset()
      this.supportForm.controls.latitude.reset()
      this.supportForm.controls.longitude.reset()
      this.supportForm.controls.location.reset()
      this.supportForm.controls.province.reset()
      this.supportForm.controls.country.reset()

      if(this.supportForm.controls.image_1)
        this.supportForm.removeControl('image_1')
      if(this.supportForm.controls.image_2)
        this.supportForm.removeControl('image_2')
      if(this.supportForm.controls.image_3)
        this.supportForm.removeControl('image_3')
      if(this.supportForm.controls.image_4)
        this.supportForm.removeControl('image_4')

    }
    
    getDataName(event) {
      this.data = this.autocomplete.getData(event.target.value, this.authService.endpoint+"/Support/");
    }

    back(){
      this.router.navigateByUrl( localStorage.getItem('current_url') != null ? `/`+localStorage.getItem('current_url') : '/tabs-enduser/enduser-profile' );
    }

}
