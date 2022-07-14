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

export function computeVentilationACH(
  activityGroups,
  ambientPPM,
  steadyStatePPM,
  volumeCubicMeters
) {
  /*
   * (steadyStatePPM - ambientPPM) / 1_000_000
   *   = totalCO2 Emitted (m3 / h) / [V (m3) ACH (1 / h) ]
   *
   *        1_000_000 * totalCO2 Emitted (L / s) * 3600 s / h * 1 m3 / 1000 L
   *  ACH = -------------------------------------
   *          (steadyStatePPM - ambientPPM) * V
   *
   *        1_000_000 * totalCO2 Emitted (L / h) * 3.6 * 1 m3 / L
   *  ACH = -------------------------------------
   *          (steadyStatePPM - ambientPPM) * V
   *
   *        1_000_000 * totalCO2 Emitted (m3 / h) * 3.6
   *  ACH = -------------------------------------
   *          (steadyStatePPM - ambientPPM) * V
   *
   *        3.6 * 10^6 * totalCO2 Emitted (m3 / h)
   *  ACH = -------------------------------------
   *          (steadyStatePPM - ambientPPM) * V
   *
   *
   */

  let total = 0

  for (let activityGroup of activityGroups) {
    let met = getMetFromCO2GenerationActivity(activityGroup['carbonDioxideGenerationActivity'])
    let co2GenerationRate = getCO2GenerationRate(met, activityGroup['sex'] == 'Male', activityGroup['ageGroup'])
    total += co2GenerationRate * parseInt(activityGroup['numberOfPeople'])
  }

  const numerator = total * 3.6 * 1000000
  // 36 * 10^5
  // divided by 60
  // 6 x 10^4
  const denominator = (parseInt(steadyStatePPM) - parseInt(ambientPPM)) * volumeCubicMeters

  const ach = numerator / denominator

  return ach
}

export function computePortableACH(
  portableAirCleaners,
  roomUsableVolumeCubicMeters
) {
  let total = 0.0
  for (let portableAirCleaner of portableAirCleaners) {
    total += parseFloat(portableAirCleaner['airDeliveryRateCubicMetersPerHour']) / parseFloat(roomUsableVolumeCubicMeters)
  }

  return total
}

function getMetFromCO2GenerationActivity(activity) {
  const mapping = {
      "Calisthenics—light effort": 2.8,
      "Calisthenics—moderate effort": 3.8,
      "Calisthenics—vigorous effort": 8.0,
      "Child care": 2.5, // 2 - 3
      "Cleaning, sweeping—moderate effort": 3.8,
      "Custodial work—light": 2.3,
      "Dancing—aerobic, general": 7.3,
      "Dancing—general": 7.8,
      "Health club exercise classes—general": 5.0,
      "Kitchen activity—moderate effort": 3.3,
      "Lying or sitting quietly": 1.0,
      "Sitting reading, writing, typing": 1.3,
      "Sitting at sporting event as spectator": 1.5,
      "Sitting tasks, light effort (e.g, office work)": 1.5,
      "Sitting quietly in religious service": 1.3,
      "Sleeping": 0.95,
      "Standing quietly": 1.3,
      "Standing tasks, light effort (e.g, store clerk, filing)": 3.0,
      "Walking, less than 2 mph, level surface, very slow": 2.0,
      "Walking, 2.8 mph to 3.2 mph, level surface, moderate pace": 3.5,
  }

  return mapping[activity]
}

function getCO2GenerationRate(met, man, age) {
  /*  Meant for extrapolating CO2 generation rate given met, sex, and age
   *
   *  Params:
   *    met: a number
   *      Higher met, higher CO2 breathed out
   *    man: boolean
   *      True if man, False, otherwise.
   *    age: string
   *      Age groups
   *  Returns:
   *    CO2 generation rate (L/s)
   */
  const dict = [
    {
      '1 to <3': {'coef': 0.00279, 'intercept': -0.000017},
      '3 to <6': {'coef': 0.002774, 'intercept': -0.000016},
      '6 to <11': {'coef': 0.002749, 'intercept': -0.000015},
      '11 to <16': {'coef': 0.002713, 'intercept': -0.000015},
      '16 to <21': {'coef': 0.002698, 'intercept': -0.000014},
      '21 to <30': {'coef': 0.002688, 'intercept': -0.000013},
      '30 to <40': {'coef': 0.002696, 'intercept': -0.000014},
      '40 to <50': {'coef': 0.002693, 'intercept': -0.000012},
      '50 to <60': {'coef': 0.002694, 'intercept': -0.000014},
      '60 to <70': {'coef': 0.002716, 'intercept': -0.000014},
      '70 to <80': {'coef': 0.002722, 'intercept': -0.000015},
      '<1': {'coef': 0.002813, 'intercept': -0.000015},
      '>=80': {'coef': 0.002729, 'intercept': -0.000015}
    },
    {
      '1 to <3': {'coef': 0.001459, 'intercept': 0.000055},
      '11 to <16': {'coef': 0.003397, 'intercept': 0.00001},
      '16 to <21': {'coef': 0.00376, 'intercept': -0.000012},
      '21 to <30': {'coef': 0.004014, 'intercept': -0.000043},
      '3 to <6': {'coef': 0.001878, 'intercept': 0.000019},
      '30 to <40': {'coef': 0.00381, 'intercept': -0.000029},
      '40 to <50': {'coef': 0.003891, 'intercept': -0.000064},
      '50 to <60': {'coef': 0.003863, 'intercept': -0.000022},
      '6 to <11': {'coef': 0.0025, 'intercept': 0.0},
      '60 to <70': {'coef': 0.003323, 'intercept': -0.000028},
      '70 to <80': {'coef': 0.003177, 'intercept': -0.000003},
      '<1': {'coef': 0.000897, 'intercept': 0.00001},
      '>=80': {'coef': 0.003, 'intercept': 0.0}
    }
  ]

  const model = dict[man * 1][age]

  return model['coef'] * met + model['intercept']
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
