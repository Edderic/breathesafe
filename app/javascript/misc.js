// esversion: 6
import axios from 'axios';

const INCHES_PER_FOOT = 12;
const CUBIC_FEET_PER_CUBIC_METER = 35.3147
const CUBIC_METER_PER_CUBIC_FEET = 1 / CUBIC_FEET_PER_CUBIC_METER
const FEET_PER_METER = 3.28084
const DAYS = [
  'Sundays', 'Mondays', 'Tuesdays', 'Wednesdays', 'Thursdays',
  'Fridays', 'Saturdays'
]

const infectorActivityTypeMapping = {
  "Resting – Oral breathing": 1,
  "Resting – Speaking": 4.7,
  "Resting – Loudly speaking": 30.3,
  "Standing – Oral breathing": 1.2,
  "Standing – Speaking": 5.7,
  "Standing – Loudly speaking": 32.6,
  "Light exercise – Oral breathing": 2.8,
  "Light exercise – Speaking": 13.2,
  "Light exercise – Loudly speaking": 85,
  "Heavy exercise – Oral breathing": 6.8,
  "Heavy exercise – Speaking": 31.6,
  "Heavy exercise – Loudly speaking": 204,
}

const maskToFactor = {
  'None': 1.0,
  'Cloth / Surgical': 0.5,
  'N95 - unfitted': 0.1,
  'Elastomeric N95': 0.05,
  'Elastomeric N99': 0.01,
  'Elastomeric P100': 0.001
}

export const maskToPenetrationFactor = maskToFactor


export const co2ActivityToSusceptibleBreathingActivity = {
  "Calisthenics—light effort": "Light Intensity",
  "Calisthenics—moderate effort": "Moderate Intensity",
  "Calisthenics—vigorous effort": "High Intensity",
  "Child care": "Sedentary / Passive", // 2 - 3
  "Cleaning, sweeping—moderate effort": "Light Intensity",
  "Custodial work—light": "Light Intensity",
  "Dancing—aerobic, general": "High Intensity",
  "Dancing—general": "High Intensity",
  "Health club exercise classes—general": "Moderate Intensity",
  "Kitchen activity—moderate effort": "Light Intensity",
  "Lying or sitting quietly": "Sedentary / Passive",
  "Sitting reading, writing, typing": "Sedentary / Passive",
  "Sitting at sporting event as spectator": "Sedentary / Passive",
  "Sitting tasks, light effort (e.g, office work)": "Sedentary / Passive",
  "Sitting quietly in religious service": "Sedentary / Passive",
  "Sleeping": "Sleep or Nap",
  "Standing quietly": "Sedentary / Passive",
  "Standing tasks, light effort (e.g, store clerk, filing)": "Sedentary / Passive",
  "Walking, less than 2 mph, level surface, very slow": "Light Intensity",
  "Walking, 2.8 mph to 3.2 mph, level surface, moderate pace": "Light Intensity",
}

// Uses age groups taken from the Harvard Healthy Buildings website instead of
// the original, which had more
export const susceptibleBreathingActivityToFactor = {
  "Sleep or Nap": {
    "1 to <3": {
      "mean cubic meters per hour": 0.276,
    },
    "3 to <6": {
      "mean cubic meters per hour": 0.258,
    },
    "6 to <11": {
      "mean cubic meters per hour": 0.27,
    },
    "11 to <16": {
      "mean cubic meters per hour": 0.3,
    },
    "16 to <21": {
      "mean cubic meters per hour": 0.294,
    },
    "21 to <30": {
      "mean cubic meters per hour": 0.258,
    },
    "30 to <40": {
      "mean cubic meters per hour": 0.276,
    },
    "40 to <50": {
      "mean cubic meters per hour": 0.3,
    },
    "50 to <60": {
      "mean cubic meters per hour": 0.312,
    },
    "60 to <70": {
      "mean cubic meters per hour": 0.318,
    },
    "70 to <80": {
      "mean cubic meters per hour": 0.318,
    },
    ">= 80": {
      "mean cubic meters per hour": 0.312,
    },
  },
  "Sedentary / Passive": {
    "1 to <3": {
      "mean cubic meters per hour": 0.27,
    },
    "3 to <6": {
      "mean cubic meters per hour": 0.282,
    },
    "6 to <11": {
      "mean cubic meters per hour": 0.324,
    },
    "11 to <16": {
      "mean cubic meters per hour": 0.318,
    },
    "16 to <21": {
      "mean cubic meters per hour": 0.318,
    },
    "21 to <30": {
      "mean cubic meters per hour": 0.252,
    },
    "30 to <40": {
      "mean cubic meters per hour": 0.258,
    },
    "40 to <50": {
      "mean cubic meters per hour": 0.288,
    },
    "50 to <60": {
      "mean cubic meters per hour": 0.3,
    },
    "60 to <70": {
      "mean cubic meters per hour": 0.294,
    },
    "70 to <80": {
      "mean cubic meters per hour": 0.3,
    },
    ">= 80": {
      "mean cubic meters per hour": 0.294,
    },
  },
  "Light Intensity": {
    "1 to <3": {
      "mean cubic meters per hour": 0.72,
    },
    "3 to <6": {
      "mean cubic meters per hour": 0.66,
    },
    "6 to <11": {
      "mean cubic meters per hour": 0.66,
    },
    "11 to <16": {
      "mean cubic meters per hour": 0.78,
    },
    "16 to <21": {
      "mean cubic meters per hour": 0.72,
    },
    "21 to <30": {
      "mean cubic meters per hour": 0.72,
    },
    "30 to <40": {
      "mean cubic meters per hour": 0.72,
    },
    "40 to <50": {
      "mean cubic meters per hour": 0.78,
    },
    "50 to <60": {
      "mean cubic meters per hour": 0.78,
    },
    "60 to <70": {
      "mean cubic meters per hour": 0.72,
    },
    "70 to <80": {
      "mean cubic meters per hour": 0.72,
    },
    ">= 80": {
      "mean cubic meters per hour": 0.72,
    },
  },
  "Moderate Intensity": {
    "1 to <3": {
      "mean cubic meters per hour": 1.26,
    },
    "3 to <6": {
      "mean cubic meters per hour": 1.26,
    },
    "6 to <11": {
      "mean cubic meters per hour": 1.32,
    },
    "11 to <16": {
      "mean cubic meters per hour": 1.5,
    },
    "16 to <21": {
      "mean cubic meters per hour": 1.56,
    },
    "21 to <30": {
      "mean cubic meters per hour": 1.56,
    },
    "30 to <40": {
      "mean cubic meters per hour": 1.62,
    },
    "40 to <50": {
      "mean cubic meters per hour": 1.68,
    },
    "50 to <60": {
      "mean cubic meters per hour": 1.74,
    },
    "60 to <70": {
      "mean cubic meters per hour": 1.56,
    },
    "70 to <80": {
      "mean cubic meters per hour": 1.5,
    },
    ">= 80": {
      "mean cubic meters per hour": 1.5,
    },
  },
  "High Intensity": {
    "1 to <3": {
      "mean cubic meters per hour": 2.28,
    },
    "3 to <6": {
      "mean cubic meters per hour": 2.22,
    },
    "6 to <11": {
      "mean cubic meters per hour": 2.52,
    },
    "11 to <16": {
      "mean cubic meters per hour": 2.94,
    },
    "16 to <21": {
      "mean cubic meters per hour": 2.94,
    },
    "21 to <30": {
      "mean cubic meters per hour": 3.0,
    },
    "30 to <40": {
      "mean cubic meters per hour": 2.94,
    },
    "40 to <50": {
      "mean cubic meters per hour": 3.12,
    },
    "50 to <60": {
      "mean cubic meters per hour": 3.18,
    },
    "60 to <70": {
      "mean cubic meters per hour": 2.82,
    },
    "70 to <80": {
      "mean cubic meters per hour": 2.82,
    },
    ">= 80": {
      "mean cubic meters per hour": 2.88,
    },
  }
}

export const infectorActivityTypes = infectorActivityTypeMapping

export const hourToIndex = {
  '1 AM': 0,
  '2 AM': 1,
  '3 AM': 2,
  '4 AM': 3,
  '5 AM': 4,
  '6 AM': 5,
  '7 AM': 6,
  '8 AM': 7,
  '9 AM': 8,
  '10 AM': 9,
  '11 AM': 10,
  '12 PM': 11,
  '1 PM': 12,
  '2 PM': 13,
  '3 PM': 14,
  '4 PM': 15,
  '5 PM': 16,
  '6 PM': 17,
  '7 PM': 18,
  '8 PM': 19,
  '9 PM': 20,
  '10 PM': 21,
  '11 PM': 22,
  '12 AM': 23,
}


export function computeRiskWithVariableOccupancy(
  event,
  probaRandomSampleOfOneIsInfectious,
  flowRate,
  roomUsableVolumeCubicMeters,
  susceptibleMaskType,
  eventDisplayRiskTime
) {
  // const probaRandomSampleOfOneIsInfectious = this.numPositivesLastSevenDays
    // * this.uncountedFactor / this.numPopulation
  // const flowRate = this.measurements.roomUsableVolumeCubicMeters * this.measurements.totalAch
  const susceptibleAgeGroup = '30 to <40' // TODO:
  const susceptibleMaskPenentrationFactor = maskToPenetrationFactor[susceptibleMaskType]

  const basicInfectionQuanta = 18.6
  const variantMultiplier = 3.3
  const quanta = basicInfectionQuanta * variantMultiplier
  const duration = 1

  // TODO: randomly pick from the set of activity groups. Let's say there
  // are two activity groups, one with 10 people who are doing X and 5
  // people doing Y.
  // Activity Factor for Y should be sampled about 5 out of 15 times?
  const activityGroups = event.activityGroups
  const maximumOccupancy = event.maximumOccupancy

  let date = new Date()
  let occupancy;
  if (eventDisplayRiskTime == "At this hour") {
    occupancy = findCurrentOccupancy(maximumOccupancy, date, event.occupancy.parsed)
  } else {
    occupancy = maximumOccupancy
  }

  const numSamples = 1000000

  let r = simplifiedRisk(
    activityGroups,
    occupancy,
    flowRate,
    quanta,
    susceptibleMaskPenentrationFactor,
    susceptibleAgeGroup,
    probaRandomSampleOfOneIsInfectious,
    duration
  )

  let digitsFactor = 1000000

  return Math.round(r * digitsFactor) / digitsFactor
}


// export function computeRisk(maxOccupancy, date, parsed) {
  // const day = DAYS[date.getDay()]
  // const hour = indexToHour[date.getHours()]
//
  // if (parsed[day] && parsed[day][hour] && parsed[day][hour]['occupancyPercent']) {
    // return Math.round(parseFloat(parsed[day][hour]['occupancyPercent']) / 100.0  * maxOccupancy)
  // }
//
  // return 0
// }
//
export function findCurrentOccupancy(maxOccupancy, date, parsed) {
  const day = DAYS[date.getDay()]
  const hour = indexToHour[date.getHours()]

  if (parsed[day] && parsed[day][hour] && parsed[day][hour]['occupancyPercent']) {
    return Math.round(parseFloat(parsed[day][hour]['occupancyPercent']) / 100.0  * maxOccupancy)
  }

  return 0
}

function findWorstCaseInhalationFactor(activityGroups, susceptibleAgeGroup) {
  let inhalationFactor = 0
  let val;
  let ageGroup = 0
  let activity = ""
  let tmpActivity = ""

  for (let activityGroup of activityGroups) {
    if (!susceptibleAgeGroup) {
      susceptibleAgeGroup = activityGroup['ageGroup']
    }

    tmpActivity = co2ActivityToSusceptibleBreathingActivity[
      activityGroup['carbonDioxideGenerationActivity']
    ]

    val = susceptibleBreathingActivityToFactor[
      tmpActivity
    ][susceptibleAgeGroup]['mean cubic meters per hour']

    if (val > inhalationFactor) {
      ageGroup = susceptibleAgeGroup
      inhalationFactor = val
      activity = tmpActivity
    }
    inhalationFactor = Math.max(val, inhalationFactor)
  }

  return {
    'inhalationFactor': inhalationFactor,
    'inhalationActivity': activity,
    'ageGroup': ageGroup
  }
}

export function findWorstCaseInhFactor(activityGroups, susceptibleAgeGroup) {
  return findWorstCaseInhalationFactor(activityGroups, susceptibleAgeGroup)
}

export function simplifiedRisk(
  activityGroups,
  occupancy,
  flowRate,
  quanta,
  susceptibleMaskPenentrationFactor,
  susceptibleAgeGroup,
  probaRandomSampleOfOneIsInfectious,
  duration
) {
  let total = 0.0

  let susceptibleInhalationFactor = findWorstCaseInhalationFactor(
    activityGroups,
    susceptibleAgeGroup
  )
  let infectorSpecificTerm = 1.0

  let totalPeople = getTotalNumberOfPeopleinActivityGroups(activityGroups)

  for (let activityGroup of activityGroups) {
    let numberOfPeople = Math.round(parseFloat(activityGroup['numberOfPeople']) / totalPeople * occupancy)
    let probaAtLeastOneInfectious = 1.0 - (1.0 - probaRandomSampleOfOneIsInfectious) ** numberOfPeople

    let aerosolGenerationActivityFactor = infectorActivityTypeMapping[
      activityGroup['aerosolGenerationActivity']
    ]
    let maskPenetrationFactor = maskToFactor[activityGroup['maskType']]

    infectorSpecificTerm = maskPenetrationFactor * aerosolGenerationActivityFactor

    // What inhalation factor should we choose?
    // Pick the worst one?
    total += computeRisk(
      flowRate,
      quanta,
      infectorSpecificTerm,
      susceptibleInhalationFactor,
      susceptibleMaskPenentrationFactor,
      duration
    ) * probaAtLeastOneInfectious
  }

  return total
}

export function sampleComputeRisk(
  numSamples,
  activityGroups,
  occupancy,
  flowRate,
  quanta,
  susceptibleMaskPenentrationFactor,
  susceptibleAgeGroup,
  probaRandomSampleOfOneIsInfectious
) {
  let totalPeople = getTotalNumberOfPeopleinActivityGroups(activityGroups)
  let peopleBehaviors = generatePeopleBehaviors(
    activityGroups,
    occupancy,
    totalPeople,
    susceptibleAgeGroup
  )

  let infectionCount = 0

  for (let i = 0; i < numSamples; i++) {
    // pick a susceptible behavior
    const susceptibleIndex = Math.floor(Math.random() * peopleBehaviors.length)
    const susceptible = peopleBehaviors[susceptibleIndex]

    let totalInfectorQuantaPerHour = computeTotalInfectorQuantaPerHour(
      peopleBehaviors,
      probaRandomSampleOfOneIsInfectious
    )

    let risk = computeRisk(
      flowRate,
      quanta,
      totalInfectorQuantaPerHour,
      susceptible['inhalationFactor'],
      susceptibleMaskPenentrationFactor,
      1
    )

    if (Math.random() < risk) {
      infectionCount += 1
    }
  }

  return parseFloat(infectionCount) / numSamples
}

function getTotalNumberOfPeopleinActivityGroups(activityGroups) {
  let totalPeople = 0
  for (let activityGroup of activityGroups) {
    totalPeople += parseInt(activityGroup.numberOfPeople)
  }

  return totalPeople
}

function computeTotalInfectorQuantaPerHour(peopleBehaviors, probaRandomSampleOfOneIsInfectious) {
  let totalInfectorQuantaPerHour = 0.0

  for (let peopleBehavior of peopleBehaviors) {
    let infectorAgeGroup = peopleBehavior['ageGroup']

    if (Math.random() < probaRandomSampleOfOneIsInfectious) {
      totalInfectorQuantaPerHour += peopleBehavior['aerosolGenerationActivityFactor']
        * peopleBehavior['maskPenetrationFactor']
    }
  }

  return totalInfectorQuantaPerHour
}

function generatePeopleBehaviors(
  activityGroups,
  occupancy,
  totalPeople,
  susceptibleAgeGroup
) {
  // generate an array of behaviors where each item represents an individual
  let peopleBehaviors = []

  for (let activityGroup of activityGroups) {
    let numPeopleActivityGroup = parseInt(
      occupancy * parseFloat(activityGroup['numberOfPeople']) / totalPeople
    )

    for (let i = 0; i < numPeopleActivityGroup; i++) {
      peopleBehaviors.push({
        'aerosolGenerationActivityFactor': infectorActivityTypeMapping[
          activityGroup['aerosolGenerationActivity']
        ],
        'maskPenetrationFactor': maskToFactor[activityGroup['maskType']],
        'inhalationFactor': susceptibleBreathingActivityToFactor[
          co2ActivityToSusceptibleBreathingActivity[
            activityGroup['carbonDioxideGenerationActivity']
          ]
        ][susceptibleAgeGroup]['mean cubic meters per hour']
      })
    }
  }

  return peopleBehaviors
}

export function filterEvents(search, events) {
  let collection = []
  const lowercasedSearch = search.toLowerCase()
  let typeFound

  for (let event of events) {
    typeFound = false

    for (let type of event.placeData.types) {
      if (type.match(search)) {
        typeFound = true
      }
    }
    if (event.roomName.toLowerCase().match(lowercasedSearch)
      || typeFound
      || event.placeData.formattedAddress.toLowerCase().match(lowercasedSearch)) {
      collection.push(event)
    }
  }

  return collection
}

export function round(val, numDigits) {
  const factor = 10**numDigits
  return Math.round(val * factor) / factor
}
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

export function interpolateRgb(prevColor, nextColor, prevVal, currVal, nextVal) {
  let distanceFromPrevToNextVal = Math.abs(
    (nextVal - prevVal)
  )

  let distanceFromCurrToNext = Math.abs(
    (currVal - nextVal)
  )

  let multiplier = distanceFromCurrToNext / distanceFromPrevToNextVal

  let red = nextColor.r + (prevColor.r - nextColor.r) * multiplier
  let green = nextColor.g + (prevColor.g - nextColor.g) * multiplier
  let blue = nextColor.b + (prevColor.b - nextColor.b) * multiplier

  return `rgb(${parseInt(red)}, ${parseInt(green)}, ${parseInt(blue)})`;
}


export function parseOccupancyHTML(value) {
  const occupancyRegex = /\w+\s?\d*\%\s*busy\s*\w*\s*\d*\s*[A-Z]*/g
  const closedDaysRegex = /(?<=Closed )\w+/g
  const percentRegex = /(\d+)(?=\% busy)/g
  const hourRegex = /(?<=at )(\d+ \w{2})/g
  const usuallyRegex = /(?<=usually )(\d+)(?=% busy)/
  const currentlyRegex = /Currently/

  const matches = value.match(occupancyRegex)
  const closedDays = value.match(closedDaysRegex) || []

  let closedIndices = []
  for (let closedDay of closedDays) {
    closedIndices.push(daysToIndexDict[closedDay])
  }

  let offset = 0
  const numberOfHours = 18
  const maxHours = 7 * numberOfHours

  let dictionary = {
    'Sundays': {},
    'Mondays': {},
    'Tuesdays': {},
    'Wednesdays': {},
    'Thursdays': {},
    'Fridays': {},
    'Saturdays': {},
  }

  console.log(matches)

  let numDaysSkipped = 0;

  for (const day in daysToIndexDict) {
    let dayIndex = daysToIndexDict[day]

    if (closedIndices.includes(dayIndex)) {
      numDaysSkipped += 1
      continue
    }

    let percentVal;
    let hourVal;
    let indexToRemove;

    for (let h = 0; h < matches.length; h++) {
      if (matches[h].match(currentlyRegex)) {
        indexToRemove = h
      }
    }

    if (indexToRemove) {
      matches.splice(indexToRemove, 1)
    }

    let regex;

    for (let h = 0; h < numberOfHours; h++) {
      let overall_index = h + (dayIndex - numDaysSkipped) * numberOfHours;
      if (matches[overall_index].match(usuallyRegex)) {
        regex = usuallyRegex;
      } else {
        regex = percentRegex;
      }

      percentVal = matches[overall_index].match(regex)[0]
      if (matches[overall_index].match(/\d+ [A|P]M/)) {
        hourVal = matches[overall_index].match(/\d+ [A|P]M/)[0]
      } else {
        // We've encountered a "usually block"
        let newIndex = hourToIndex[hourVal] + 1
        hourVal = indexToHour[newIndex]
      }

      dictionary[day][hourVal] = {
        'occupancyPercent': percentVal,
      }
    }
  }

  return dictionary
}

export function getWeekdayText(placeData) {
  if (!placeData.openingHours) {
    return ["N/A"]
  } else {
    return placeData.openingHours.weekdayText
  }
}

function snakeToCamel(str) {
  if (!str.match("_")) {
    return str
  }

  return str.toLowerCase().replace(/([-_][a-z])/g, group =>
    group
      .toUpperCase()
      .replace('-', '')
      .replace('_', '')
  );
}

export function deepSnakeToCamel(obj) {
  /*
   * Useful for converting nested objects / arrays. Ruby convention is to use
   * snake_case while Javascript convention is to use camelCase. This should be
   * used when converting data from the Rails backend into Javascript.
   */
  let new_obj;

  if (Array.isArray(obj)) {
    new_obj = []
  } else if (typeof(obj) == 'object') {
    new_obj = {}
  } else {
    return obj
  }

  for (let o in obj) {
    new_obj[snakeToCamel(o)] = deepSnakeToCamel(obj[o])
  }

  return new_obj
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

export function convertLengthBasedOnMeasurementType(
  from_num,
  from_measurement_type,
  to_measurement_type,
) {
  if (from_measurement_type == to_measurement_type) {
    return parseFloat(from_num)
  } else if (from_measurement_type == 'feet' && to_measurement_type == 'meters'){
    return parseFloat(from_num) / FEET_PER_METER
  } else if (from_measurement_type == 'meters' && to_measurement_type == 'feet'){
    return parseFloat(from_num) * FEET_PER_METER
  } else if (from_measurement_type == 'inches' && to_measurement_type == 'meters') {
    return parseFloat(from_num) / INCHES_PER_FOOT / FEET_PER_METER
  }
}

export function convertCubicMetersPerHour(
  from_num,
  to_unit
) {
  /*
   * m3 / h * 1h / 60 min * ft3 / m3
   */
  if (to_unit == "cubic feet per minute") {
    return from_num / 60 *
      convertLengthBasedOnMeasurementType(1, 'meters', 'feet') ** 3
  } else if (to_unit == 'cubic meters per hour') {
    return from_num
  }
}

export function getMeasurementUnits(systemOfMeasurement) {
  let lengthMeasurementType;
  let airDeliveryRateMeasurementType;
  let airDeliveryRateMeasurementTypeShort;
  let cubicLengthShort;

  if (systemOfMeasurement == 'imperial') {
    lengthMeasurementType = 'feet';
    airDeliveryRateMeasurementType = 'cubic feet per minute';
    airDeliveryRateMeasurementTypeShort = 'ft³ / min';
    cubicLengthShort = 'ft³'
  } else {
    lengthMeasurementType = 'meters';
    airDeliveryRateMeasurementType = 'cubic meters per hour';
    airDeliveryRateMeasurementTypeShort = 'm³ / h';
    cubicLengthShort = 'm³'
  }

  return {
    'lengthMeasurementType': lengthMeasurementType,
    'airDeliveryRateMeasurementType': airDeliveryRateMeasurementType,
    'airDeliveryRateMeasurementTypeShort': airDeliveryRateMeasurementTypeShort,
    'cubicLengthShort': cubicLengthShort
  }
}

// TODO: replace this with convertLengthBasedOnMeasurementType
export function feetToMeters(measurement_type, num) {
  if (measurement_type == 'feet') {
    return num / 3.048
  } else {
    return num
  }
}

export function cubicFeetPerMinuteTocubicMetersPerHour(measurement_type, num) {
  if (measurement_type == 'cubic feet per minute') {
    return parseFloat(num) * 60 / CUBIC_FEET_PER_CUBIC_METER
  } else if (measurement_type == 'cubic meters per hour') {
    return parseFloat(num)
  } else {
    throw `measurement_type ${measurement_type} not recognized.`
  }
}

export function displayCADR(systemOfMeasurement, cubicMetersPerHour) {
  if (systemOfMeasurement == 'imperial') {
    return parseFloat(cubicMetersPerHour) / 60 * CUBIC_FEET_PER_CUBIC_METER
  } else if (systemOfMeasurement == 'metric') {
    return parseFloat(cubicMetersPerHour)
  }
  // else {
    // throw `measurement_type ${measurement_type} not recognized.`
  // }
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

const indexToHour = [
  '1 AM',
  '2 AM',
  '3 AM',
  '4 AM',
  '5 AM',
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
  '12 AM',
]


export const daysToIndexDict = {
  'Sundays': 0,
  'Mondays': 1,
  'Tuesdays': 2,
  'Wednesdays': 3,
  'Thursdays': 4,
  'Fridays': 5,
  'Saturdays': 6,
}

export function computeRisk(
  flowRate,
  quanta,
  infectorSpecificTerm,
  susceptibleInhalationFactor,
  susceptibleMaskPenentrationFactor,
  duration
) {

    const denominator = flowRate

    const susceptibleSpecificTerm = susceptibleInhalationFactor
      * susceptibleMaskPenentrationFactor

    const numerator = quanta * infectorSpecificTerm
      * susceptibleSpecificTerm * duration

    return 1 - Math.exp(- numerator / denominator)
}
