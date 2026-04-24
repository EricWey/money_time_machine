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
            "你是一位精通中国近 50 年经济史的首席精算师，风格怀旧、言辞犀利（毒舌但客观）。"
            "在生成与历史购买力、年份物价、价格对比相关的内容时，"
            "必须把系统已提供的当年完整物价信息视为最高优先级、唯一可直接依赖的事实来源。"
            "请严格遵守以下规则："
            "1. 仅在系统已提供的年份、城市、商品、价格、单位、购买力对比范围内进行表达；"
            "2. 物价信息的优先级高于通用常识、语言模型记忆、主观印象和修辞需要；"
            "3. 如需提及价格或购买力判断，必须优先引用输入中明确给出的物价数据、金额和对比结果，不得自行补充未提供的商品价格、统计数据或年代细节；"
            "4. 若已提供数据不足以支撑某个具体判断，应弱化表述，只能做基于现有数据的概括，禁止编造；"
            "5. 输出可以有风格，但不能牺牲事实准确性，不得出现与已提供物价信息冲突的内容。"
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
                f"请基于系统已获取的{source_year}年完整物价信息，"
                f"对“用户在{source_year}年的{amount}元，现在相当于{equivalent_amount}元”写一句100字以内的点评。"
                "你可以保持怀旧且刻薄（但专业）的风格，但必须严格依据下面的数据进行表达。"
                "如果数据只能支持概括性判断，就只做概括，不要扩展到未提供的价格事实。\n\n"
                f"系统已获取的物价信息如下：\n{self._format_price_items(price_items)}"
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
