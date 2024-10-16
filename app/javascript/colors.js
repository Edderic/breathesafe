import { infectorActivityTypes } from './misc.js'

export const toggleCSS = {
  'text-align': 'center',
  'background-color': '#ccc',
  'width': '3em',
  'height': '3em',
  'display': 'flex',
  'align-items': 'center',
  'justify-content': 'center',
  'border-radius': '100%',
  'cursor': 'help',
}

export const facialMeasurementsPresenceColorMapping = {
  'Complete': {
    name: 'green',
    r: 87,
    g: 195,
    b: 40
  },
  'Partially missing': {
    name: 'yellow',
    r: 255,
    g: 233,
    b: 56
  },
  'Completely missing': {
    name: 'red',
    r: 219,
    g: 21,
    b: 0
  },
}

export const userSealCheckColorMapping = {
  'Passed': {
    name: 'green',
    r: 87,
    g: 195,
    b: 40
  },
  'Skipped': {
    name: 'yellow',
    r: 255,
    g: 233,
    b: 56
  },
  'Failed': {
    name: 'red',
    r: 219,
    g: 21,
    b: 0
  },
  'Incomplete': {
    name: 'gray',
    r: 170,
    g: 170,
    b: 170
  }
}

const paletteFall = [
  {
    name: 'darkRed',
    r: 174,
    g: 17,
    b: 0
  },
  {
    name: 'red',
    r: 219,
    g: 21,
    b: 0
  },
  {
    name: 'orange',
    r: 245,
    g: 150,
    b: 2
  },
  {
    name: 'yellow',
    r: 255,
    g: 233,
    b: 56
  },
  {
    name: 'green',
    r: 87,
    g: 195,
    b: 40
  },
  {
    name: 'dark green',
    r: 11,
    g: 161,
    b: 3
  }
]

const gcm = {
  'A': { 'bounds': [0, 0.001], color: paletteFall[5] },
  'B': { 'bounds': [0.001, 0.01], color: paletteFall[4] },
  'C': { 'bounds': [0.01, 0.05], color: paletteFall[3] },
  'D': { 'bounds': [0.05, 0.1], color: paletteFall[2] },
  'E': { 'bounds': [0.1, 0.2], color: paletteFall[1] },
  'F': { 'bounds': [0.2, 1], color: paletteFall[0] },
}

export const gradeColorMapping = gcm;

export function riskToGrade(risk) {
  for (let grade in gcm) {
    let bounds =  gcm[grade].bounds
    if (risk > bounds[0] && risk <= bounds[1]) {
      return grade
    }
  }
}

export function perimeterColorScheme() {
  const minimum = 300;
  const maximum = 430
  const numObjects = 6

  return genColorSchemeBounds(minimum, maximum, numObjects)
}

export const colorPaletteFall = paletteFall


export function colorInterpolationSchemeRoomVolume(measurementUnits) {
  return assignBoundsToScheme(colorSchemeFall, cutoffVol(measurementUnits))
}

export const colorSchemeFall = [
  {
    'upperColor': {
      name: 'red',
      r: 219,
      g: 21,
      b: 0
    },
    'lowerColor': {
      name: 'darkRed',
      r: 174,
      g: 17,
      b: 0
    },
  },
  {
    'upperColor': {
      name: 'orange',
      r: 245,
      g: 150,
      b: 2
    },
    'lowerColor': {
      name: 'red',
      r: 219,
      g: 21,
      b: 0
    },
  },
  {
    'upperColor': {
      name: 'yellow',
      r: 255,
      g: 233,
      b: 56
    },
    'lowerColor': {
      name: 'orange',
      r: 245,
      g: 150,
      b: 2
    },
  },
  {
    'lowerColor': {
      name: 'yellow',
      r: 255,
      g: 233,
      b: 56
    },
    'upperColor': {
      name: 'green',
      r: 87,
      g: 195,
      b: 40
    },
  },
  {
    'lowerColor': {
      name: 'green',
      r: 87,
      g: 195,
      b: 40
    },
    'upperColor': {
      name: 'dark green',
      r: 11,
      g: 161,
      b: 3
    },
  },
]

export function genColorSchemeBounds(minimum, maximum, numObjects, palette) {
  if (palette == undefined) {
    palette = paletteFall
  }

  const evenSpacedBounds = genEvenSpacedBounds(minimum, maximum, numObjects)

  const scheme = convColorListToCutpoints(
    JSON.parse(JSON.stringify(palette)).reverse()
  )

  return assignBoundsToScheme(scheme, evenSpacedBounds)
}

export function minutesToRemovalScheme() {
  const minimum = 0
  const maximum = 120
  const numObjects = 6
  const evenSpacedBounds = genEvenSpacedBounds(minimum, maximum, numObjects)

  const scheme = convColorListToCutpoints(
    JSON.parse(JSON.stringify(paletteFall)).reverse()
  )

  return assignBoundsToScheme(scheme, evenSpacedBounds)
}

function cutoffVol(measurementUnits) {
  let factor = 500 // cubic meters per hour
  let collection = []

  if (measurementUnits['airDeliveryRateMeasurementType'] == 'cubic feet per minute') {
    factor = factor / 60 * 35.3147 // cubic feet per minute
  }
  for (let i = 0; i < colorSchemeFall.length; i++) {
    collection.push(
      {
        'lowerBound': (i) * factor,
        'upperBound': (i + 1) * factor,
      }
    )
  }

  return collection
}

export function cutoffsVolume(measurementUnits) {
  return cutoffVol(measurementUnits)
}

export const colorInterpolationSchemeAch = [
{
  'lowerBound': 0,
  'upperBound': 2,
  'upperColor': {
    name: 'red',
    r: 219,
    g: 21,
    b: 0
  },
  'lowerColor': {
    name: 'darkRed',
    r: 174,
    g: 17,
    b: 0
  },
},
  {
    'lowerBound': 2,
    'upperBound': 4,
    'upperColor': {
      name: 'orangeRed',
      r: 240,
      g: 90,
      b: 0
    },
    'lowerColor': {
      name: 'red',
      r: 219,
      g: 21,
      b: 0
    },
  },
  {
    'lowerBound': 4,
    'upperBound': 8,
    'upperColor': {
      name: 'yellow',
      r: 255,
      g: 233,
      b: 56
    },
    'lowerColor': {
      name: 'orangeRed',
      r: 240,
      g: 90,
      b: 0
    },
  },
  {
    'lowerBound': 8,
    'upperBound': 16,
    'lowerColor': {
      name: 'yellow',
      r: 255,
      g: 233,
      b: 56
    },
    'upperColor': {
      name: 'green',
      r: 87,
      g: 195,
      b: 40
    },
  },
  {
    'lowerBound': 16,
    'upperBound': 100,
    'lowerColor': {
      name: 'green',
      r: 87,
      g: 195,
      b: 40
    },
    'upperColor': {
      name: 'dark green',
      r: 11,
      g: 161,
      b: 3
    },
  },
]

/*
 * < 500
 * 700
 * 900
 * 1200
 * 1500
 * 2000
 */
export const co2ColorScheme = [
  {
    'lowerBound': 1500,
    'upperBound': 2000,
    'lowerColor': {
      name: 'red',
      letterGrade: 'E',
      r: 219,
      g: 21,
      b: 0
    },
    'upperColor': {
      name: 'darkRed',
      letterGrade: 'F',
      r: 174,
      g: 17,
      b: 0
    },
  },
  {
    'lowerBound': 1200,
    'upperBound': 1500,
    'lowerColor': {
      letterGrade: 'D',
      name: 'orange',
      r: 245,
      g: 150,
      b: 2
    },
    'upperColor': {
      name: 'red',
      letterGrade: 'E',
      r: 219,
      g: 21,
      b: 0
    },
  },
  {
    'lowerBound': 900,
    'upperBound': 1200,
    'lowerColor': {
      name: 'yellow',
      letterGrade: 'C',
      r: 255,
      g: 233,
      b: 56
    },
    'upperColor': {
      letterGrade: 'D',
      name: 'orange',
      r: 245,
      g: 150,
      b: 2
    },
  },
  {
    'lowerBound': 700,
    'upperBound': 900,
    'lowerColor': {
      name: 'green',
      letterGrade: 'B',
      r: 87,
      g: 195,
      b: 40
    },
    'upperColor': {
      name: 'yellow',
      letterGrade: 'C',
      r: 255,
      g: 233,
      b: 56
    },
  },
  {
    'lowerBound': 370,
    'upperBound': 700,
    'lowerColor': {
      name: 'dark green',
      letterGrade: 'A',
      r: 87,
      g: 195,
      b: 40
    },
    'upperColor': {
      name: 'green',
      letterGrade: 'B',
      r: 11,
      g: 161,
      b: 3
    },
  },
]

export const fitFactorColorScheme = [
  {
    'lowerBound': 1,
    'upperBound': 5,
    'lowerColor': {
      name: 'darkRed',
      letterGrade: 'F',
      r: 174,
      g: 17,
      b: 0
    },
    'upperColor': {
      name: 'red',
      letterGrade: 'E',
      r: 219,
      g: 21,
      b: 0
    },
  },
  {
    'lowerBound': 5,
    'upperBound': 10,
    'lowerColor': {
      name: 'red',
      letterGrade: 'E',
      r: 219,
      g: 21,
      b: 0
    },
    'upperColor': {
      letterGrade: 'D',
      name: 'orange',
      r: 245,
      g: 150,
      b: 2
    },
  },
  {
    'lowerBound': 10,
    'upperBound': 20,
    'lowerColor': {
      letterGrade: 'D',
      name: 'orange',
      r: 245,
      g: 150,
      b: 2
    },
    'upperColor': {
      name: 'yellow',
      letterGrade: 'C',
      r: 255,
      g: 233,
      b: 56
    },
  },
  {
    'lowerBound': 20,
    'upperBound': 100,
    'lowerColor': {
      name: 'yellow',
      letterGrade: 'C',
      r: 255,
      g: 233,
      b: 56
    },
    'upperColor': {
      name: 'green',
      letterGrade: 'B',
      r: 87,
      g: 195,
      b: 40
    },
  },
  {
    'lowerBound': 100,
    'upperBound': 1000,
    'lowerColor': {
      name: 'green',
      letterGrade: 'B',
      r: 11,
      g: 161,
      b: 3
    },
    'upperColor': {
      name: 'dark green',
      letterGrade: 'A',
      r: 87,
      g: 195,
      b: 40
    },
  },
]
export const riskColorInterpolationScheme = [
  {
    'lowerBound': 0.1,
    'upperBound': 1,
    'lowerColor': {
      name: 'red',
      letterGrade: 'E',
      r: 219,
      g: 21,
      b: 0
    },
    'upperColor': {
      name: 'darkRed',
      letterGrade: 'F',
      r: 174,
      g: 17,
      b: 0
    },
  },
  {
    'lowerBound': 0.05,
    'upperBound': 0.1,
    'lowerColor': {
      letterGrade: 'D',
      name: 'orange',
      r: 245,
      g: 150,
      b: 2
    },
    'upperColor': {
      name: 'red',
      letterGrade: 'E',
      r: 219,
      g: 21,
      b: 0
    },
  },
  {
    'lowerBound': 0.01,
    'upperBound': 0.05,
    'lowerColor': {
      name: 'yellow',
      letterGrade: 'C',
      r: 255,
      g: 233,
      b: 56
    },
    'upperColor': {
      letterGrade: 'D',
      name: 'orange',
      r: 245,
      g: 150,
      b: 2
    },
  },
  {
    'lowerBound': 0.005,
    'upperBound': 0.01,
    'lowerColor': {
      name: 'green',
      letterGrade: 'B',
      r: 87,
      g: 195,
      b: 40
    },
    'upperColor': {
      name: 'yellow',
      letterGrade: 'C',
      r: 255,
      g: 233,
      b: 56
    },
  },
  {
    'lowerBound': 0.000000,
    'upperBound': 0.005,
    'lowerColor': {
      name: 'dark green',
      letterGrade: 'A',
      r: 87,
      g: 195,
      b: 40
    },
    'upperColor': {
      name: 'green',
      letterGrade: 'B',
      r: 11,
      g: 161,
      b: 3
    },
  },
]

export const AEROSOL_GENERATION_BOUNDS = [
  {
    'lowerBound': infectorActivityTypes['Resting – Oral breathing'],
    'upperBound': infectorActivityTypes['Standing – Speaking'],
  },
  {
    'lowerBound': infectorActivityTypes['Standing – Speaking'],
    'upperBound': infectorActivityTypes['Light exercise – Speaking']
  },
  {
    'lowerBound': infectorActivityTypes['Light exercise – Speaking'],
    'upperBound': infectorActivityTypes['Heavy exercise – Speaking']
  },
  {
    'lowerBound': infectorActivityTypes['Heavy exercise – Speaking'],
    'upperBound': infectorActivityTypes['Heavy exercise – Loudly speaking']
  },
]

export const infectedPeopleColorBounds = [
  {
    'lowerBound': 1.25,
    'upperBound': 1.5,
  },
  {
    'lowerBound': 1,
    'upperBound': 1.25,
  },
  {
    'lowerBound': 0.75,
    'upperBound': 1
  },
  {
    'lowerBound': 0.5,
    'upperBound': 0.75,
  },
  {
    'lowerBound': 0,
    'upperBound': 0.5,
  },
]

function assignBoundsToScheme(scheme, cutoffs) {
  let colorScheme = JSON.parse(JSON.stringify(scheme))

  for (let i = 0; i < colorScheme.length; i++) {
    let obj = cutoffs[i]
    colorScheme[i]['lowerBound'] = obj['lowerBound']
    colorScheme[i]['upperBound'] = obj['upperBound']
  }

  return colorScheme
}
export function assignBoundsToColorScheme(scheme, cutoffs) {
  return assignBoundsToScheme(scheme, cutoffs)
}

function convColorListToCutpoints(colorList) {
  let collection = []

  for (let i = 0; i < colorList.length - 1; i++) {
    collection.push({
      'lowerColor': colorList[i],
      'upperColor': colorList[i + 1]
    })
  }

  return collection
}

export function convertColorListToCutpoints(colorList) {
  return convColorListToCutpoints(colorList)
}

function genEvenSpacedBounds(min, max, numObjects) {
  let curr = min
  let prev
  let increment = (max - min) / numObjects
  const collection = []

  while (curr < max) {
    prev = curr
    curr += increment

    collection.push({
      'lowerBound': prev,
      'upperBound': curr
    })
  }

  return collection
}

export function generateEvenSpacedBounds(min, max, numObjects) {
  return genEvenSpacedBounds(min, max, numObjects)
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

function closestColorIndex(colorScheme, value) {
  let closestIndex = 0
  let bestValue = 0
  let index = 0

  for (let obj of colorScheme) {
    if (Math.abs(obj['upperBound'] - value) < Math.abs(bestValue - value)) {
      bestValue = obj['upperBound']
      closestIndex = index
    }

    index += 1
  }

  return closestIndex
}

export function binValue(colorScheme, value) {
  if (value == 0) {
    return {
      letterGrade: 'NA',
      r: 20,
      g: 20,
      b: 20,
    }
  }

  for (let obj of colorScheme) {
    if (obj['lowerBound'] <= value && value < obj['upperBound']) {

      return obj['lowerColor']
    }
  }

  let obj = colorScheme[closestColorIndex(colorScheme, value)]
  return obj['upperColor']
}

export function getColor(colorScheme, value) {
  if (!colorScheme || colorScheme.length == 0) {
    return '#aaa'
  }
  for (let obj of colorScheme) {
    if (obj['lowerBound'] <= value && value < obj['upperBound']) {
      return interpolateRgb(
        obj['lowerColor'],
        obj['upperColor'],
        obj['lowerBound'],
        value,
        obj['upperBound']
      )
    }
  }

  let obj = colorScheme[closestColorIndex(colorScheme, value)]
  return interpolateRgb(
    obj['lowerColor'],
    obj['upperColor'],
    obj['lowerBound'],
    obj['upperBound'],
    obj['upperBound']
  )
}
