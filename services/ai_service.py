#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI评价服务
功能：调用DeepSeek模型API生成货币购买力变化的AI评价
"""

import logging
import requests
import os
from typing import Optional

logger = logging.getLogger(__name__)

class AIService:
    """AI评价服务"""
    
    def __init__(self):
        """初始化AI服务"""
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.temperature = 0.7
    
    def generate_comment(self, source_year: int, amount: float, equivalent_amount: float) -> Optional[str]:
        """
        生成AI评价
        
        Args:
            source_year: 起始年份
            amount: 原始金额
            equivalent_amount: 等价值
            
        Returns:
            AI评价字符串，生成失败返回None
        """
        if not self.api_key:
            logger.warning("未配置DeepSeek API密钥，使用默认评价")
            return f"时光荏苒，{source_year}年的{amount}元现在只值{equivalent_amount}元。"
        
        try:
            # 构建提示词
            prompt = f"你是一个怀旧且刻薄（但专业）的财务专家。用户在{source_year}年的{amount}元，现在相当于{equivalent_amount}元。请结合当时的社会背景写一句50字以内的点评。"
            
            # 调用DeepSeek API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
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
    
    def generate_fallback_comment(self, source_year: int, amount: float, equivalent_amount: float) -> str:
        """
        生成备用评价（当AI服务不可用时使用）

        Args:
            source_year: 起始年份
            amount: 原始金额
            equivalent_amount: 等价值

        Returns:
            备用评价字符串
        """
        return f"时光荏苒，{source_year}年的{amount}元现在只值{equivalent_amount}元。"

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
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [
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