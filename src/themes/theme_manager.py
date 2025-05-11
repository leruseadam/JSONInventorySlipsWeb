class ThemeColors:
    def __init__(self, theme="dark"):
        # Define theme colors
        self.themes = {
            "dark": {
                "bg_main": "#1E1E2E",
                "bg_secondary": "#181825",
                "fg_main": "#CDD6F4",
                "fg_secondary": "#BAC2DE",
                "accent": "#89B4FA",
                "highlight": "#F5C2E7",
                "button_bg": "#313244",
                "button_fg": "#CDD6F4",
                "checkbox_bg": "#45475A",
                "checkbox_fg": "#F5C2E7",
                "entry_bg": "#313244",
                "entry_fg": "#CDD6F4",
                "success": "#A6E3A1",
                "error": "#F38BA8",
                "warning": "#FAB387"
            },
            "light": {
                "bg_main": "#EFF1F5",
                "bg_secondary": "#CCD0DA",
                "fg_main": "#4C4F69",
                "fg_secondary": "#5C5F77",
                "accent": "#1E66F5",
                "highlight": "#EA76CB",
                "button_bg": "#DCE0E8",
                "button_fg": "#4C4F69",
                "checkbox_bg": "#BCC0CC",
                "checkbox_fg": "#EA76CB",
                "entry_bg": "#DCE0E8",
                "entry_fg": "#4C4F69",
                "success": "#40A02B",
                "error": "#D20F39",
                "warning": "#FE640B"
            },
            "green": {
                "bg_main": "#1A2F1A",
                "bg_secondary": "#132613",
                "fg_main": "#B8E6B8",
                "fg_secondary": "#99CC99",
                "accent": "#40A02B",
                "highlight": "#73D35F",
                "button_bg": "#2D4B2D",
                "button_fg": "#B8E6B8",
                "checkbox_bg": "#3A5F3A",
                "checkbox_fg": "#73D35F",
                "entry_bg": "#2D4B2D",
                "entry_fg": "#B8E6B8",
                "success": "#40A02B",
                "error": "#E64545",
                "warning": "#FFA500"
            }
        }
        
        # Default to dark theme if requested theme doesn't exist
        self.current = self.themes.get(theme, self.themes["dark"])
    
    def get(self, color_name):
        return self.current.get(color_name, "#FFFFFF")
    
    def switch_theme(self, theme_name):
        if theme_name in self.themes:
            self.current = self.themes[theme_name]
            return True
        return False 