const { ITEM_CATALOG, formatCurrency, buildVintageComment } = require('./shared')

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
    1990: { pork: 2.5, rice: 0.8, bicycle: 180 },
    2024: { pork: 25, rice: 6, bicycle: 1599 }
  },
  上海: {
    1990: { pork: 2.7, rice: 0.9, bicycle: 220 },
    2024: { pork: 28, rice: 6.5, bicycle: 1899 }
  },
  广州: {
    1990: { pork: 2.4, rice: 0.85, bicycle: 210 },
    2024: { pork: 26, rice: 6.2, bicycle: 1699 }
  },
  深圳: {
    1990: { pork: 2.6, rice: 0.95, bicycle: 260 },
    2024: { pork: 27, rice: 6.8, bicycle: 1999 }
  },
  杭州: {
    1990: { pork: 2.3, rice: 0.82, bicycle: 200 },
    2024: { pork: 25, rice: 6.1, bicycle: 1799 }
  },
  成都: {
    1990: { pork: 2.2, rice: 0.75, bicycle: 175 },
    2024: { pork: 24, rice: 5.8, bicycle: 1499 }
  },
  武汉: {
    1990: { pork: 2.3, rice: 0.78, bicycle: 185 },
    2024: { pork: 24.5, rice: 5.9, bicycle: 1559 }
  },
  西安: {
    1990: { pork: 2.1, rice: 0.76, bicycle: 170 },
    2024: { pork: 23.5, rice: 5.7, bicycle: 1459 }
  },
  南京: {
    1990: { pork: 2.4, rice: 0.81, bicycle: 195 },
    2024: { pork: 25.5, rice: 6.1, bicycle: 1669 }
  },
  重庆: {
    1990: { pork: 2.0, rice: 0.72, bicycle: 168 },
    2024: { pork: 23, rice: 5.6, bicycle: 1429 }
  }
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

function convert(amount, year, city) {
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

  return Promise.resolve({
    year,
    city,
    sourceAmount: formatCurrency(amount),
    equivalentAmount: formatCurrency(equivalentAmount),
    deltaAmount: formatCurrency(equivalentAmount - amount),
    aiComment: buildVintageComment(amount, year, city, equivalentAmount),
    items
  })
}

module.exports = {
  convert
}
