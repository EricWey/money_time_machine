const YEAR_OPTIONS = Array.from({ length: 46 }, (_, index) => String(2025 - index))

const CITY_OPTIONS = [
  '北京',
  '上海',
  '天津',
  '重庆',
  '石家庄',
  '太原',
  '呼和浩特',
  '沈阳',
  '长春',
  '哈尔滨',
  '南京',
  '杭州',
  '合肥',
  '福州',
  '南昌',
  '济南',
  '郑州',
  '武汉',
  '长沙',
  '广州',
  '南宁',
  '海口',
  '成都',
  '贵阳',
  '昆明',
  '拉萨',
  '西安',
  '兰州',
  '西宁',
  '银川',
  '乌鲁木齐'
]

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

module.exports = {
  YEAR_OPTIONS,
  CITY_OPTIONS,
  ITEM_CATALOG,
  formatCurrency,
  buildVintageComment,
  normalizeApiItems
}
