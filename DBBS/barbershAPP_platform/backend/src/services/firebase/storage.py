class StoragePaths:
    PROFILES = 'profiles'
    PORTFOLIO = 'portfolio'
    SHOPS = 'shops'
    TEMP = 'temp'

    @staticmethod
    def get_profile_path(user_id: str) -> str:
        return f"{StoragePaths.PROFILES}/{user_id}"
    
    @staticmethod
    def get_portfolio_path(barber_id: str) -> str:
        return f"{StoragePaths.PORTFOLIO}/{barber_id}"
    
    @staticmethod
    def get_shop_path(shop_id: str) -> str:
        return f"{StoragePaths.SHOPS}/{shop_id}"