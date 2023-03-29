/*
 * Conditional Probability Tables
 *
 *
 */

import {Factor} from './factor.js'

export class CPT {
  constructor(args) {
    this.outcome = args.outcome
    this.factor = args.factor
  }

  toFactor() {
    return this.factor
  }
}

export const CPTs = [
  new CPT(
    {
      outcome: 'has_covid',
      factor: new Factor([
        {
          has_covid: 'true',
          value: 0.01
        },
        {
          has_covid: 'false',
          value: 0.99
        },
      ])
    }
  ),
  new CPT(
    {
      outcome: 'pcr',
      factor: new Factor(
        [
          {
            'pcr': '-',
            'has_covid': 'false',
            'value': 0.999
          },
          {
            'pcr': '+',
            'has_covid': 'false',
            'value': 0.001
          },
          {
            'pcr': '+',
            'has_covid': 'true',
            'value': 0.95
          },
          {
            'pcr': '-',
            'has_covid': 'true',
            'value': 0.05
          },
        ]
      )
    }
  ),

  new CPT(
    {
      outcome: 'rapid',
      factor: new Factor(
        [
          {
            'rapid': '-',
            'has_covid': 'false',
            'symptomatic': '-',
            'value': 1.0
          },
          {
            'rapid': '+',
            'has_covid': 'false',
            'symptomatic': '-',
            'value': 0.0
          },
          {
            'rapid': '-',
            'has_covid': 'false',
            'symptomatic': '+',
            'value': 1.0
          },
          {
            'rapid': '+',
            'has_covid': 'false',
            'symptomatic': '+',
            'value': 0.0
          },
          {
            'rapid': '-',
            'has_covid': 'true',
            'symptomatic': '-',
            'value': 0.5
          },
          {
            'rapid': '+',
            'has_covid': 'true',
            'symptomatic': '-',
            'value': 0.5
          },
          {
            'rapid': '+',
            'has_covid': 'true',
            'symptomatic': '+',
            'value': 0.8
          },
          {
            'rapid': '-',
            'has_covid': 'true',
            'symptomatic': '+',
            'value': 0.2
          },
        ]
      )
    }
  ),
  new CPT(
    {

      outcome: 'symptomatic',
      factor: new Factor([
        {
          'symptomatic': '+',
          'has_covid': 'true',
          'value': 0.75,
        },

        {
          'symptomatic': '-',
          'has_covid': 'true',
          'value': 0.25,
        },

        {
          'symptomatic': '+',
          'has_covid': 'false',
          'value': 0.08,
        },
        {
          'symptomatic': '-',
          'has_covid': 'false',
          'value': 0.92,
        },
      ])
    }
  )
]
