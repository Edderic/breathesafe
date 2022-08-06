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
      r: 219,
      g: 21,
      b: 0
    },
    'upperColor': {
      name: 'darkRed',
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
      r: 240,
      g: 90,
      b: 0
    },
    'upperColor': {
      name: 'red',
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
      r: 255,
      g: 233,
      b: 56
    },
    'upperColor': {
      name: 'orangeRed',
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
      r: 255,
      g: 233,
      b: 56
    },
    'lowerColor': {
      name: 'green',
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
      r: 87,
      g: 195,
      b: 40
    },
    'lowerColor': {
      name: 'dark green',
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
