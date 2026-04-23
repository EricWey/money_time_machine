"""时光机实物元数据。"""

from typing import Dict


ITEM_METADATA: Dict[str, dict] = {
    "梗米": {
        "category": "food",
        "unit": "元/斤",
        "note": "家庭主食的基础款，一斤米价最能照见日常饭桌的分量。",
    },
    "大豆油": {
        "category": "food",
        "unit": "元/升",
        "note": "厨房刚需消耗品，油价起伏通常会悄悄传导到每一顿家常菜。",
    },
    "精瘦肉": {
        "category": "food",
        "unit": "元/斤",
        "note": "家常荤菜的代表，一斤肉价最容易让人感到餐桌成本的变化。",
    },
    "棉质T恤": {
        "category": "clothing",
        "unit": "元/件",
        "note": "日常穿着的基础单品，一件T恤能看出消费从耐穿到快消的变化。",
    },
    "330ml啤酒": {
        "category": "beverage",
        "unit": "元/瓶",
        "note": "最常见的轻社交饮品，一瓶价格常常对应一代人的夜生活记忆。",
    },
    "500ml五粮液": {
        "category": "beverage",
        "unit": "元/瓶",
        "note": "典型的宴请型消费品，一瓶价格往往映射出礼数与体面的时代成本。",
    },
    "月平均工资": {
        "category": "income",
        "unit": "元/月",
        "note": "这是一个时代最直接的收入刻度，最适合用来对照体感购买力。",
    },
    "理发": {
        "category": "service",
        "unit": "元/次",
        "note": "高频生活服务的代表，一次理发最能反映人工服务价格的时代位移。",
    },
}


def get_item_metadata(item_name: str) -> dict:
    return ITEM_METADATA.get(item_name, {})
