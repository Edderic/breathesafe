import { infectorActivityTypes } from './misc.js'

export const colorPaletteFall = [
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
    name: 'orangeRed',
    r: 240,
    g: 90,
    b: 0
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

export const riskColorInterpolationScheme = [
  {
    'lowerBound': 0.1,
    'upperBound': 0.999999,
    'lowerColor': {
      name: 'red',
      letterGrade: 'e',
      r: 219,
      g: 21,
      b: 0
    },
    'upperColor': {
      name: 'darkRed',
      letterGrade: 'f',
      r: 174,
      g: 17,
      b: 0
    },
  },
  {
    'lowerBound': 0.01,
    'upperBound': 0.1,
    'lowerColor': {
      name: 'orangeRed',
      letterGrade: 'd',
      r: 240,
      g: 90,
      b: 0
    },
    'upperColor': {
      name: 'red',
      letterGrade: 'e',
      r: 219,
      g: 21,
      b: 0
    },
  },
  {
    'lowerBound': 0.001,
    'upperBound': 0.01,
    'lowerColor': {
      name: 'yellow',
      letterGrade: 'c',
      r: 255,
      g: 233,
      b: 56
    },
    'upperColor': {
      name: 'orangeRed',
      letterGrade: 'e',
      r: 240,
      g: 90,
      b: 0
    },
  },
  {
    'lowerBound': 0.0001,
    'upperBound': 0.001,
    'upperColor': {
      name: 'yellow',
      letterGrade: 'c',
      r: 255,
      g: 233,
      b: 56
    },
    'lowerColor': {
      name: 'green',
      letterGrade: 'b',
      r: 87,
      g: 195,
      b: 40
    },
  },
  {
    'lowerBound': -0.000001,
    'upperBound': 0.0001,
    'upperColor': {
      name: 'green',
      letterGrade: 'b',
      r: 87,
      g: 195,
      b: 40
    },
    'lowerColor': {
      name: 'dark green',
      letterGrade: 'a',
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
    'upperBound': infectorActivityTypes['Heavy Exercise – Speaking']
  },
  {
    'lowerBound': infectorActivityTypes['Heavy Exercise – Speaking'],
    'upperBound': infectorActivityTypes['Heavy Exercise – Loudly Speaking']
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

export function assignBoundsToColorScheme(scheme, cutoffs) {
  let colorScheme = JSON.parse(JSON.stringify(scheme))

  for (let i = 0; i < colorScheme.length; i++) {
    let obj = cutoffs[i]
    colorScheme[i]['lowerBound'] = obj['lowerBound']
    colorScheme[i]['upperBound'] = obj['upperBound']
  }

  return colorScheme
}

export function convertColorListToCutpoints(colorList) {
  let collection = []

  for (let i = 0; i < colorList.length - 1; i++) {
    collection.push({
      'lowerColor': colorList[i],
      'upperColor': colorList[i + 1]
    })
  }

  return collection
}

export function generateEvenSpacedBounds(min, max, numObjects) {
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

export function binColor(colorScheme, value) {
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
