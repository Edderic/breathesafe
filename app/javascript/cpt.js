/*
 * Conditional Probability Tables
 *
 *
 */

export class CPT {
  constructor(args) {
    this.outcome = args.outcome
    this.factor = args.factor
  }

  toFactor() {
    return this.factor
  }
}
