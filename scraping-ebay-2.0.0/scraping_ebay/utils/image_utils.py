import re
from typing import Optional

class ImageUtils:
    
    @staticmethod
    def get_high_resolution_url(
        image_url: Optional[str],
        image_size: str = "s-l500"
    ) -> Optional[str]:
        """_summary_

        Args:
            image_url (Optional[str]): _description_
            image_size (str, optional): _description_. Defaults to "s-l500".

        Returns:
            Optional[str]: _description_
        """
        if not image_url:
            return None

        # Replace the size in the URL with the desired size
        high_res_url = re.sub(r"s-l\d+", image_size, image_url)
        return high_res_url
    
    @staticmethod
    def is_image_url(url: Optional[str]) -> bool:
        """
        Returns True if URL points to an image.
        """

        if not url:
            return False

        return any(
            url.lower().endswith(ext)
            for ext in (
                ".jpg",
                ".jpeg",
                ".png",
                ".webp"
            )
        )
    
    @staticmethod
    def unique_urls(urls):
        """
        Remove duplicate URLs while preserving order.
        """

        seen = set()
        result = []

        for url in urls:

            if url not in seen:
                seen.add(url)
                result.append(url)

        return result
    
    @staticmethod
    def extract_best_image(urls):
        """
        Return the highest quality image URL.

        To be implemented.
        """
        pass