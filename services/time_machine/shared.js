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

const API_ITEM_METADATA = {
  梗米: {
    title: '梗米',
    unit: '元/斤',
    image: '../../images/item_rice.svg',
    note: '家庭主食的基础款，一斤米价最能照见日常饭桌的分量。'
  },
  大豆油: {
    title: '大豆油',
    unit: '元/升',
    image: '../../images/item_rice.svg',
    note: '厨房刚需消耗品，油价起伏通常会悄悄传导到每一顿家常菜。'
  },
  精瘦肉: {
    title: '精瘦肉',
    unit: '元/斤',
    image: '../../images/item_pork.svg',
    note: '家常荤菜的代表，一斤肉价最容易让人感到餐桌成本的变化。'
  },
  '棉质T恤': {
    title: '棉质T恤',
    unit: '元/件',
    image: '../../images/item_bicycle.svg',
    note: '日常穿着的基础单品，一件T恤能看出消费从耐穿到快消的变化。'
  },
  '330ml啤酒': {
    title: '330ml啤酒',
    unit: '元/瓶',
    image: '../../images/item_bicycle.svg',
    note: '最常见的轻社交饮品，一瓶价格常常对应一代人的夜生活记忆。'
  },
  '500ml五粮液': {
    title: '500ml五粮液',
    unit: '元/瓶',
    image: '../../images/item_bicycle.svg',
    note: '典型的宴请型消费品，一瓶价格往往映射出礼数与体面的时代成本。'
  },
  '月平均工资': {
    title: '月平均工资',
    unit: '元/月',
    image: '../../images/item_bicycle.svg',
    note: '这是一个时代最直接的收入刻度，最适合用来对照体感购买力。'
  },
  理发: {
    title: '理发',
    unit: '元/次',
    image: '../../images/item_bicycle.svg',
    note: '高频生活服务的代表，一次理发最能反映人工服务价格的时代位移。'
  }
}

function formatCurrency(value) {
  return Number(value).toFixed(2)
}

function buildVintageComment(amount, year, city, equivalentAmount) {
  return `${year}年的${amount}元，在${city}像一张刚发下来的工资条。如今折算成约${formatCurrency(equivalentAmount)}元，时代换了底色，柴米油盐的分量也悄悄变重了。`
}

function getItemMeta(itemName, index) {
  const apiMeta = API_ITEM_METADATA[itemName]
  if (apiMeta) {
    return apiMeta
  }

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
      unit: item.unit || meta.unit,
      image: meta.image,
      note: item.note || meta.note,
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
