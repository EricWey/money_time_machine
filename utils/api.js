const API_BASE_URL = 'http://127.0.0.1:8000'
const REQUEST_TIMEOUT = 10000

function normalizeErrorMessage(detail, fallbackMessage) {
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((item) => item.msg || item.message || '请求参数错误').join('；')
  }

  if (typeof detail === 'string' && detail) {
    return detail
  }

  return fallbackMessage
}

function buildHttpError(statusCode, detail) {
  if (statusCode === 400) {
    return {
      type: 'validation',
      recoverable: true,
      message: normalizeErrorMessage(detail, '提交的信息不完整或格式不对，请检查后重试。')
    }
  }

  if (statusCode === 404) {
    return {
      type: 'not_found',
      recoverable: true,
      message: normalizeErrorMessage(detail, '目标数据暂时没找到，换个城市再试试。')
    }
  }

  if (statusCode >= 500) {
    return {
      type: 'server',
      recoverable: true,
      message: normalizeErrorMessage(detail, '服务器刚刚有点晕，稍后再试通常就能恢复。')
    }
  }

  return {
    type: 'http',
    recoverable: true,
    message: normalizeErrorMessage(detail, `请求失败（${statusCode}）`)
  }
}

function request({ path, method = 'GET', data, timeout = REQUEST_TIMEOUT }) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE_URL}${path}`,
      method,
      timeout,
      header: {
        'content-type': 'application/json',
        Accept: 'application/json'
      },
      data,
      success: (response) => {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          resolve(response.data)
          return
        }

        reject(buildHttpError(response.statusCode, response.data && response.data.detail))
      },
      fail: (error) => {
        if (error.errMsg && error.errMsg.indexOf('timeout') !== -1) {
          reject({
            type: 'timeout',
            recoverable: true,
            message: '请求超时了，网络可能在摸鱼，建议再试一次。'
          })
          return
        }

        reject({
          type: 'network',
          recoverable: true,
          message: '网络连接失败，请确认后端服务可访问后重试。'
        })
      }
    })
  })
}

function requestDrift(data) {
  return request({
    path: '/api/v1/drift',
    method: 'POST',
    data
  })
}

function requestConvert(data) {
  return request({
    path: '/api/v1/convert',
    method: 'POST',
    data
  })
}

module.exports = {
  API_BASE_URL,
  REQUEST_TIMEOUT,
  requestDrift,
  requestConvert
}
