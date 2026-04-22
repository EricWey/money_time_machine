const API_BASE_URL = 'http://127.0.0.1:8000'

const YEAR_OPTIONS = Array.from({ length: 46 }, (_, index) => String(2025 - index))

const CITY_OPTIONS = [
  '北京',
  '上海',
  '广州',
  '深圳',
  '杭州',
  '成都',
  '武汉',
  '西安',
  '南京',
  '重庆'
]

const MACRO_DATA = {
  1980: { cpi: 100.0, m2Adj: 11.1, property: 100 },
  1985: { cpi: 123.5, m2Adj: 11.0, property: 120 },
  1990: { cpi: 177.6, m2Adj: 16.3, property: 140 },
  1995: { cpi: 305.9, m2Adj: 18.6, property: 185 },
  2000: { cpi: 334.7, m2Adj: 3.8, property: 220 },
  2005: { cpi: 358.7, m2Adj: 6.2, property: 320 },
  2010: { cpi: 421.1, m2Adj: 9.1, property: 500 },
  2015: { cpi: 500.7, m2Adj: 6.3, property: 700 },
  2020: { cpi: 557.8, m2Adj: 7.9, property: 1000 },
  2024: { cpi: 587.2, m2Adj: 3.7, property: 990 },
  2025: { cpi: 591.9, m2Adj: 3.0, property: 980 }
}

const CITY_PRICE_LIBRARY = {
  北京: {
    1990: {
      pork: 2.5,
      rice: 0.8,
      bicycle: 180
    },
    2024: {
      pork: 25,
      rice: 6,
      bicycle: 1599
    }
  },
  上海: {
    1990: {
      pork: 2.7,
      rice: 0.9,
      bicycle: 220
    },
    2024: {
      pork: 28,
      rice: 6.5,
      bicycle: 1899
    }
  },
  广州: {
    1990: {
      pork: 2.4,
      rice: 0.85,
      bicycle: 210
    },
    2024: {
      pork: 26,
      rice: 6.2,
      bicycle: 1699
    }
  },
  深圳: {
    1990: {
      pork: 2.6,
      rice: 0.95,
      bicycle: 260
    },
    2024: {
      pork: 27,
      rice: 6.8,
      bicycle: 1999
    }
  },
  杭州: {
    1990: {
      pork: 2.3,
      rice: 0.82,
      bicycle: 200
    },
    2024: {
      pork: 25,
      rice: 6.1,
      bicycle: 1799
    }
  },
  成都: {
    1990: {
      pork: 2.2,
      rice: 0.75,
      bicycle: 175
    },
    2024: {
      pork: 24,
      rice: 5.8,
      bicycle: 1499
    }
  },
  武汉: {
    1990: {
      pork: 2.3,
      rice: 0.78,
      bicycle: 185
    },
    2024: {
      pork: 24.5,
      rice: 5.9,
      bicycle: 1559
    }
  },
  西安: {
    1990: {
      pork: 2.1,
      rice: 0.76,
      bicycle: 170
    },
    2024: {
      pork: 23.5,
      rice: 5.7,
      bicycle: 1459
    }
  },
  南京: {
    1990: {
      pork: 2.4,
      rice: 0.81,
      bicycle: 195
    },
    2024: {
      pork: 25.5,
      rice: 6.1,
      bicycle: 1669
    }
  },
  重庆: {
    1990: {
      pork: 2.0,
      rice: 0.72,
      bicycle: 168
    },
    2024: {
      pork: 23,
      rice: 5.6,
      bicycle: 1429
    }
  }
}

const ITEM_CATALOG = [
  {
    key: 'pork',
    title: '猪肉',
    unit: '元/斤',
    image: '../../images/item_pork.svg',
    note: '那时一斤猪肉，往往就是一顿小灶的底气。'
  },
  {
    key: 'rice',
    title: '大米',
    unit: '元/斤',
    image: '../../images/item_rice.svg',
    note: '一袋米撑起的是全家的烟火，也是最直接的物价记忆。'
  },
  {
    key: 'bicycle',
    title: '凤凰自行车',
    unit: '元/辆',
    image: '../../images/item_bicycle.svg',
    note: '从代步工具到家庭大件，价格背后都是时代印记。'
  }
]

function formatCurrency(value) {
  return Number(value).toFixed(2)
}

function getNearestMacroYear(year) {
  const numericYear = Number(year)
  const availableYears = Object.keys(MACRO_DATA).map(Number).sort((a, b) => a - b)
  let nearest = availableYears[0]

  availableYears.forEach((candidate) => {
    if (Math.abs(candidate - numericYear) < Math.abs(nearest - numericYear)) {
      nearest = candidate
    }
  })

  return nearest
}

function buildVintageComment(amount, year, city, equivalentAmount) {
  return `${year}年的${amount}元，在${city}像一张刚发下来的工资条。如今折算成约${formatCurrency(equivalentAmount)}元，时代换了底色，柴米油盐的分量也悄悄变重了。`
}

function getItemMeta(itemName, index) {
  const byName = ITEM_CATALOG.find((item) => item.title === itemName)
  if (byName) {
    return byName
  }

  return ITEM_CATALOG[index] || ITEM_CATALOG[0]
}

function normalizeApiItems(apiItems, year) {
  return (apiItems || []).slice(0, 3).map((item, index) => {
    const meta = getItemMeta(item.name, index)
    const oldPrice = Number(item.price_then || 0)
    const currentPrice = Number(item.price_now || 0)

    return {
      title: item.name || meta.title,
      unit: meta.unit,
      image: meta.image,
      note: meta.note,
      priceThen: formatCurrency(oldPrice),
      priceNow: formatCurrency(currentPrice),
      comparison: item.purchasing_power || `${year} 到 2024 年价格发生变化`
    }
  })
}

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
    modeLabel: '当前模式：真实接口',
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

    this.setData({
      debugMode: nextMode,
      modeLabel: nextMode === 'api' ? '当前模式：真实接口' : '当前模式：本地演示',
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
      if (debugMode === 'local') {
        const result = this.calculateLocalResult(numericAmount, selectedYear, selectedCity)
        this.setData({
          loading: false,
          result,
          modeLabel: '当前模式：本地演示'
        })
        return
      }

      this.fetchRealResult(numericAmount, selectedYear, selectedCity)
    }, 500)
  },

  fetchRealResult(amount, year, city) {
    wx.request({
      url: `${API_BASE_URL}/api/v1/convert`,
      method: 'POST',
      timeout: 8000,
      data: {
        amount,
        source_year: Number(year),
        city
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data) {
          const result = this.buildResultFromApi(amount, year, city, res.data)
          this.setData({
            loading: false,
            result,
            modeLabel: '当前模式：真实接口'
          })
          return
        }

        const fallbackResult = this.calculateLocalResult(amount, year, city)
        this.setData({
          loading: false,
          result: fallbackResult,
          modeLabel: '当前模式：真实接口（已回退本地演示）',
          error: '真实接口暂不可用，已切换为本地演示结果'
        })
      },
      fail: () => {
        const fallbackResult = this.calculateLocalResult(amount, year, city)
        this.setData({
          loading: false,
          result: fallbackResult,
          modeLabel: '当前模式：真实接口（已回退本地演示）',
          error: '无法连接本地接口，已切换为本地演示结果'
        })
      }
    })
  },

  buildResultFromApi(amount, year, city, apiData) {
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
  },

  calculateLocalResult(amount, year, city) {
    // 用轻量本地模型完成首页演示，保证前端离线也能出效果。
    const sourceMacroYear = getNearestMacroYear(year)
    const sourceMacro = MACRO_DATA[sourceMacroYear]
    const targetMacro = MACRO_DATA[2024]

    const cpiRatio = targetMacro.cpi / sourceMacro.cpi
    const m2Ratio = (1 + targetMacro.m2Adj / 100) / (1 + sourceMacro.m2Adj / 100)
    const propertyRatio = targetMacro.property / sourceMacro.property
    const equivalentAmount = amount * (0.4 * cpiRatio + 0.4 * m2Ratio + 0.2 * propertyRatio)

    const cityPriceData = CITY_PRICE_LIBRARY[city] || CITY_PRICE_LIBRARY.北京
    const sourcePriceYear = cityPriceData[year] ? Number(year) : 1990
    const sourceItems = cityPriceData[sourcePriceYear] || cityPriceData[1990]
    const currentItems = cityPriceData[2024]

    const items = ITEM_CATALOG.map((item) => {
      const oldPrice = sourceItems[item.key]
      const currentPrice = currentItems[item.key]
      const ratio = currentPrice / oldPrice

      return {
        title: item.title,
        unit: item.unit,
        image: item.image,
        note: item.note,
        priceThen: formatCurrency(oldPrice),
        priceNow: formatCurrency(currentPrice),
        comparison: `如今约是当年的 ${ratio.toFixed(1)} 倍`
      }
    })

    return {
      year,
      city,
      sourceAmount: formatCurrency(amount),
      equivalentAmount: formatCurrency(equivalentAmount),
      deltaAmount: formatCurrency(equivalentAmount - amount),
      aiComment: buildVintageComment(amount, year, city, equivalentAmount),
      items
    }
  },

  onUnload() {
    if (this.loadingTimer) {
      clearTimeout(this.loadingTimer)
    }
  }
})
