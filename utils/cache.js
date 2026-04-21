const CACHE_PREFIX = 'wealth_drift_cache_'

function buildCacheKey(namespace, payload) {
  return `${CACHE_PREFIX}${namespace}_${JSON.stringify(payload)}`
}

function setCache(namespace, payload, data) {
  const key = buildCacheKey(namespace, payload)
  wx.setStorageSync(key, {
    timestamp: Date.now(),
    data
  })
}

function getCache(namespace, payload, maxAge) {
  const key = buildCacheKey(namespace, payload)
  const record = wx.getStorageSync(key)

  if (!record || !record.timestamp) {
    return null
  }

  if (Date.now() - record.timestamp > maxAge) {
    wx.removeStorageSync(key)
    return null
  }

  return record.data || null
}

module.exports = {
  getCache,
  setCache
}
