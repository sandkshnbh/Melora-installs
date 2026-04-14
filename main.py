import sys
import os
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, Gio, GLib

from src.ui import InstallerWindow
from src.settings import SettingsWindow
from src.i18n import _, I18nManager
from src.config import ConfigManager

class MeloraInstaller(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(flags=Gio.ApplicationFlags.HANDLES_OPEN, **kwargs)
        self.connect('activate', self.on_activate)
        self.connect('open', self.on_open)
        
        self.config = ConfigManager()
        I18nManager().set_language(self.config.get("general", "language"))
        
        self.css_provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.update_appearance()
        
        # Register custom icon theme path
        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        icon_theme.add_search_path(assets_path)
        
        # Add preferences action
        action_prefs = Gio.SimpleAction.new("preferences", None)
        action_prefs.connect("activate", self.on_preferences_action)
        self.add_action(action_prefs)
        self.set_accels_for_action("app.preferences", ["<Primary>comma"])

        # Add about action
        action_about = Gio.SimpleAction.new("about", None)
        action_about.connect("activate", self.on_about_action)
        self.add_action(action_about)

    def update_appearance(self):
        from src.config import ConfigManager
        config = ConfigManager()
        accent = config.get("appearance", "accent_color") or "blue"
        is_deep_dark = config.get("appearance", "deep_dark")
        
        # 1. Update Global Accent Colors
        colors = {
            "blue": ("#3584e4", "#ffffff"),
            "red": ("#e01b24", "#ffffff"),
            "green": ("#26a269", "#ffffff"),
            "purple": ("#9141ac", "#ffffff"),
            "orange": ("#ff7800", "#ffffff")
        }
        color_hex, fg_hex = colors.get(accent, ("#3584e4", "#ffffff"))
        
        css = f"""
        :root {{
            --accent-bg-color: {color_hex};
            --accent-fg-color: {fg_hex};
            --accent-color: {color_hex};
        }}
        
        .deep-dark {{
            --window-bg-color: #101010;
            --window-fg-color: #eeeeee;
            --view-bg-color: #121212;
            --view-fg-color: #eeeeee;
            --headerbar-bg-color: transparent;
            --headerbar-fg-color: #eeeeee;
            --headerbar-border-color: transparent;
            --card-bg-color: #151515;
            --card-fg-color: #eeeeee;
            --card-border-color: #303030;
            --popover-bg-color: #151515;
            --popover-fg-color: #eeeeee;
            --dialog-bg-color: #101010;
            --dialog-fg-color: #eeeeee;
        }}

        headerbar.flat {{
            background-color: transparent;
            background-image: none;
            border-color: transparent;
            box-shadow: none;
        }}

        /* Ensure standard dark mode still looks great on Fedora */
        @media (prefers-color-scheme: dark) {{
            .deep-dark {{
                --window-bg-color: #101010;
            }}
        }}
        """
        self.css_provider.load_from_data(css.encode())
        
        # 2. Update Style Manager (Global)
        style_manager = Adw.StyleManager.get_default()
        if is_deep_dark:
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
            
        # 3. Update all windows (CSS Classes)
        for window in self.get_windows():
            if is_deep_dark:
                window.add_css_class("deep-dark")
            else:
                window.remove_css_class("deep-dark")

    def on_preferences_action(self, action, param):
        prefs_win = SettingsWindow(application=self)
        self.update_appearance() # Ensure current classes are applied to the new window
        prefs_win.present()

    def on_about_action(self, action, param):
        about = Adw.AboutWindow(
            transient_for=self.win,
            application_name=_("app_name"),
            application_icon="sk",
            developer_name="sandkshnbh",
            version="1.0.0",
            website="https://github.com/sandkshnbh/Melora-installs",
            issue_url="https://github.com/sandkshnbh/Melora-installs/issues",
            copyright="© 2024 sandkshnbh"
        )
        
        # Ensure it follows the theme class
        from src.config import ConfigManager
        if ConfigManager().get("appearance", "deep_dark"):
            about.add_css_class("deep-dark")
            
        about.present()
        # Handle the branding image (developer portrait)
        # AdwAboutWindow doesn't have a direct "set_developer_photo", 
        # but we can use branding-image or just add it to credits.
        # Let's set the branding image to the developer photo.
        try:
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(curr_dir, "assets", "sk.png")
            if os.path.exists(logo_path):
                # Safe check for older Libadwaita
                if hasattr(about, 'set_property') and about.find_property("branding-image"):
                    paintable = Gtk.Image.new_from_file(logo_path).get_paintable()
                    about.set_property("branding-image", paintable)
        except Exception as e:
            print(f"Branding image fallback error: {e}")
            pass
            
        about.set_transient_for(self.win)
        about.present()
        self.update_appearance() # Apply theme to the newly created About window

    def on_activate(self, app):
        self.win = InstallerWindow(application=app)
        self.update_appearance() # Apply theme to main window
        self.win.present()
        
        # Check if we have a file from command line (for simple activation)
        if len(sys.argv) > 1:
            file_path = os.path.abspath(sys.argv[1])
            if os.path.exists(file_path):
                self.win.start_installation(file_path)

    def on_open(self, app, files, n_files, hint):
        self.on_activate(app)
        if n_files > 0:
            file_path = files[0].get_path()
            if file_path:
                self.win.start_installation(file_path)

if __name__ == '__main__':
    app = MeloraInstaller(application_id="com.github.installer.Melora")
    app.run(sys.argv)
