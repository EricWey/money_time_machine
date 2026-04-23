const { createPoster } = require('../../utils/poster')
const {
  CITY_MAP,
  INCOME_PRESETS,
  getSearchResults,
  getHeroHint,
  createDisplayResult,
  formatAiComment
} = require('../../services/wealth_drift/local')
const {
  buildPayloads,
  fetchDriftResult,
  fetchExpertComment
} = require('../../services/wealth_drift/real')

function buildRetryState(type, payload) {
  return {
    type,
    payload
  }
}

Page({
  data: {
    currentCity: '上海',
    targetCity: '成都',
    currentCitySearch: '上海',
    targetCitySearch: '成都',
    monthlyIncome: '',
    activePicker: 'none',
    filteredCurrentCities: getSearchResults('上海', '成都'),
    filteredTargetCities: getSearchResults('成都', '上海'),
    incomePresets: INCOME_PRESETS,
    pageStage: 'form',
    transitioning: false,
    loadingText: '',
    heroHint: getHeroHint('上海', '成都'),
    result: null,
    stampVisible: false,
    error: '',
    driftError: null,
    commentError: null,
    loadingDrift: false,
    loadingComment: false,
    expertComment: '',
    lastRetryAction: null,
    posterGenerating: false,
    posterVisible: false,
    posterTempFilePath: '',
    posterError: '',
    shareHint: ''
  },

  onLoad() {
    this.activeRunId = 0
  },

  bindCitySearch(e) {
    const role = e.currentTarget.dataset.role
    const value = e.detail.value
    const update = {
      error: '',
      driftError: null
    }

    if (role === 'current') {
      update.currentCitySearch = value
      update.activePicker = 'current'
      update.filteredCurrentCities = getSearchResults(value, this.data.targetCity)
    } else {
      update.targetCitySearch = value
      update.activePicker = 'target'
      update.filteredTargetCities = getSearchResults(value, this.data.currentCity)
    }

    this.setData(update)
  },

  focusCitySearch(e) {
    const role = e.currentTarget.dataset.role

    if (role === 'current') {
      this.setData({
        activePicker: 'current',
        filteredCurrentCities: getSearchResults(this.data.currentCitySearch, this.data.targetCity)
      })
      return
    }

    this.setData({
      activePicker: 'target',
      filteredTargetCities: getSearchResults(this.data.targetCitySearch, this.data.currentCity)
    })
  },

  selectCity(e) {
    const role = e.currentTarget.dataset.role
    const city = e.currentTarget.dataset.city

    if (role === 'current') {
      this.setData({
        currentCity: city,
        currentCitySearch: city,
        activePicker: 'none',
        heroHint: getHeroHint(city, this.data.targetCity),
        filteredTargetCities: getSearchResults(this.data.targetCitySearch, city),
        error: '',
        driftError: null
      })
      return
    }

    this.setData({
      targetCity: city,
      targetCitySearch: city,
      activePicker: 'none',
      heroHint: getHeroHint(this.data.currentCity, city),
      filteredCurrentCities: getSearchResults(this.data.currentCitySearch, city),
      error: '',
      driftError: null
    })
  },

  closePicker() {
    this.setData({
      activePicker: 'none'
    })
  },

  noop() {},

  bindIncomeInput(e) {
    this.setData({
      monthlyIncome: e.detail.value.replace(/[^\d]/g, ''),
      error: '',
      driftError: null
    })
  },

  chooseIncomePreset(e) {
    const value = String(e.currentTarget.dataset.value)
    this.setData({
      monthlyIncome: value,
      error: '',
      driftError: null
    })
  },

  resetForm() {
    this.activeRunId += 1
    this.setData({
      pageStage: 'form',
      transitioning: false,
      stampVisible: false,
      activePicker: 'none',
      loadingDrift: false,
      loadingComment: false,
      driftError: null,
      commentError: null,
      lastRetryAction: null,
      posterGenerating: false,
      posterVisible: false,
      posterTempFilePath: '',
      posterError: '',
      shareHint: ''
    })
  },

  validateForm() {
    const income = Number(this.data.monthlyIncome)

    if (!this.data.currentCity || !this.data.targetCity || !this.data.monthlyIncome) {
      return '先把城市和月收入补齐，漂流瓶才知道往哪儿冲。'
    }

    if (!CITY_MAP[this.data.currentCity] || !CITY_MAP[this.data.targetCity]) {
      return '城市不在样本库里，先从列表里挑一个，别让算法瞎漂。'
    }

    if (this.data.currentCity === this.data.targetCity) {
      return '起点和终点是同一座城的话，这趟漂流只会得到“原地打工”。'
    }

    if (!income || income <= 0) {
      return '月收入得是大于 0 的数字，不然财富轨迹无法起飞。'
    }

    return ''
  },

  async startDrift() {
    const validationError = this.validateForm()
    if (validationError) {
      this.setData({
        error: validationError
      })
      return
    }

    const { driftPayload, commentPayload } = buildPayloads(
      this.data.currentCity,
      this.data.targetCity,
      this.data.monthlyIncome
    )
    const runId = Date.now()
    this.activeRunId = runId

    this.setData({
      transitioning: true,
      loadingDrift: true,
      loadingComment: true,
      loadingText: `正在把 ${this.data.currentCity} 的工资条漂向 ${this.data.targetCity}`,
      error: '',
      driftError: null,
      commentError: null,
      expertComment: '',
      activePicker: 'none',
      lastRetryAction: buildRetryState('drift', driftPayload)
    })

    try {
      const driftResult = await fetchDriftResult(driftPayload)

      if (this.activeRunId !== runId) {
        return
      }

      this.setData({
        result: createDisplayResult(this.data.currentCity, this.data.targetCity, this.data.monthlyIncome, driftResult),
        pageStage: 'result',
        transitioning: false,
        loadingDrift: false
      })

      setTimeout(() => {
        if (this.activeRunId !== runId) {
          return
        }
        this.setData({
          stampVisible: true
        })
      }, 80)

      this.fetchExpertComment(commentPayload, runId)
    } catch (error) {
      if (this.activeRunId !== runId) {
        return
      }

      this.setData({
        transitioning: false,
        loadingDrift: false,
        loadingComment: false,
        driftError: error,
        error: error.message,
        lastRetryAction: error.recoverable ? buildRetryState('drift', driftPayload) : null
      })
    }
  },

  async fetchExpertComment(payload, runId) {
    this.setData({
      loadingComment: true,
      commentError: null,
      lastRetryAction: buildRetryState('comment', payload)
    })

    try {
      const response = await fetchExpertComment(payload)

      if (this.activeRunId !== runId) {
        return
      }

      this.setData({
        expertComment: formatAiComment(response.ai_comment),
        loadingComment: false,
        commentError: null,
        lastRetryAction: null
      })
    } catch (error) {
      if (this.activeRunId !== runId) {
        return
      }

      this.setData({
        loadingComment: false,
        commentError: error,
        lastRetryAction: error.recoverable ? buildRetryState('comment', payload) : null
      })
    }
  },

  retryLastRequest() {
    const retryState = this.data.lastRetryAction
    if (!retryState) {
      return
    }

    if (retryState.type === 'drift') {
      this.startDrift()
      return
    }

    if (retryState.type === 'comment') {
      this.fetchExpertComment(retryState.payload, this.activeRunId)
    }
  },

  buildPosterPayload() {
    const { result, expertComment } = this.data

    return {
      route: `${result.currentCity.name} → ${result.targetCity.name}`,
      equivalentAmount: result.equivalentAmount,
      wealthRatio: result.wealthRatio,
      identityLabel: result.identityLabel,
      moodTag: result.moodTag,
      summary: result.summary,
      expertComment: formatAiComment(expertComment || '专家暂时沉默，但数字已经说明一切。')
    }
  },

  async generatePoster() {
    if (!this.data.result) {
      return
    }

    this.setData({
      posterGenerating: true,
      posterError: '',
      shareHint: ''
    })

    wx.showLoading({
      title: '海报生成中',
      mask: true
    })

    try {
      const tempFilePath = await createPoster('posterCanvas', this.buildPosterPayload(), this)
      this.setData({
        posterGenerating: false,
        posterVisible: true,
        posterTempFilePath: tempFilePath,
        posterError: ''
      })
    } catch (error) {
      this.setData({
        posterGenerating: false,
        posterVisible: true,
        posterError: error.message || '海报生成失败，请稍后重试。',
        posterTempFilePath: ''
      })
    } finally {
      wx.hideLoading()
    }
  },

  closePosterPanel() {
    this.setData({
      posterVisible: false,
      posterError: '',
      shareHint: ''
    })
  },

  async savePosterToAlbum() {
    if (!this.data.posterTempFilePath) {
      return
    }

    try {
      await new Promise((resolve, reject) => {
        wx.saveImageToPhotosAlbum({
          filePath: this.data.posterTempFilePath,
          success: resolve,
          fail: reject
        })
      })

      wx.showToast({
        title: '已保存到相册',
        icon: 'success'
      })
    } catch (error) {
      if (error.errMsg && error.errMsg.indexOf('auth deny') !== -1) {
        wx.showModal({
          title: '需要相册权限',
          content: '请在设置中允许保存到相册，然后再试一次。',
          confirmText: '去设置',
          success: (res) => {
            if (res.confirm) {
              wx.openSetting()
            }
          }
        })
        return
      }

      wx.showToast({
        title: '保存失败',
        icon: 'none'
      })
    }
  },

  sharePosterImage() {
    if (!this.data.posterTempFilePath) {
      return
    }

    if (wx.showShareImageMenu) {
      wx.showShareImageMenu({
        path: this.data.posterTempFilePath
      })
      return
    }

    this.setData({
      shareHint: '当前基础库不支持直接图片分享，已为你打开预览，可长按图片转发。'
    })

    wx.previewImage({
      urls: [this.data.posterTempFilePath],
      current: this.data.posterTempFilePath
    })
  },

  onShareAppMessage() {
    return {
      title: this.data.result
        ? `${this.data.result.identityLabel}：我的财富人生漂流结果`
        : '来测测你的财富漂流人生',
      path: '/pages/wealth_drift/wealth_drift',
      imageUrl: this.data.posterTempFilePath || ''
    }
  }
})
