const ENV_API_BASE_URLS = {
  develop: 'http://127.0.0.1:8000',
  trial: '',
  release: ''
}

function normalizeBaseUrl(value) {
  return (value || '').trim().replace(/\/+$/, '')
}

function getEnvVersion() {
  try {
    if (wx.getAccountInfoSync) {
      const accountInfo = wx.getAccountInfoSync()
      return accountInfo.miniProgram && accountInfo.miniProgram.envVersion
    }
  } catch (error) {
    return 'develop'
  }

  return 'develop'
}

function getApiBaseUrl() {
  const envVersion = getEnvVersion()
  const baseUrl = normalizeBaseUrl(ENV_API_BASE_URLS[envVersion] || ENV_API_BASE_URLS.develop)
  const isLocalAddress = /^https?:\/\/(localhost|127(?:\.\d{1,3}){3})/i.test(baseUrl)

  if (!baseUrl) {
    throw new Error('未配置 API 地址，请在 utils/apiConfig.js 中填写当前环境对应的后端地址。')
  }

  if (envVersion === 'develop') {
    return baseUrl
  }

  if (isLocalAddress) {
    throw new Error('体验版和正式版不能指向本地服务，请改为可访问的测试环境或生产环境域名。')
  }

  return baseUrl
}

module.exports = {
  getApiBaseUrl
}
