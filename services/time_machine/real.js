const {
  formatCurrency,
  buildVintageComment,
  normalizeApiItems
} = require('./shared')

const API_BASE_URL = 'http://127.0.0.1:8000'
const REQUEST_TIMEOUT = 8000

function requestConvert(data) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE_URL}/api/v1/convert`,
      method: 'POST',
      timeout: REQUEST_TIMEOUT,
      data,
      success: (response) => {
        if (response.statusCode === 200 && response.data) {
          resolve(response.data)
          return
        }

        reject({
          message: '真实接口暂不可用，请稍后重试。'
        })
      },
      fail: () => {
        reject({
          message: '无法连接本地接口，请确认后端服务是否启动。'
        })
      }
    })
  })
}

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
    aiComment: apiData.ai_comment || buildVintageComment(amount, year, city, equivalentAmount),
    items: normalizeApiItems(apiData.items, year)
  }
}

module.exports = {
  convert
}
