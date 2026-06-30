class SelectorUtils:
    @staticmethod
    def css_text(node, selector, default=None):
        """
        Return stripped text from a CSS selector.
        """
        value = node.css(selector).get()
        if value:
            return value.strip()
        return default
    
    @staticmethod
    def css_attr(node, selector, default=None):
        """
        Return stripped attribute value.
        """
        value = node.css(selector).get()
        if value:
            return value.strip()
        return default