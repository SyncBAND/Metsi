import { Component, OnInit, NgZone} from '@angular/core';

import { ModalController, NavParams } from '@ionic/angular';

declare var google;

@Component({
  selector: 'app-modal-location',
  templateUrl: './modal-location.page.html',
  styleUrls: ['./modal-location.page.scss'],
})

export class ModalLocationPage implements OnInit {
  
  autocompleteItems;
  autocomplete;

  latitude: number = 0;
  longitude: number = 0;
  geo: any
  show_auto = true

  service = new google.maps.places.AutocompleteService();

  constructor (private navParams: NavParams, public modalCtrl: ModalController, private zone: NgZone) {
    this.show_auto = this.navParams.get('show')
    let object = this.navParams.get('object')
    if(!this.show_auto){
      this.geoCode({'location': object.latlng}, object.lat, object.lng, '')
      return
    }
    this.autocompleteItems = [];
    this.autocomplete = {
      query: ''
    };
  }

  ngOnInit() {
  }

  dismiss() {
    this.modalCtrl.dismiss({'success': false});
  }

  chooseItem(item: any) {
    if(item)
      this.geoCode({ 'address': item }, '', '', item);//convert Address to lat and long]
    else
      this.dismiss()
  }

  updateSearch() {

    if (this.autocomplete.query == '') {
     this.autocompleteItems = [];
     return;
    }

    let me = this;
    this.service.getPlacePredictions({
    input: this.autocomplete.query,
    componentRestrictions: {
      country: 'za'
    }
   }, (predictions, status) => {
     me.autocompleteItems = [];

   me.zone.run(() => {
     if (predictions != null) {
        predictions.forEach((prediction) => {
          me.autocompleteItems.push(prediction.description);
        });
       }
     });
   });
  }

  //convert Address string to lat and long
  async geoCode(obj:any, lat, lng, address) {
    let geocoder = new google.maps.Geocoder();

    var street_name='';
    var province='';
    var city='';
    var country='';
    var suburb='';

    geocoder.geocode(obj, (results, status) => {
        
      let latitude = results[0].geometry.location.lat();
      let longitude = results[0].geometry.location.lng();
      let array = results[0].address_components
      if(address == '')
        address = results[0].formatted_address
        
      if(array)
        array.forEach( function(address_component, i) {
        
          if(address_component.types)
          for(let j = 0; j < address_component.types.length; j++){
            if (address_component.types[j] == "route"){
                street_name = address_component.long_name;
                break;
            }
        
            if (address_component.types[j] == "locality"){
                city = address_component.long_name;
                break;
            }
        
            if (address_component.types[j] == "administrative_area_level_1"){ 
                province = address_component.long_name;
                break;
            }
        
            if (address_component.types[j] == "country"){ 
                country = address_component.long_name;
                break;
            }
        
            if (address_component.types[j] == "sublocality"){ 
                suburb = address_component.long_name;
                break;
            }
        
        }
    });
    let data = {'success': true, 'latitude': latitude, 'city': city, 'country': country, 'province': province, 'suburb': suburb, 'street_name': street_name, 'longitude': longitude, 'location': address}
    return this.modalCtrl.dismiss(data);
    
   }, (err) => {
    let data = {'success': true, 'latitude': lat, 'city': city, 'country': country, 'province': province, 'suburb': suburb, 'street_name': street_name, 'longitude': lng, 'location': address}
    return this.modalCtrl.dismiss(data);
    
   });
  }

}
