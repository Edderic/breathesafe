import axios from 'axios';

// Assumes there are at least two colors
export function interpolateColor(colors, ratio) {
    if (colors.length < 2) {
      throw "Oops. Number of colors expected by interpolateColor is at least 2";
    }

    const colorLenMin1 = colors.length - 1;

    for(let i=0; i< colorLenMin1; i++) {
      if (ratio > 0.99) {
        let lastColor = colors[colors.length-1] ;
        return `rgb(${lastColor.r}, ${lastColor.g}, ${lastColor.b})`;
      }

      if (ratio < (i+1)/colorLenMin1 && ratio >= (i) / colorLenMin1) {
        let distanceToPrevColor = ratio - i / colorLenMin1;
        let prevColor = colors[i];
        let currColor = colors[i+1];

        let red = prevColor.r + (currColor.r - prevColor.r) * distanceToPrevColor * colorLenMin1;
        let green = prevColor.g + (currColor.g - prevColor.g) * distanceToPrevColor * colorLenMin1;
        let blue = prevColor.b + (currColor.b - prevColor.b) * distanceToPrevColor * colorLenMin1;

        return `rgb(${parseInt(red)}, ${parseInt(green)}, ${parseInt(blue)})`;
      }
    }
  }


export function feetToMeters(measurement_type, num) {
  if (measurement_type == 'feet') {
    return num / 3.048
  } else {
    return num
  }
}

export function cubicFeetPerMinuteTocubicMetersPerHour(measurement_type, num) {
  if (measurement_type == 'cubic feet per minute') {
    return num * 60 / (3.048)**3
  } else {
    return num
  }
}

export function setupCSRF() {
    let token = document.getElementsByName('csrf-token')[0].getAttribute('content')
    axios.defaults.headers.common['X-CSRF-Token'] = token
    axios.defaults.headers.common['Accept'] = 'application/json'
}

export function generateUUID() {
    // https://stackoverflow.com/questions/105034/how-to-create-guid-uuid
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}

export function indexToHour(index) {
  return [
    '6 AM',
    '7 AM',
    '8 AM',
    '9 AM',
    '10 AM',
    '11 AM',
    '12 PM',
    '1 PM',
    '2 PM',
    '3 PM',
    '4 PM',
    '5 PM',
    '6 PM',
    '7 PM',
    '8 PM',
    '9 PM',
    '10 PM',
    '11 PM',
  ][index]
}

export const daysToIndexDict = {
  'Sundays': 0,
  'Mondays': 1,
  'Tuesdays': 2,
  'Wednesdays': 3,
  'Thursdays': 4,
  'Fridays': 5,
  'Saturdays': 6,
}
