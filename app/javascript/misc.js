// esversion: 6

import axios from 'axios';

export const QUANTA = 100;
// https://www.sciencedirect.com/science/article/pii/S1674987121001493?via%3Dihub
// could be as high as 1000 quanta per hour for B.1.1.529. See https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8848576/
// The above has a wide distribution. We use 100 quanta (more on the higher end) to be conservative.

const INCHES_PER_FOOT = 12;
const CUBIC_FEET_PER_CUBIC_METER = 35.3147
const CUBIC_METER_PER_CUBIC_FEET = 1 / CUBIC_FEET_PER_CUBIC_METER
const FEET_PER_METER = 3.28084
export const DAYS = [
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
  'KN95': 0.15,
  'N95 - unfitted': 0.1,
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

export function oneInFormat(ratio) {
  if (1 / ratio >= 10) {
    return round(1 / ratio, 0)
  }
  return round(1 / ratio, 1)
}

export function sortArrow(value, applicable) {
  if (!applicable) {
    return "⇵"
  }
  else if (value == 'ascending') {
    return "↑"
  } else if (value == "descending") {
    return "↓"
  }
  else {
    return "⇵"
  }
}

export function computeRiskWithVariableOccupancy(
  event,
  probaRandomSampleOfOneIsInfectious,
  flowRate,
  roomUsableVolumeCubicMeters,
  susceptibleMaskType,
  numWays
) {
  // const probaRandomSampleOfOneIsInfectious = this.numPositivesLastSevenDays
    // * this.uncountedFactor / this.numPopulation
  // const flowRate = this.measurements.roomUsableVolumeCubicMeters * this.measurements.totalAch
  const susceptibleAgeGroup = '30 to <40' // TODO:
  const susceptibleMaskPenentrationFactor = maskToPenetrationFactor[susceptibleMaskType]

  const quanta = QUANTA
  const duration = 1

  // TODO: randomly pick from the set of activity groups. Let's say there
  // are two activity groups, one with 10 people who are doing X and 5
  // people doing Y.
  // Activity Factor for Y should be sampled about 5 out of 15 times?
  let activityGroups = JSON.parse(JSON.stringify(event.activityGroups))
  if (numWays == 2) {
    // two-way masking.
    for (let activityGroup of activityGroups) {
      activityGroup['maskType'] = susceptibleMaskType
    }
  }

  const maximumOccupancy = event.maximumOccupancy

  let date = new Date()
  let occupancy = maximumOccupancy;

  const numSamples = 1000000

  let r = simplifiedRisk(
    activityGroups,
    occupancy,
    flowRate,
    quanta,
    susceptibleMaskPenentrationFactor,
    susceptibleAgeGroup,
    probaRandomSampleOfOneIsInfectious,
    duration,
  )

  return r
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

function steadyStateFactor(a, time) {
  /*
   * Parameters:
   *   c_0: initial concentration (e.g. quanta, CO2 (ppm))
   *   cadr: clean air delivery rate (m3 / h)
   *   generation_rate:  (quanta / h or m3 / h * ppm)
   *   volume: room volume (m3)
   *   time: minutes
   *
   */

  if (!a.generationRate) {
    a.generationRate = 0
  }

  if (!a.c_0) {
    a.c_0 = 0
  }

  if (!a.cBackground) {
    a.cBackground = 0
  }

  let generationRateInMinutes = a.generationRate / 60
  let cadrInMinutes = a.cadr / 60

  return a.cBackground + generationRateInMinutes / cadrInMinutes + (a.c_0 - a.cBackground - generationRateInMinutes / cadrInMinutes) * Math.exp(-a.cadr / a.roomUsableVolumeCubicMeters * time / 60)
}

export function steadyStateFac(a, time) {
  return steadyStateFactor(a, time)
}

function integrateSteadyStateFactor(duration, steadyStateFactorArgs) {
  /*
   * Parameters:
   *   duration: hours
   *   steadyStateFactorArgs: Object
   */
  let sum = 0
  let cumulative = []

  for (let i = 1; i <= duration; i++) {
    // Scale by hour
    sum += steadyStateFactor(steadyStateFactorArgs, i)
    cumulative.push(sum)
  }

  return {
    sum: sum,
    cumulative: cumulative
  }
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
  duration,
  roomUsableVolumeCubicMeters,
  loop
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
    if (loop) {
      return computeRisk(
        flowRate,
        quanta,
        infectorSpecificTerm,
        susceptibleInhalationFactor['inhalationFactor'],
        susceptibleMaskPenentrationFactor,
        duration,
        roomUsableVolumeCubicMeters,
        loop
      )

    }

    total += computeRisk(
      flowRate,
      quanta,
      infectorSpecificTerm,
      susceptibleInhalationFactor['inhalationFactor'],
      susceptibleMaskPenentrationFactor,
      duration,
      roomUsableVolumeCubicMeters,
      loop
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
  let steadyStateFactor = 1

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


export function filterEvents(search, events, placeType) {
  let collection = []
  const lowercasedSearch = search.toLowerCase()
  let typeFound

  for (let event of events) {
    typeFound = false

    if (!!placeType) {
      for (let type of event.placeData.types) {
        if (type.match(placeType)) {
          typeFound = true
        }
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

function r(val, numDigits) {
  const factor = 10**numDigits
  return Math.round(val * factor) / factor
}

export function round(val, numDigits) {
  return r(val, numDigits)
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

function emissionRate(activityGroups) {
  /*
   * Returns total CO2 emission rate (L/s)
   */
  let total = 0

  for (let activityGroup of activityGroups) {
    let met = getMetFromCO2GenerationActivity(activityGroup['carbonDioxideGenerationActivity'])
    let co2GenerationRate = getCO2GenerationRate(met, activityGroup['sex'] == 'Male', activityGroup['ageGroup'])
    total += co2GenerationRate * parseInt(activityGroup['numberOfPeople'])
  }

  return total
}

export function computeCO2EmissionRate(activityGroups) {
  return emissionRate(activityGroups)
}

function greedy(producer, producerArgs, actualData, gradArgs) {
  // let lastMoves = []

  let minErrorIteration = 100000000
  let lastMinErrorIteration = minErrorIteration
  let possibleError1 = 0

  let bestPosition = {}
  let bestLocalMove = {
    'cadr': 0,
    'c0': 0
  }

  let newData = []
  let copyProducerArgs = {};

  for (let i = 0; i < 1000000; i++) {

    for (let cadr_d of [-1, 0, 1]) {
      for (let c0_d of [-1, 0, 1]) {

        copyProducerArgs = JSON.parse(JSON.stringify(producerArgs))

        if ((producerArgs['c0_d'] < 1 && c0_d == -1) || (producerArgs['cadr_d'] < 1 && cadr_d == -1)) {
          continue
        }

        copyProducerArgs['cadr'] = producerArgs['cadr'] + cadr_d
        copyProducerArgs['c0'] = producerArgs['c0'] + c0_d

        newData = producer(copyProducerArgs)

        possibleError1 = computeError(
          newData,
          actualData,
          (data1, data2) => Math.abs(data1 - data2)
        )

        if (possibleError1 < minErrorIteration) {
          minErrorIteration = possibleError1
          bestLocalMove = JSON.parse(JSON.stringify(copyProducerArgs))
        }
      }
    }

    if (minErrorIteration >= lastMinErrorIteration) {
      return {
        result: bestLocalMove,
        error: lastMinErrorIteration
      }
    }

    lastMinErrorIteration = minErrorIteration
    Object.assign(producerArgs, bestLocalMove)
  }

  return {
    result: bestLocalMove,
    error: minErrorIteration
  }
}

function gradientDescent(producer, producerArgs, actualData, gradArgs) {
  /*
   * Parameters
   *   producer: Function
   *     some function that could produce data. Takes in producerArgs
   *   producerArgs: Object
   *     Arguments for the producer
   *   actualData: Array
   *     Data. Used to compare error
   *
   *   gradArgs: Object
   *     Has stepSize
   */

  let newData = producer(producerArgs)
  let change = {}
  let changeError = 0
  let prevError = 0
  let old = {}

  prevError = computeError(
    newData,
    actualData,
    (data1, data2) => Math.abs(data1 - data2)
  )

  let newProducerArgs = JSON.parse(JSON.stringify(producerArgs))

  for (let searchArg of gradArgs.searchArgs) {
    change[searchArg] = Math.random() * gradArgs.initialStep[searchArg]
    newProducerArgs[searchArg] += change[searchArg]
    old[searchArg] = producerArgs[searchArg]
  }

  newData = producer(newProducerArgs)
  let error = computeError(
    newData,
    actualData,
    (data1, data2) => Math.abs(data1 - data2)
  )

  changeError = error - prevError
  prevError = error
  let trueCount = 0

  for (let i = 0; i < 10000; i++) {
    for (let searchArg of gradArgs.searchArgs) {
      producerArgs[searchArg] = -gradArgs.stepSize[searchArg] * changeError
        / change[searchArg]
        + old[searchArg]
    }

    newData = producer(producerArgs)

    error = computeError(
      newData,
      actualData,
      (data1, data2) => Math.abs(data1 - data2)
    )
    changeError = error - prevError
    prevError = error

    trueCount = 0

    for (let searchArg of gradArgs.searchArgs) {
      change[searchArg] = producerArgs[searchArg] - old[searchArg]
      old[searchArg] = producerArgs[searchArg]

      // if (change[searchArg] < 0.00001 && change[searchArg] > -0.0001) {
        // trueCount += 1
      // }
    }

    // if (trueCount == gradArgs.searchArgs.length) {
       // return {
         // result: producerArgs,
         // error: error
       // }
    // }
  }

  return {
    result: producerArgs,
    error: error
  }
}

export function computeVentilationNIDR(
  activityGroups,
  co2Readings,
  co2Background,
  roomUsableVolumeCubicMeters,
  method
) {
  let useMethod = undefined
  if (!method)  {
    useMethod = 'gradientDescent'
  }
  // Assumption: There are at least two CO2 readings
  // co2Readings are divided by 1000 (i.e. 420 ppm is 0.000420)
  const startCO2 = (co2Readings[0] + co2Readings[1]) / 2
  // L / s * 1 m3 / 1000 L * 3600 seconds / h
  // gives us m3 / h
  // Multiply by 1000000 ppm is the same thing as multiplying by 1
  let generationRate = emissionRate(activityGroups) / 1000 * 3600 * 1000000

  let gradArgs = {
    initialStep: {
      'cadr': 1,
      'c0': 1
    },
    stepSize: {
      'cadr': 0.005,
      'c0': 0.005
    },
    searchArgs: [
      'cadr',
      'c0'
    ]
  }

  let producerArgs = {
    roomUsableVolumeCubicMeters: roomUsableVolumeCubicMeters,
    cadr: 100,
    c0: startCO2,
    generationRate: generationRate,
    cBackground: co2Background,
    windowLength: co2Readings.length
  }

  let errors = []
  let error = 0
  let newData = undefined
  let minError = 1000000000
  let bestArg = 0

  if (useMethod == 'bruteForce') {
    for (let i = 0; i < 1000; i++) {
      producerArgs['cadr'] = i
      newData = generateData(producerArgs)

      error = computeError(newData, co2Readings,
        (data1, data2) => Math.abs(data1 - data2)
      )

      errors.push(error)

      if (error < minError) {
        minError = error
        bestArg = i
      }
    }

    return { cadr: bestArg, error: minError }
  }

  return greedy(
    generateData,
    producerArgs,
    co2Readings,
    gradArgs
  )
}


function computeError(data1, data2, comparatorFunc) {
  /*
   * Assumptions: data1 and data2 are of the same length
   */

  if (data1.length != data2.length) {
    throw `data1 length (${data1.length}) should be equal to data2 length (${data2.length}).`
  }

  let summation = 0

  for (let i = 0; i < data1.length; i++) {
    summation += comparatorFunc(data1[i], data2[i])
  }

  return summation / data1.length
}

function generateData(args) {
  let collection = []

  for (let t=0; t < args.windowLength; t++) {
    collection.push(
      steadyStateFactor({
        roomUsableVolumeCubicMeters: args.roomUsableVolumeCubicMeters,
        c_0: args.c0,
        generationRate: args.generationRate,
        cadr: args.cadr,
        cBackground: parseFloat(args.cBackground)
      }, t)
    )
  }

  return collection
}

export function genConcCurve(args) {
  return generateData(args)
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

  let total = emissionRate(activityGroups)

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

const co2ToMet = {
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

export const CO2_TO_MET = co2ToMet;

function getMetFromCO2GenerationActivity(activity) {
  const mapping = co2ToMet

  return mapping[activity]
}

export function getCO2Rate(met, man, age) {
  return getCO2GenerationRate(met, man, age)
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

export const indexToHour = [
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
  duration,
  roomUsableVolumeCubicMeters,
  durationLoop
) {


    const denominator = flowRate

    const susceptibleSpecificTerm = susceptibleInhalationFactor
      * susceptibleMaskPenentrationFactor

    const numerator = quanta * infectorSpecificTerm
      * susceptibleSpecificTerm

    // Assumptions: the infector comes in at the same time as the susceptible.
    // At the beginning, infectious dose is 0.
    //
    // we pass in generation rate to be same as the cadr = 1 so that we end up with 1 -
    // Math.exp(-ach * t / 60). i.e. we can pass the real values of generation
    // rate / cadr at a later point
    let steadyStateFactorObj = integrateSteadyStateFactor(duration * 60, {
      roomUsableVolumeCubicMeters: roomUsableVolumeCubicMeters,
      generationRate: flowRate,
      cadr: flowRate,
    })

    if (durationLoop) {
      let coll = []

      for (let steadyStateVal of steadyStateFactorObj.cumulative) {

        coll.push(
          1- Math.exp(-steadyStateVal / 60 * numerator / flowRate)
        )
      }

      return coll
    }


    let steadyStateMultiplier = steadyStateFactorObj.sum / 60 // normalize for 1 hr

    let inhaled_quanta = numerator * steadyStateMultiplier / flowRate

    return 1 - Math.exp(- inhaled_quanta)
}
