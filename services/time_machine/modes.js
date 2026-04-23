const localMode = require('./local')
const realMode = require('./real')

const MODES = {
  api: {
    key: 'api',
    label: '当前模式：真实接口',
    buttonSubtext: '0.5 秒后请求真实接口',
    service: realMode
  },
  local: {
    key: 'local',
    label: '当前模式：本地演示',
    buttonSubtext: '0.5 秒后生成本地演示结果',
    service: localMode
  }
}

function getModeConfig(modeKey) {
  return MODES[modeKey] || MODES.api
}

module.exports = {
  getModeConfig
}
