import { infectorActivityTypes } from './misc.js'

export const toggleCSS = {
  'text-align': 'center',
  'background-color': '#ccc',
  'width': '1.5em',
  'height': '1.5em',
  'display': 'flex',
  'align-items': 'center',
  'justify-content': 'center',
  'border-radius': '100%',
  'margin-right': '0.5em',
  'cursor': 'help',
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
export const colorPaletteFall = paletteFall

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

export function cutoffsVolume(measurementUnits) {
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

export const riskColorInterpolationScheme = [
  {
    'lowerBound': 0.1,
    'upperBound': 0.999999,
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
    'lowerBound': -0.000001,
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
    'lowerBound': 4 / 5,
    'upperBound': 1,
  },
  {
    'lowerBound': 3 / 5,
    'upperBound': 4 / 5,
  },
  {
    'lowerBound': 2 / 5,
    'upperBound': 3 / 5
  },
  {
    'lowerBound': 1 / 5,
    'upperBound': 2 / 5,
  },
  {
    'lowerBound': 0 / 5,
    'upperBound': 1 / 5,
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

      if (Math.abs(obj['upperBound'] - value) < Math.abs(obj['lowerBound'] - value)) {
        return obj['upperColor']
      }

      return obj['lowerColor']
    }
  }

  let obj = colorScheme[closestColorIndex(colorScheme, value)]
  return obj['upperColor']
}

export function getColor(colorScheme, value) {
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
