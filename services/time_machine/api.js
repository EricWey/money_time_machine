const { requestConvert } = require('../../utils/api')
const {
  formatCurrency,
  normalizeApiItems
} = require('./shared')

async function convert(amount, year, city) {
  const apiData = await requestConvert({
    amount,
    source_year: Number(year),
    city
  })
  const equivalentAmount = Number(apiData.equivalent_amount || 0)

  return {
    year,
    city,
    sourceAmount: formatCurrency(amount),
    equivalentAmount: formatCurrency(equivalentAmount),
    deltaAmount: formatCurrency(equivalentAmount - amount),
    aiComment: apiData.ai_comment,
    items: normalizeApiItems(apiData.items, year)
  }
}

module.exports = {
  convert
}
