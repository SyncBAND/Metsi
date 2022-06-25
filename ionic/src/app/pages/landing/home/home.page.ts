import { Component, OnInit, ViewChild } from '@angular/core';
import { IonSlides } from '@ionic/angular';
import { NavController } from '@ionic/angular';

import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.page.html',
  styleUrls: ['./home.page.scss'],
})
export class HomePage implements OnInit {

  @ViewChild('slideWithNav', { static: false }) slideWithNav: IonSlides;

  modeSlider: any;
  //Configuration for each Slider
  slideOpts = {
    initialSlide: 0,
    slidesPerView: 1,
    autoplay: {
      delay: 3000,
      disableOnInteraction:false
    },
    speed: 500
  };
  
  constructor(public nav: NavController, private router: Router) { 
    //Item object for Nature
    this.modeSlider =
    {
      isBeginningSlide: true,
      isEndSlide: false,
      slidesItems: [
        {
          id: 995
        }
      ]
    };
  }

  ngOnInit() {
    
  }

  ionViewDidEnter() {

    this.slideWithNav.slideTo(0)
    localStorage.setItem('current_url', this.router.url)
  }

  //Move to Next slide
  slideNext(object, slideView) {
    slideView.slideNext(500).then(() => {
      this.checkIfNavDisabled(object, slideView);
    });
  }

  //Move to previous slide
  slidePrev(object, slideView) {
    slideView.slidePrev(500).then(() => {
      this.checkIfNavDisabled(object, slideView);
    });;
  }

  //Method called when slide is changed by drag or navigation
  SlideDidChange(object, slideView) {
    this.checkIfNavDisabled(object, slideView);
  }

  //Call methods to check if slide is first or last to enable disbale navigation  
  checkIfNavDisabled(object, slideView) {
    this.checkisBeginning(object, slideView);
    this.checkisEnd(object, slideView);
  }

  checkisBeginning(object, slideView) {
    slideView.isBeginning().then((istrue) => {
      object.isBeginningSlide = istrue;
    });
  }
  checkisEnd(object, slideView) {
    slideView.isEnd().then((istrue) => {
      object.isEndSlide = istrue;
    });
  }

  set_mode(){
    localStorage.setItem('mode', 'enduser')
    return this.nav.navigateRoot('/tabs-enduser');
  }

}
