const { YEAR_OPTIONS, CITY_OPTIONS } = require('../../services/time_machine/shared')
const { getModeConfig } = require('../../services/time_machine/modes')

Page({
  data: {
    amount: '',
    yearOptions: YEAR_OPTIONS,
    cityOptions: CITY_OPTIONS,
    yearIndex: 35,
    cityIndex: 0,
    selectedYear: YEAR_OPTIONS[35],
    selectedCity: CITY_OPTIONS[0],
    loading: false,
    loadingText: '',
    debugMode: 'api',
    modeLabel: getModeConfig('api').label,
    buttonSubtext: getModeConfig('api').buttonSubtext,
    result: null,
    error: ''
  },

  bindAmountInput(e) {
    this.setData({
      amount: e.detail.value,
      error: ''
    })
  },

  bindYearChange(e) {
    const yearIndex = Number(e.detail.value)
    this.setData({
      yearIndex,
      selectedYear: this.data.yearOptions[yearIndex],
      error: ''
    })
  },

  bindCityChange(e) {
    const cityIndex = Number(e.detail.value)
    this.setData({
      cityIndex,
      selectedCity: this.data.cityOptions[cityIndex],
      error: ''
    })
  },

  switchMode(e) {
    const nextMode = e.currentTarget.dataset.mode
    if (!nextMode || nextMode === this.data.debugMode) {
      return
    }

    const nextConfig = getModeConfig(nextMode)
    this.setData({
      debugMode: nextMode,
      modeLabel: nextConfig.label,
      buttonSubtext: nextConfig.buttonSubtext,
      error: '',
      result: null
    })
  },

  convert() {
    const { amount, selectedYear, selectedCity, debugMode } = this.data
    const numericAmount = Number(amount)

    if (!amount || Number.isNaN(numericAmount) || numericAmount <= 0) {
      this.setData({
        error: '请输入大于 0 的金额'
      })
      return
    }

    this.setData({
      loading: true,
      loadingText: `正在穿越回 ${selectedYear} 年...`,
      result: null,
      error: ''
    })

    if (this.loadingTimer) {
      clearTimeout(this.loadingTimer)
    }

    this.loadingTimer = setTimeout(() => {
      this.runConversion(debugMode, numericAmount, selectedYear, selectedCity)
    }, 500)
  },

  async runConversion(modeKey, amount, year, city) {
    const modeConfig = getModeConfig(modeKey)

    try {
      const result = await modeConfig.service.convert(amount, year, city)
      this.setData({
        loading: false,
        result,
        modeLabel: modeConfig.label,
        error: ''
      })
    } catch (error) {
      this.setData({
        loading: false,
        result: null,
        modeLabel: modeConfig.label,
        error: error.message || '转换失败，请稍后重试。'
      })
    }
  },

  onUnload() {
    if (this.loadingTimer) {
      clearTimeout(this.loadingTimer)
    }
  }
})
