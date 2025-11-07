"""
选择器构建器
负责将数据库中的选择器类型和值转换为 Playwright 选择器
"""


class SelectorBuilder:
    """
    选择器构建器
    将数据库中的 selector_type 和 selector_value 转换为 Playwright 选择器格式
    """
    
    @staticmethod
    def build_selector(selector_type: str, selector_value: str) -> str:
        """
        构建 Playwright 选择器
        
        Args:
            selector_type: 选择器类型（ID/NAME/CSS/XPATH等）
            selector_value: 选择器值
        
        Returns:
            Playwright 格式的选择器字符串
        """
        selector_map = {
            'ID': f'#{selector_value}',
            'NAME': f'[name="{selector_value}"]',
            'CSS': selector_value,
            'XPATH': f'xpath={selector_value}',
            'CLASS_NAME': f'.{selector_value}',
            'TAG_NAME': selector_value,
            'LINK_TEXT': f'text={selector_value}',
            'PARTIAL_LINK_TEXT': f'text=/{selector_value}/',
            'TEST_ID': f'[data-testid="{selector_value}"]'
        }
        
        return selector_map.get(selector_type, selector_value)
    
    @staticmethod
    def escape_selector_value(value: str) -> str:
        """
        转义选择器值中的特殊字符
        
        Args:
            value: 原始值
        
        Returns:
            转义后的值
        """
        # 转义引号
        value = value.replace('"', '\\"')
        value = value.replace("'", "\\'")
        return value
