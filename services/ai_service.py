#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI评价服务
功能：调用DeepSeek模型API生成货币购买力变化的AI评价
"""

import logging
import requests
import os
from typing import Optional, Sequence, Mapping, Any

logger = logging.getLogger(__name__)

class AIService:
    """AI评价服务"""
    
    def __init__(self):
        """初始化AI服务"""
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.temperature = 0.7

    def _build_price_guardrail_system_prompt(self) -> str:
        """构建 DeepSeek 系统级约束提示词。"""
        return (
            "你是一位精通中国近 50 年经济史的“首席财富精算师”。你的人格特征如下："
            "1. 专业且刻薄：你看透了名义货币的数字游戏，擅长用通胀和购买力稀释的真相“扎”醒用户。"
            "2. 毒舌且风趣：语言犀利，多用反讽、对标和生活化的尖锐对比，拒绝官方套话。"
            "3. 事实至上：你对 80 年代的粮票、90 年代的下海潮、00 年代的房改如数家珍，评论必须建立在事实基础上。"
            "4. 语言风格：北京老炮的损、上海老克勒的傲、互联网毒舌的快，三者结合。"
        )
    
    def _format_price_items(self, price_items: Sequence[Mapping[str, Any]]) -> str:
        """格式化系统已获取的物价信息，供模型严格引用。"""
        lines = []
        for index, item in enumerate(price_items, start=1):
            name = item.get("name", "未知商品")
            unit = item.get("unit") or "未知单位"
            price_then = item.get("price_then", "未知")
            price_now = item.get("price_now", "未知")
            purchasing_power = item.get("purchasing_power") or "未提供购买力描述"
            note = item.get("note") or ""
            note_text = f"，备注：{note}" if note else ""
            lines.append(
                f"{index}. {name}：{price_then}{unit} -> {price_now}{unit}；购买力对比：{purchasing_power}{note_text}"
            )
        return "\n".join(lines)

    def generate_comment(
        self,
        source_year: int,
        amount: float,
        equivalent_amount: float,
        price_items: Sequence[Mapping[str, Any]]
    ) -> Optional[str]:
        """
        生成AI评价
        
        Args:
            source_year: 起始年份
            amount: 原始金额
            equivalent_amount: 等价值
            price_items: 系统已获取的当年完整物价信息
            
        Returns:
            AI评价字符串，生成失败返回None
        """
        if not self.api_key:
            logger.warning("未配置 DeepSeek API 密钥，无法生成 AI 评价")
            return None
        
        try:
            system_prompt = self._build_price_guardrail_system_prompt()
            prompt = (
                f"请对以下财富变迁进行一次\"灵魂辣评\":\n"
                f"- 【核心数据】：{source_year} 年的 {amount} 元，相当于今天的 {equivalent_amount} 元。\n"
                f"- 【历史参考】：物价： {self._format_price_items(price_items)}。\n"
                f"要求：\n"
                f"1. 必须直接引用【历史参考】中的实物数据进行对比。\n"
                f"2. 风格要足够“辣”，重点嘲讽“数字涨了，地位跌了”的真相。\n"
                f"3. 严禁使用“通货膨胀”、“物价上涨”等无聊词汇，改用更具画面感的词。\n"
                f"4. 严格限制在80字以内。"
            )
            
            # 调用DeepSeek API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": 100
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                comment = result["choices"][0]["message"]["content"].strip()
                logger.info(f"AI评价生成成功: {comment}")
                return comment
            else:
                logger.error(f"DeepSeek API调用失败: {response.status_code}, {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"生成AI评价时出错: {str(e)}")
            return None
    
    def generate_custom_comment(self, prompt: str) -> Optional[str]:
        """
        生成自定义评价

        Args:
            prompt: 自定义提示词

        Returns:
            生成的评价字符串，生成失败返回None
        """
        if not self.api_key:
            logger.warning("未配置DeepSeek API密钥，无法生成自定义评价")
            return None

        try:
            system_prompt = self._build_price_guardrail_system_prompt()
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": 100
            }

            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                comment = result["choices"][0]["message"]["content"].strip()
                logger.info(f"自定义评价生成成功: {comment}")
                return comment
            else:
                logger.error(f"DeepSeek API调用失败: {response.status_code}, {response.text}")
                return None

        except Exception as e:
            logger.error(f"生成自定义评价时出错: {str(e)}")
            return None

    def generate_drift_essay(self, current_city: str, target_city: str, monthly_income: float,
                         equivalent_amount: float, identity_label: str) -> Optional[str]:
        """
        生成财富漂流感言

        Args:
            current_city: 当前城市
            target_city: 目标城市
            monthly_income: 月收入
            equivalent_amount: 等值收入
            identity_label: 身份标签

        Returns:
            AI生成的感言，失败返回None
        """
        prompt = f"""请根据以下"财富漂流"结果，写一段犀利风趣的深度吐槽：
                - 用户从{current_city}来到{target_city}。
                - 【购买力变迁】：月薪 {monthly_income} 元转换后，相当于{target_city}的 {equivalent_amount} 元购买力。
                - 【系统判定身份】：{identity_label}。
                要求：
                1. 结合两地典型的生活方式差异进行攻击。
                2. 文案要符合【系统判定身份】的社会语境，越毒舌越好。
                3. 揭示"地理位置决定阶层"的扎心现实。
                4. 严格限制在 100 字以内。"""
        return self.generate_custom_comment(prompt)
