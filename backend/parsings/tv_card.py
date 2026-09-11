class TVCard:
    def __init__(
                    self,
                    name: str = None,
                    title: str = None,
                    url: str = None,
                    description: str = None,
                    os: str = None,
                    screen_resolution: str = None,
                    brand: str = None,
                    matrix: str = None,
                    diagonal: int = None,
                    currency: str = None,
                    full_price=None,
                    discount_price=None,
                    card_price=None,
                 ):
        self.name = name
        self.title = title
        self.url = url
        self.description = description
        self.os = os
        self.screen_resolution = screen_resolution
        self.brand = brand
        self.matrix = matrix
        self.diagonal = diagonal
        self.full_price = full_price
        self.discount_price = discount_price
        self.card_price = card_price
        self.currency = currency

    def get_dict(self):
        return {
            'name': self.name,
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'os': self.os,
            'screen_resolution': self.screen_resolution,
            'brand': self.brand,
            'matrix': self.matrix,
            'diagonal': self.diagonal,
            'full_price': self.full_price,
            'discount_price': self.discount_price,
            'card_price': self.card_price,
            'currency': self.currency,
        }
