// import {CostComputer, Employee} from '../app/assets/javascripts/cost_computer.js'
importScripts('cost_computer1.js')

function computeLostWages(
  args
) {
  let dict = {}

  for (let j = 0; j < args.numSims; j++) {
    let employees = []

    for (let i = 0; i < args.numEmployees; i++) {
      employees.push(
        new Employee(
          new Mask(args.employeeMask, 1),
          args.numDaysInEpoch,
          args.schedule,
          args.hourlyRate
        )
      )
    }
    const computer = new CostComputer(
      args.event,
      args.environmentalInterventions,
      args.occupancy,
      employees,
      args.prevalence,
      args.numDaysInEpoch,
      new Mask(args.employeeMask, 1),
    )

    computer.compute()
    dict[j] = computer.getLostWages()
  }

  return dict
}

onmessage = (e) => {
  const result = computeLostWages(JSON.parse(e.data))
  postMessage(JSON.stringify(result));
}
