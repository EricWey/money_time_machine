// test-normalize.js
const { normalizeApiItems, getItemMeta, formatCurrency } = require('./services/time_machine/shared');

// 模拟 API 返回的数据
const testApiItems = [
  {
    name: '猪肉',
    price_then: '2.5',
    price_now: '25.0',
    purchasing_power: '如今约是当年的 10 倍'
  },
  {
    name: '大米',
    price_then: '0.8',
    price_now: '6.0'
  },
  {
    name: '鸡蛋',
    price_then: '1.2',
    price_now: '12.0'
  }
];

console.log('测试 normalizeApiItems 函数:');
const result = normalizeApiItems(testApiItems, 1990);
console.log('\n函数返回结果:');
console.log(result);