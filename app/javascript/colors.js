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
    'lowerBound': 0.01,
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
    'lowerBound': 0.001,
    'upperBound': 0.01,
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
    'lowerBound': 0.0001,
    'upperBound': 0.001,
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
    'upperBound': 0.0001,
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

export function binValue(colorScheme, value) {
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
