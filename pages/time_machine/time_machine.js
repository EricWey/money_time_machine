const { YEAR_OPTIONS, CITY_OPTIONS } = require('../../services/time_machine/shared')
const { convert } = require('../../services/time_machine/api')

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
    modeLabel: '当年你爸妈挣得可不少哦',
    buttonSubtext: '带你回到那个年代',
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

  convert() {
    const { amount, selectedYear, selectedCity } = this.data
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
      this.runConversion(numericAmount, selectedYear, selectedCity)
    }, 500)
  },

  async runConversion(amount, year, city) {
    try {
      const result = await convert(amount, year, city)
      this.setData({
        loading: false,
        result,
        error: ''
      })
    } catch (error) {
      this.setData({
        loading: false,
        result: null,
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
