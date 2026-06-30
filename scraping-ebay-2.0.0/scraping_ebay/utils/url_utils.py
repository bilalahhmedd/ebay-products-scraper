import re

class URLUtils:
    @staticmethod
    def extract_product_id(url:str):
        """
        Extract the product ID from the product URL.
        """
        if not url:
            return None
        match = re.search(r"/itm/(\d+)", url)
        return match.group(1) if match else None