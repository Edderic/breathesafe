
export class Factor {
  /*
   * A table with a "value" column
   * Parameters:
   *   arrayOfObj:
   *    e.g.
   *      [
   *        {
   *          'column1': 'some val',
   *          'column2': 'another val',
   *          'value': 0.6,
   *        },
   *        {
   *          'column1': 'a',
   *          'column2': 'b',
   *          'value': 0.5,
   *        }
   *      ]
   *
   */
  constructor(arrayOfObj) {
    this.arrayOfObj = arrayOfObj
  }

  div(factor) {
    /*
     * Take the product of this factor with another factor.
     */
    let division = this.doStuff(factor, function(itemAValue, itemBValue) {
      return itemAValue / itemBValue
    })

    return new Factor(division)
  }

  prod(factor) {
    /*
     * Take the product of this factor with another factor.
     */
    let product = this.doStuff(factor, function(itemAValue, itemBValue) {
      return itemAValue * itemBValue
    })

    return new Factor(product)
  }

  doStuff(factor, innerFunc) {
    let product = []

    // Case 1: If the two factors have something in common, group them
    let itemA = this.arrayOfObj[0]
    let itemB = factor.arrayOfObj[0]

    // find common variables between the two factors
    let commonVars = []

    for (let keyA in itemA) {
      for (let keyB in itemB) {
        if (keyA == keyB) {
          commonVars.push(keyA)
        }
      }
    }

    let combo = []


    // combine
    for (let itemA of this.arrayOfObj) {

      for (let itemB of factor.arrayOfObj) {
        let match = true

        for (let c of commonVars) {
          if (c != 'value') {
            match = match && itemA[c] == itemB[c]
          }
        }

        if (match) {
          let newItem = JSON.parse(JSON.stringify(itemA))
          let itemAValue = itemA['value']
          let itemBValue = itemB['value']

          newItem = Object.assign(newItem, itemB)
          newItem['value'] = innerFunc(itemAValue, itemBValue)

          combo.push(newItem)
        }
      }
    }

    return combo
  }


  sum(variables) {
    let cache = {}
    let delimiter = '|'

    // TODO: sort the column names
    for (let itemA of this.arrayOfObj) {
      let longKey = ""

      for (let key in itemA) {
        if (!variables.includes(key) && key != 'value') {
          longKey += `${key}: ${itemA[key]}${delimiter}`
        }
      }

      if (longKey in cache) {
        cache[longKey].push(itemA)
      } else {
        cache[longKey] = [itemA]
      }
    }


    let summedCache = []
    for (let c in cache) {
      let array = cache[c]
      let summation = 0
      for (let item of array) {
        summation += item['value']
      }
      let keyValues = c.split(delimiter)

      let newItem = {}

      for (let kv of keyValues) {
        let keyValue = kv.split(": ")
        if (keyValue.length == 2) {
          newItem[keyValue[0]] = keyValue[1]
        }
      }

      newItem['value'] = summation

      summedCache.push(
        newItem
      )
    }

    return new Factor(summedCache)
  }

  filter(obj) {
    let includables = []
    for (let item of this.arrayOfObj) {
      let include = true
      for (let k in obj) {
        include = include && obj[k] == item[k]
      }

      if (include) {
        includables.push(item)
      }
    }

    return new Factor(includables)
  }
}
