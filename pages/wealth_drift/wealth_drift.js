const { requestDrift, requestConvert } = require('../../utils/api')
const { getCache, setCache } = require('../../utils/cache')
const { createPoster } = require('../../utils/poster')

const COMMENT_SOURCE_YEAR = 2024
const DRIFT_CACHE_TTL = 30 * 60 * 1000
const COMMENT_CACHE_TTL = 12 * 60 * 60 * 1000

const CITY_LIBRARY = [
  {
    name: '北京',
    keywords: ['beijing', '帝都', '京'],
    coli: 98,
    medianIncome: 7500,
    level: 'super',
    vibe: '北漂',
    metrics: { housing: 7200, dining: 1700, traffic: 520, entertainment: 1500 }
  },
  {
    name: '上海',
    keywords: ['shanghai', '魔都', '沪'],
    coli: 100,
    medianIncome: 7800,
    level: 'super',
    vibe: '沪漂',
    metrics: { housing: 7600, dining: 1800, traffic: 480, entertainment: 1650 }
  },
  {
    name: '深圳',
    keywords: ['shenzhen', '深', '鹏城'],
    coli: 95,
    medianIncome: 7200,
    level: 'super',
    vibe: '搞钱人',
    metrics: { housing: 6900, dining: 1650, traffic: 430, entertainment: 1520 }
  },
  {
    name: '广州',
    keywords: ['guangzhou', '广', '羊城'],
    coli: 92,
    medianIncome: 6900,
    level: 'super',
    vibe: '老广',
    metrics: { housing: 6200, dining: 1550, traffic: 400, entertainment: 1420 }
  },
  {
    name: '杭州',
    keywords: ['hangzhou', '杭', '互联网'],
    coli: 88,
    medianIncome: 6800,
    level: 'new-first',
    vibe: '大厂候选人',
    metrics: { housing: 5800, dining: 1450, traffic: 360, entertainment: 1360 }
  },
  {
    name: '南京',
    keywords: ['nanjing', '宁', '金陵'],
    coli: 84,
    medianIncome: 6200,
    level: 'new-first',
    vibe: '六朝打工人',
    metrics: { housing: 5000, dining: 1320, traffic: 320, entertainment: 1180 }
  },
  {
    name: '成都',
    keywords: ['chengdu', '蓉', '巴适'],
    coli: 72,
    medianIncome: 4700,
    level: 'strong-second',
    vibe: '松弛派',
    metrics: { housing: 3600, dining: 980, traffic: 260, entertainment: 980 }
  },
  {
    name: '武汉',
    keywords: ['wuhan', '汉', '热干面'],
    coli: 74,
    medianIncome: 4800,
    level: 'strong-second',
    vibe: '过早玩家',
    metrics: { housing: 3700, dining: 1020, traffic: 270, entertainment: 930 }
  },
  {
    name: '西安',
    keywords: ['xian', '西安', '长安'],
    coli: 70,
    medianIncome: 4300,
    level: 'strong-second',
    vibe: '碳水王者',
    metrics: { housing: 3400, dining: 960, traffic: 240, entertainment: 880 }
  },
  {
    name: '重庆',
    keywords: ['chongqing', '渝', '山城'],
    coli: 68,
    medianIncome: 4200,
    level: 'strong-second',
    vibe: '火锅狠人',
    metrics: { housing: 3200, dining: 930, traffic: 250, entertainment: 910 }
  },
  {
    name: '郑州',
    keywords: ['zhengzhou', '郑', '中原'],
    coli: 65,
    medianIncome: 3500,
    level: 'second',
    vibe: '中原实干派',
    metrics: { housing: 2800, dining: 860, traffic: 210, entertainment: 760 }
  },
  {
    name: '开封',
    keywords: ['kaifeng', '汴梁', '开'],
    coli: 52,
    medianIncome: 2800,
    level: 'second',
    vibe: '小城慢活家',
    metrics: { housing: 1900, dining: 620, traffic: 120, entertainment: 520 }
  },
  {
    name: '鹤岗',
    keywords: ['hegang', '鹤'],
    coli: 30,
    medianIncome: 1800,
    level: 'small',
    vibe: '低压生存派',
    metrics: { housing: 900, dining: 430, traffic: 80, entertainment: 310 }
  },
  {
    name: '长沙',
    keywords: ['changsha', '湘', '夜宵'],
    coli: 69,
    medianIncome: 4300,
    level: 'strong-second',
    vibe: '夜生活选手',
    metrics: { housing: 3300, dining: 950, traffic: 230, entertainment: 900 }
  },
  {
    name: '苏州',
    keywords: ['suzhou', '苏', '园林'],
    coli: 86,
    medianIncome: 6500,
    level: 'new-first',
    vibe: '精致勤奋派',
    metrics: { housing: 5400, dining: 1380, traffic: 310, entertainment: 1160 }
  },
  {
    name: '青岛',
    keywords: ['qingdao', '青', '海风'],
    coli: 73,
    medianIncome: 4700,
    level: 'strong-second',
    vibe: '海边微醺派',
    metrics: { housing: 3500, dining: 1010, traffic: 240, entertainment: 950 }
  }
]

const CITY_MAP = CITY_LIBRARY.reduce((result, city) => {
  result[city.name] = city
  return result
}, {})

function formatCurrency(value) {
  const numericValue = Number(value) || 0
  return numericValue.toLocaleString('zh-CN', {
    minimumFractionDigits: numericValue % 1 === 0 ? 0 : 1,
    maximumFractionDigits: 1
  })
}

const INCOME_PRESETS = [5000, 8000, 12000, 18000, 26000].map((value) => ({
  value: String(value),
  label: formatCurrency(value)
}))

const COST_DIMENSIONS = [
  { key: 'housing', label: '住房', unit: '元/月', icon: '住' },
  { key: 'dining', label: '餐饮', unit: '元/月', icon: '吃' },
  { key: 'traffic', label: '交通', unit: '元/月', icon: '行' },
  { key: 'entertainment', label: '娱乐', unit: '元/月', icon: '玩' }
]

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

function getSearchResults(keyword, excludeCity) {
  const normalizedKeyword = (keyword || '').trim().toLowerCase()

  return CITY_LIBRARY.filter((city) => {
    if (excludeCity && city.name === excludeCity) {
      return false
    }

    if (!normalizedKeyword) {
      return true
    }

    const targets = [city.name].concat(city.keywords || [])
    return targets.some((target) => String(target).toLowerCase().indexOf(normalizedKeyword) !== -1)
  })
}

function getHeroHint(currentCity, targetCity) {
  if (!currentCity || !targetCity) {
    return '同一份工资，漂到别处，体面程度可能直接换皮。'
  }

  return `${currentCity}的工资条，漂到${targetCity}，可能直接改写朋友圈话术。`
}

function buildFallbackIdentityLabel(currentCity, targetCity, income, equivalentAmount, wealthRatio) {
  if (currentCity.level === 'super' && targetCity.level === 'small' && equivalentAmount >= 15000) {
    return '县城土豪'
  }

  if (targetCity.level === 'super' && wealthRatio < 0.7) {
    return 'CBD气氛组'
  }

  if (wealthRatio >= 3) {
    return `${targetCity.vibe}现金王`
  }

  if (wealthRatio >= 2) {
    return `${targetCity.vibe}体面名流`
  }

  if (wealthRatio >= 1.2 && income >= 10000) {
    return '奶茶自由体'
  }

  if (wealthRatio >= 0.9) {
    return '平替生活家'
  }

  if (wealthRatio >= 0.65) {
    return '合租哲学家'
  }

  return '通勤生存挑战'
}

function buildSummary(currentCity, targetCity, income, equivalentAmount, wealthRatio) {
  const ratioText = `${wealthRatio.toFixed(2)}x`

  if (wealthRatio >= 2.5) {
    return `在${targetCity.name}，你这份${formatCurrency(income)}元月薪的体感约等于${formatCurrency(equivalentAmount)}元，已经不是省着花，是花完还有空点评物价。`
  }

  if (wealthRatio >= 1) {
    return `漂到${targetCity.name}后，你的购买力约为当地月收入中位数的${ratioText}，日子不算奢华，但已经能把“随便点”说得更真诚一点。`
  }

  return `从${currentCity.name}漂到${targetCity.name}后，购买力只剩当地体面线的${ratioText}，生活不会立刻塌，但每次付款前都会更爱思考人生。`
}

function buildInsight(currentCity, targetCity, equivalentAmount) {
  const housingGap = currentCity.metrics.housing - targetCity.metrics.housing

  if (housingGap > 2500) {
    return `${currentCity.name}里压着你情绪的房租，到了${targetCity.name}大概率会变成你的周末预算。`
  }

  if (housingGap < -1200) {
    return `${targetCity.name}的房租会先给你上一课：工资也会漂流，但押一付三通常不会心软。`
  }

  if (equivalentAmount >= targetCity.medianIncome * 1.2) {
    return `你在${targetCity.name}的状态，大概属于“工资不一定能炫耀，但拒绝拼单时已经没那么心虚”。`
  }

  return `${targetCity.name}对你来说不是降维打击，也不是轻松开挂，更像一场把预算表重新排版的人生小重构。`
}

function buildDimensionComment(key, ratio, currentCityName, targetCityName) {
  if (ratio > 1.35) {
    if (key === 'housing') {
      return `${currentCityName}的房租像在交情绪税，换到${targetCityName}终于像在租房。`
    }

    if (key === 'dining') {
      return `${currentCityName}一顿外卖的钱，到了${targetCityName}能多加一道不心疼的配菜。`
    }

    if (key === 'traffic') {
      return `通勤在${targetCityName}更温柔，至少刷码那一下没那么刺痛。`
    }

    return `${targetCityName}的娱乐预算没那么冒犯，你终于可以把“出去玩”从待办改成行动。`
  }

  if (ratio < 0.8) {
    if (key === 'housing') {
      return `${targetCityName}的房租提醒你，梦想和卧室面积通常不同时上涨。`
    }

    if (key === 'dining') {
      return `${targetCityName}吃饭不算离谱，但“随便点”最好还是建立在工资到账之后。`
    }

    if (key === 'traffic') {
      return `${targetCityName}的出行成本不至于破防，只是会让你更珍惜步行。`
    }

    return `${targetCityName}的消遣要挑着来，不然快乐值会先于余额归零。`
  }

  return `${currentCityName}和${targetCityName}在这项开销上差距不算夸张，真正刺痛你的可能是频率。`
}

function buildComparisonItems(currentCity, targetCity) {
  return COST_DIMENSIONS.map((dimension) => {
    const currentValue = currentCity.metrics[dimension.key]
    const targetValue = targetCity.metrics[dimension.key]
    const ratio = targetValue > 0 ? currentValue / targetValue : 1
    const maxValue = Math.max(currentValue, targetValue)

    return {
      key: dimension.key,
      label: dimension.label,
      unit: dimension.unit,
      icon: dimension.icon,
      currentValue: formatCurrency(currentValue),
      targetValue: formatCurrency(targetValue),
      currentWidth: `${clamp((currentValue / maxValue) * 100, 24, 100)}%`,
      targetWidth: `${clamp((targetValue / maxValue) * 100, 24, 100)}%`,
      ratioText: ratio >= 1
        ? `${currentCity.name}贵 ${Math.max(0, Math.round((ratio - 1) * 100))}%`
        : `${targetCity.name}贵 ${Math.max(0, Math.round(((1 / ratio) - 1) * 100))}%`,
      roast: buildDimensionComment(dimension.key, ratio, currentCity.name, targetCity.name)
    }
  })
}

function formatAiComment(comment) {
  const normalized = (comment || '').replace(/\r\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim()
  return normalized || '专家暂时没开口，但从数字看，这次漂流已经把你的生活体感改写了。'
}

function createDisplayResult(currentCityName, targetCityName, incomeValue, driftResponse) {
  const currentCity = CITY_MAP[currentCityName]
  const targetCity = CITY_MAP[targetCityName]
  const income = Number(incomeValue)
  const equivalentAmount = Number(driftResponse.equivalent_amount || income * currentCity.coli / targetCity.coli)
  const wealthRatio = Number(driftResponse.wealth_ratio || 0)
  const identityLabel = driftResponse.identity_label || buildFallbackIdentityLabel(currentCity, targetCity, income, equivalentAmount, wealthRatio)
  const totalCurrentCost = Object.values(currentCity.metrics).reduce((sum, value) => sum + value, 0)
  const totalTargetCost = Object.values(targetCity.metrics).reduce((sum, value) => sum + value, 0)
  const savingsDelta = equivalentAmount - totalTargetCost

  return {
    currentCity,
    targetCity,
    equivalentAmount: formatCurrency(equivalentAmount),
    wealthRatio: wealthRatio.toFixed(2),
    identityLabel,
    costComparison: buildComparisonItems(currentCity, targetCity),
    summary: buildSummary(currentCity, targetCity, income, equivalentAmount, wealthRatio),
    insight: driftResponse.city_comparison || buildInsight(currentCity, targetCity, equivalentAmount),
    totalCurrentCost: formatCurrency(totalCurrentCost),
    totalTargetCost: formatCurrency(totalTargetCost),
    targetMedianIncome: formatCurrency(driftResponse.target_city_median_income || targetCity.medianIncome),
    monthlyBalance: formatCurrency(savingsDelta),
    moodTag: savingsDelta >= 1500 ? '月底有余粮' : savingsDelta >= 0 ? '还能稳住' : '请重新做表',
    roastLine: savingsDelta >= 1500
      ? `在${targetCity.name}，你每月大约还能剩下 ${formatCurrency(savingsDelta)} 元，已经摸到“周末能说走就走”那一层。`
      : savingsDelta >= 0
        ? `在${targetCity.name}，你还能勉强守住收支平衡，只是每次点“加料”都得先快速心算。`
        : `在${targetCity.name}，按这套开销模型你每月会倒挂 ${formatCurrency(Math.abs(savingsDelta))} 元，诗和远方还没来，账单先来了。`
  }
}

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

  buildPayloads() {
    return {
      driftPayload: {
        current_city: this.data.currentCity,
        monthly_income: Number(this.data.monthlyIncome),
        target_city: this.data.targetCity
      },
      commentPayload: {
        amount: Number(this.data.monthlyIncome),
        source_year: COMMENT_SOURCE_YEAR,
        city: this.data.currentCity
      }
    }
  },

  async startDrift() {
    const validationError = this.validateForm()
    if (validationError) {
      this.setData({
        error: validationError
      })
      return
    }

    const { driftPayload, commentPayload } = this.buildPayloads()
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
      const driftResult = await this.fetchDriftResult(driftPayload)

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

  async fetchDriftResult(payload) {
    const cached = getCache('drift', payload, DRIFT_CACHE_TTL)
    if (cached) {
      return cached
    }

    const response = await requestDrift(payload)
    setCache('drift', payload, response)
    return response
  },

  async fetchExpertComment(payload, runId) {
    this.setData({
      loadingComment: true,
      commentError: null,
      lastRetryAction: buildRetryState('comment', payload)
    })

    try {
      const cached = getCache('comment', payload, COMMENT_CACHE_TTL)
      const response = cached || await requestConvert(payload)

      if (this.activeRunId !== runId) {
        return
      }

      if (!cached) {
        setCache('comment', payload, response)
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
