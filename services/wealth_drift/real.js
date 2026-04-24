const { requestDrift, requestConvert } = require('../../utils/api')
const { getCache, setCache } = require('../../utils/cache')

const COMMENT_SOURCE_YEAR = 2025
const DRIFT_CACHE_TTL = 30 * 60 * 1000
const COMMENT_CACHE_TTL = 12 * 60 * 60 * 1000

function buildPayloads(currentCity, targetCity, monthlyIncome) {
  return {
    driftPayload: {
      current_city: currentCity,
      monthly_income: Number(monthlyIncome),
      target_city: targetCity
    },
    commentPayload: {
      amount: Number(monthlyIncome),
      source_year: COMMENT_SOURCE_YEAR,
      city: currentCity
    }
  }
}

async function fetchDriftResult(payload) {
  const cached = getCache('drift', payload, DRIFT_CACHE_TTL)
  if (cached) {
    return cached
  }

  const response = await requestDrift(payload)
  setCache('drift', payload, response)
  return response
}

async function fetchExpertComment(payload) {
  const cached = getCache('comment', payload, COMMENT_CACHE_TTL)
  if (cached) {
    return cached
  }

  const response = await requestConvert(payload)
  setCache('comment', payload, response)
  return response
}

module.exports = {
  buildPayloads,
  fetchDriftResult,
  fetchExpertComment
}
