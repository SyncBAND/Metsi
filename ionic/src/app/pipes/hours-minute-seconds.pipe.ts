import { Injectable, Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'hoursMinuteSeconds'
})
@Injectable()
export class HoursMinuteSecondsPipe implements PipeTransform {

  transform(value, ...args: unknown[]): unknown {
    
    let minutes = Math.floor(value / 60);
    let hours = Math.floor(minutes / 60);
    let days = Math.floor(hours / 24);
    let seconds = Math.floor(value % 60);
	
    if(hours > 0)
      minutes = minutes - (60 * hours);
    if(days > 0)
      hours = hours - (24 * days);
    
    return days + " days, " + hours + " hrs, " + minutes + " mins, " + seconds + " secs";
  }

}
