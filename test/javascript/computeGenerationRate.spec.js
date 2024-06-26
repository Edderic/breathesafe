// inside test/javascript/magicAdd.spec.js
import {computeGenerationRate, computeCO2EmissionRate} from 'misc.js'

describe('computeCO2EmissionRate', function() {
  let activityGroups = [
    {
      id: "360c52db-e0f6-4c71-b790-8e3d7b148ef3",
      ageGroup:"6 to <11",
      maskType:"",
      numberOfPeople:"10",
      aerosolGenerationActivity:"Light exercise - Oral breathing",
      carbonDioxideGenerationActivity:"Sitting reading, writing, typing"
    },
  ]

  test('test', () => {
    let co2GenerationRate = computeCO2EmissionRate(
      activityGroups
    )

    // should be about 2052 according to
    // https://ospe-calc.herokuapp.com/Air_Changes_-_Ventilation
    console.log(co2GenerationRate);
    expect(co2GenerationRate > 0.03).toBe(true);
    expect(co2GenerationRate < 0.04).toBe(true);
  })

});

describe('computeGenerationRate', () => {
  test('Sitting reading, writing, typing w/ 10 occupants', () => {
    let activityGroups = [
      {
        id: "360c52db-e0f6-4c71-b790-8e3d7b148ef3",
        ageGroup:"6 to <11",
        maskType:"",
        numberOfPeople:"10",
        aerosolGenerationActivity:"Light exercise - Oral breathing",
        carbonDioxideGenerationActivity:"Sitting reading, writing, typing"
      },
    ]

    let co2GenerationRate = computeGenerationRate(
      activityGroups
    )

    // should be about 2052 according to
    // https://ospe-calc.herokuapp.com/Air_Changes_-_Ventilation
    console.log(co2GenerationRate);
    expect(co2GenerationRate > 122000).toBe(true);
    expect(co2GenerationRate < 123000).toBe(true);
  })
});

