"""Centralized icon management using QtAwesome"""
import qtawesome as qta


class IconManager:
    """Manages all icons for the application using QtAwesome"""
    
    # Color scheme
    APPLE_BLUE = "#007AFF"
    APPLE_GOLD = "#FFCC00"
    APPLE_GRAY = "#8E8E93"
    WHITE = "#FFFFFF"
    LIGHT_GRAY = "#C8C8C8"
    DARK_GRAY = "#3A3A3C"
    
    @staticmethod
    def get_document_icon(color=APPLE_BLUE, size=20):
        """Get document/file icon"""
        return qta.icon('fa5s.file-alt', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_star_icon(filled=False, color=None, size=20):
        """Get star icon for favorites"""
        if filled:
            return qta.icon('fa5s.star', color=color or IconManager.APPLE_GOLD, scale_factor=1.0)
        else:
            # Use base star with lighter color for unfilled
            return qta.icon('fa5.star', color=color or IconManager.LIGHT_GRAY, scale_factor=1.0)
    
    @staticmethod
    def get_menu_icon(color=APPLE_GRAY, size=20):
        """Get menu icon (three dots vertical)"""
        return qta.icon('fa5s.ellipsis-v', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_close_icon(color=APPLE_GRAY, size=16):
        """Get close/X icon"""
        return qta.icon('fa5s.times', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_export_icon(color=WHITE, size=20):
        """Get export icon"""
        return qta.icon('fa5s.file-export', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_edit_icon(color=WHITE, size=20):
        """Get edit icon"""
        return qta.icon('fa5s.edit', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_theme_icon(color=WHITE, size=20):
        """Get theme toggle icon"""
        return qta.icon('fa5s.adjust-alt', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_search_icon(color=APPLE_GRAY, size=16):
        """Get search icon"""
        return qta.icon('fa5s.search', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_folder_icon(color=APPLE_BLUE, size=20):
        """Get folder icon"""
        return qta.icon('fa5s.folder', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_chevron_right_icon(color=APPLE_GRAY, size=16):
        """Get chevron right icon"""
        return qta.icon('fa5s.chevron-right', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_chevron_down_icon(color=APPLE_GRAY, size=16):
        """Get chevron down icon"""
        return qta.icon('fa5s.chevron-down', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_home_icon(color=APPLE_BLUE, size=20):
        """Get home icon"""
        return qta.icon('fa5s.home', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_clock_icon(color=APPLE_BLUE, size=20):
        """Get clock/recent icon"""
        return qta.icon('fa5s.clock', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_image_icon(color=APPLE_BLUE, size=20):
        """Get image icon"""
        return qta.icon('fa5s.image', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_code_icon(color=APPLE_BLUE, size=20):
        """Get code icon"""
        return qta.icon('fa5s.code', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_window_icon(color=APPLE_BLUE, size=64):
        """Get window/app icon for title bar"""
        # Use a document with code brackets
        return qta.icon('fa5s.file-code', color=color, scale_factor=1.2)
    
    @staticmethod
    def get_orb_document_icon(color=WHITE, size=20):
        """Get document icon for floating orb"""
        return qta.icon('fa5s.file-alt', color=color, scale_factor=1.0)
    
    @staticmethod
    def get_settings_icon(color=APPLE_GRAY, size=20):
        """Get settings/gear icon"""
        return qta.icon('fa5s.cog', color=color, scale_factor=1.0)