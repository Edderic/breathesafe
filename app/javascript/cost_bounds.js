export function dbWideCostBounds(context) {
  const contextMax = context?.initial_cost_max ?? context?.initialCostMax
  if (contextMax === null || contextMax === undefined) {
    return { min: null, max: null }
  }

  const numericMax = Number(contextMax)
  if (!Number.isFinite(numericMax) || numericMax <= 0) {
    return { min: null, max: null }
  }

  return { min: 0, max: Math.max(numericMax, 5) }
}
