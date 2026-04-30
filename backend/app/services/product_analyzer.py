import re
from typing import Optional, Tuple

class ProductAnalyzerService:
    
    # Common product keywords
    PRODUCT_KEYWORDS = [
        'buy', 'purchase', 'order', 'get', 'need', 'want',
        'price', 'cost', 'how much', 'looking for',
        'iphone', 'samsung', 'laptop', 'phone', 'tv', 'watch',
        'headphone', 'camera', 'tablet', 'macbook', 'airpods'
    ]
    
    # Sample product database with prices
    PRODUCT_PRICES = {
        'iphone 15': 79900,
        'iphone 14': 69900,
        'iphone 13': 59900,
        'samsung galaxy s23': 74999,
        'macbook air': 99900,
        'macbook pro': 189900,
        'airpods pro': 24900,
        'apple watch': 41900,
        'ipad': 44900,
        'sony headphones': 15900,
        'lg tv': 45000,
        'dell laptop': 55000,
    }
    
    def is_product_query(self, query: str) -> bool:
        """Determine if query is product-related"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.PRODUCT_KEYWORDS)
    
    def extract_product_info(self, query: str) -> Tuple[Optional[str], Optional[str], Optional[float]]:
        """
        Extract product name, search query, and budget from user input
        Returns: (product_name, search_query, budget)
        """
        query_lower = query.lower()
        
        # Extract budget if mentioned
        budget = self._extract_budget(query)
        
        # Find product in query
        product_name = None
        search_query = None
        
        for product_key in self.PRODUCT_PRICES.keys():
            if product_key in query_lower:
                product_name = product_key.title()
                search_query = f"{product_name} price"
                break
        
        # If no exact match, create generic search query
        if not product_name:
            # Remove common words and extract potential product
            words = query_lower.split()
            product_words = [w for w in words if w not in ['buy', 'get', 'need', 'want', 'under', 'for', 'a', 'an', 'the']]
            if product_words:
                product_name = ' '.join(product_words[:3]).title()  # Take first 3 words
                search_query = f"{product_name} price"
        
        return product_name, search_query, budget
    
    def _extract_budget(self, query: str) -> Optional[float]:
        """Extract budget amount from query"""
        # Pattern: under 50000, below 50000, ₹50000, 50000 rupees, etc.
        patterns = [
            r'under\s*₹?\s*(\d+)',
            r'below\s*₹?\s*(\d+)',
            r'₹\s*(\d+)',
            r'(\d+)\s*rupees',
            r'(\d+)\s*inr',
            r'budget\s*₹?\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return float(match.group(1))
        
        return None
    
    def get_product_price(self, product_name: str) -> Optional[float]:
        """Get price for a product"""
        if not product_name:
            return None
        
        product_lower = product_name.lower()
        
        # Exact match
        if product_lower in self.PRODUCT_PRICES:
            return self.PRODUCT_PRICES[product_lower]
        
        # Partial match
        for key, price in self.PRODUCT_PRICES.items():
            if key in product_lower or product_lower in key:
                return price
        
        # Default price for unknown products
        return 5000.0

# Singleton instance
product_analyzer_service = ProductAnalyzerService()