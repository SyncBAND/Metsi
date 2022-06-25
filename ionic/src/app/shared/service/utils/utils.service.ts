import { ModalController, Platform } from '@ionic/angular';

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { ModalPopupPage } from '../../../pages/modals/modal-popup/modal-popup.page';

import { Plugins } from '@capacitor/core';
const { Modals } = Plugins;

@Injectable({
  providedIn: 'root'
})
export class UtilsService {

   /**
    * @name platformIs
    * @type String
    * @public
    * @description               Property that stores the environment reference and is 
    *                            used as a flag for determining which features to 
    *                            'switch on' inside the component template
    */
   public platformIs 				: string 		=	'';


   constructor(
      public http : HttpClient,
      private _PLAT : Platform,
      public modalController: ModalController, 
   ) {  

    // Are we on mobile?
    if(this._PLAT.is('ios') || this._PLAT.is('android'))
    {
       this.platformIs = 'mobile';
    }

    // Or web?
    else
    {
       this.platformIs = 'browser';
    }
   }


   format_date = function( value ) {

      if (value){
          var options = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric' };
          var date_time  = new Date(value);
          value = date_time.toLocaleDateString("en-US", options);
      }
      else
          value = '-';
  
      return `${value}`
  
   };

   async openModal(id, type, info={}) {
     // type can be "Cancel" or "Rate"
     let init = {
         "id": id,
         "rating": 0,
         "title": type
      }
      let componentProps = Object.assign({}, init, info)
      const modal = await this.modalController.create({
            component: ModalPopupPage,
            componentProps: componentProps
      });
 
      await modal.present();
      const { data } = await modal.onWillDismiss();
      return data
   }

   async showAlert(title, message) {
      return await Modals.alert({
        title: title,
        message: message
      });
    }

}
