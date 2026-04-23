function roundToNearest(value, base) {
  return Math.round(value / base) * base
}

function buildMetrics(level, medianIncome, coli) {
  const housingShareMap = {
    super: 0.95,
    'new-first': 0.84,
    'strong-second': 0.76,
    second: 0.68
  }
  const housing = roundToNearest(medianIncome * (housingShareMap[level] || 0.7), 50)
  const dining = roundToNearest(520 + coli * 11.5, 10)
  const traffic = roundToNearest(70 + coli * 3.4, 10)
  const entertainment = roundToNearest(260 + coli * 7.8, 10)

  return { housing, dining, traffic, entertainment }
}

function createCity({ name, keywords, coli, medianIncome, level, vibe, metrics }) {
  return {
    name,
    keywords,
    coli,
    medianIncome,
    level,
    vibe,
    metrics: metrics || buildMetrics(level, medianIncome, coli)
  }
}

const CITY_LIBRARY = [
  createCity({ name: '北京', keywords: ['beijing', '帝都', '京'], coli: 98, medianIncome: 7800, level: 'super', vibe: '北漂' }),
  createCity({ name: '上海', keywords: ['shanghai', '魔都', '沪'], coli: 100, medianIncome: 8100, level: 'super', vibe: '沪漂' }),
  createCity({ name: '天津', keywords: ['tianjin', '津'], coli: 79, medianIncome: 5600, level: 'new-first', vibe: '津门生活家' }),
  createCity({ name: '重庆', keywords: ['chongqing', '渝', '山城'], coli: 72, medianIncome: 4600, level: 'strong-second', vibe: '火锅狠人' }),
  createCity({ name: '石家庄', keywords: ['shijiazhuang', '石家庄', '冀'], coli: 63, medianIncome: 4200, level: 'second', vibe: '冀中实干派' }),
  createCity({ name: '太原', keywords: ['taiyuan', '并州', '晋'], coli: 64, medianIncome: 4300, level: 'second', vibe: '并州稳派' }),
  createCity({ name: '呼和浩特', keywords: ['huhehaote', '呼市', '青城'], coli: 62, medianIncome: 4100, level: 'second', vibe: '草原通勤人' }),
  createCity({ name: '沈阳', keywords: ['shenyang', '盛京', '沈'], coli: 68, medianIncome: 4700, level: 'strong-second', vibe: '东北爽快派' }),
  createCity({ name: '长春', keywords: ['changchun', '春城', '吉'], coli: 63, medianIncome: 4200, level: 'second', vibe: '北国稳班人' }),
  createCity({ name: '哈尔滨', keywords: ['haerbin', 'harbin', '冰城'], coli: 65, medianIncome: 4300, level: 'second', vibe: '冰城生活派' }),
  createCity({ name: '南京', keywords: ['nanjing', '宁', '金陵'], coli: 84, medianIncome: 6500, level: 'new-first', vibe: '六朝打工人' }),
  createCity({ name: '杭州', keywords: ['hangzhou', '杭', '互联网'], coli: 88, medianIncome: 7100, level: 'new-first', vibe: '大厂候选人' }),
  createCity({ name: '合肥', keywords: ['hefei', '庐州', '合'], coli: 66, medianIncome: 4600, level: 'strong-second', vibe: '科创打拼人' }),
  createCity({ name: '福州', keywords: ['fuzhou', '榕城', '榕'], coli: 69, medianIncome: 4700, level: 'strong-second', vibe: '榕城慢锋派' }),
  createCity({ name: '南昌', keywords: ['nanchang', '洪城', '赣'], coli: 64, medianIncome: 4300, level: 'second', vibe: '洪城实在人' }),
  createCity({ name: '济南', keywords: ['jinan', '泉城', '鲁'], coli: 67, medianIncome: 4600, level: 'strong-second', vibe: '泉城进取派' }),
  createCity({ name: '郑州', keywords: ['zhengzhou', '郑', '中原'], coli: 65, medianIncome: 4400, level: 'strong-second', vibe: '中原实干派' }),
  createCity({ name: '武汉', keywords: ['wuhan', '汉', '热干面'], coli: 74, medianIncome: 5000, level: 'strong-second', vibe: '过早玩家' }),
  createCity({ name: '长沙', keywords: ['changsha', '湘', '夜宵'], coli: 69, medianIncome: 4700, level: 'strong-second', vibe: '夜生活选手' }),
  createCity({ name: '广州', keywords: ['guangzhou', '广', '羊城'], coli: 92, medianIncome: 7300, level: 'super', vibe: '老广' }),
  createCity({ name: '南宁', keywords: ['nanning', '邕城', '邕'], coli: 60, medianIncome: 4000, level: 'second', vibe: '邕城悠然派' }),
  createCity({ name: '海口', keywords: ['haikou', '椰城', '琼'], coli: 66, medianIncome: 4200, level: 'second', vibe: '海风慢活家' }),
  createCity({ name: '成都', keywords: ['chengdu', '蓉', '巴适'], coli: 72, medianIncome: 4900, level: 'strong-second', vibe: '松弛派' }),
  createCity({ name: '贵阳', keywords: ['guiyang', '筑城', '黔'], coli: 58, medianIncome: 3900, level: 'second', vibe: '山城节奏派' }),
  createCity({ name: '昆明', keywords: ['kunming', '春城', '滇'], coli: 61, medianIncome: 4100, level: 'second', vibe: '春城呼吸派' }),
  createCity({ name: '拉萨', keywords: ['lasa', '拉萨', '藏'], coli: 67, medianIncome: 4400, level: 'second', vibe: '高原慢行者' }),
  createCity({ name: '西安', keywords: ['xian', '西安', '长安'], coli: 70, medianIncome: 4600, level: 'strong-second', vibe: '碳水王者' }),
  createCity({ name: '兰州', keywords: ['lanzhou', '金城', '甘'], coli: 60, medianIncome: 4000, level: 'second', vibe: '兰州拉面派' }),
  createCity({ name: '西宁', keywords: ['xining', '夏都', '青'], coli: 59, medianIncome: 3900, level: 'second', vibe: '高原稳住派' }),
  createCity({ name: '银川', keywords: ['yinchuan', '凤城', '宁夏'], coli: 58, medianIncome: 3900, level: 'second', vibe: '塞上松弛派' }),
  createCity({ name: '乌鲁木齐', keywords: ['wulumuqi', 'urumqi', '乌市'], coli: 65, medianIncome: 4300, level: 'second', vibe: '边城硬核派' })
]

const CITY_MAP = CITY_LIBRARY.reduce((result, city) => {
  result[city.name] = city
  return result
}, {})

const COST_DIMENSIONS = [
  { key: 'housing', label: '住房', unit: '元/月', icon: '住' },
  { key: 'dining', label: '餐饮', unit: '元/月', icon: '吃' },
  { key: 'traffic', label: '交通', unit: '元/月', icon: '行' },
  { key: 'entertainment', label: '娱乐', unit: '元/月', icon: '玩' }
]

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

module.exports = {
  CITY_MAP,
  INCOME_PRESETS,
  getSearchResults,
  getHeroHint,
  createDisplayResult,
  formatAiComment
}
