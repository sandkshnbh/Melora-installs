import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from src.config import ConfigManager
from src.i18n import _, I18nManager

class SettingsWindow(Adw.PreferencesWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("preferences"))
        self.set_default_size(550, 650)
        self.set_search_enabled(True)
        self.config = ConfigManager()
        self.build_ui()

    def on_appearance_changed(self, *args):
        # Update config
        accent_idx = self.accent_row.get_selected()
        accents = ["blue", "red", "green", "purple", "orange"]
        self.config.set("appearance", "accent_color", accents[accent_idx])
        self.config.set("appearance", "deep_dark", self.deep_dark_row.get_active())
        
        # Trigger global update
        app = self.get_application()
        if app and hasattr(app, 'update_appearance'):
            app.update_appearance()

    def on_language_changed(self, combo, pspec):
        langs = ["auto", "en", "ar", "tr", "ru", "zh", "ko", "de", "fa"]
        code = langs[combo.get_selected()]
        self.config.set("general", "language", code)
        I18nManager().set_language(code)
        
        # Trigger global refresh for all open windows
        app = self.get_application()
        if app:
            for window in app.get_windows():
                if hasattr(window, "update_ui_strings"):
                    window.update_ui_strings()
        
    def update_ui_strings(self):
        """Update strings for this window."""
        self.set_title(_("preferences"))
        self.general_page.set_title(_("general"))
        self.general_group.set_title(_("general"))
        self.lang_row.set_title(_("language"))
        self.startup_row.set_title(_("startup"))
        self.notif_row.set_title(_("notifications"))
        
        self.appearance_page.set_title(_("appearance"))
        self.appearance_group.set_title(_("appearance"))
        self.accent_row.set_title(_("accent_color"))
        self.deep_dark_row.set_title(_("deep_dark"))
        
        self.installation_page.set_title(_("installation"))
        self.installation_group.set_title(_("installation"))
        self.auto_deps_row.set_title(_("auto_deps"))
        self.sudo_row.set_title(_("sudo_mode"))
        self.sudo_row.set_subtitle(_("sudo_subtitle"))

        self.appimage_page.set_title(_("save_path"))
        self.appimage_group.set_title(_("advanced"))
        self.appimage_path.set_title(_("save_path"))
        self.appimage_shortcut.set_title(_("shortcuts"))
        
        self.security_page.set_title(_("security"))
        self.security_group.set_title(_("security"))
        self.warn_untrusted.set_title(_("warn_untrusted"))
        
        self.advanced_page.set_title(_("advanced"))
        self.advanced_group.set_title(_("advanced"))
        self.debug_mode.set_title(_("debug_mode"))

    def build_ui(self):
        # 1. General Page
        self.general_page = Adw.PreferencesPage(title=_("general"), icon_name="preferences-system-symbolic")
        self.add(self.general_page)

        self.general_group = Adw.PreferencesGroup(title=_("general"))
        self.general_page.add(self.general_group)

        # Language Selection
        self.lang_row = Adw.ComboRow(title=_("language"))
        # ... (rest stays the same but variables are now self.)
        self.lang_row.set_model(Gtk.StringList.new([
            "Auto (System)", "English", "العربية", "Türkçe", "Русский", "简体中文", "한국어", "Deutsch", "فارسی"
        ]))
        
        langs = ["auto", "en", "ar", "tr", "ru", "zh", "ko", "de", "fa"]
        current_lang = self.config.get("general", "language") or "auto"
        try:
            self.lang_row.set_selected(langs.index(current_lang))
        except:
            self.lang_row.set_selected(0)
            
        self.lang_row.connect("notify::selected", self.on_language_changed)
        self.general_group.add(self.lang_row)

        self.startup_row = Adw.SwitchRow(title=_("startup"), subtitle=_("general"))
        self.startup_row.set_active(self.config.get("general", "startup"))
        self.startup_row.connect("notify::active", lambda row, params: self.config.set("general", "startup", row.get_active()))
        self.general_group.add(self.startup_row)

        self.notif_row = Adw.SwitchRow(title=_("notifications"), subtitle=_("general"))
        self.notif_row.set_active(self.config.get("general", "notifications"))
        self.notif_row.connect("notify::active", lambda row, params: self.config.set("general", "notifications", row.get_active()))
        self.general_group.add(self.notif_row)

        # Appearance Page
        self.appearance_page = Adw.PreferencesPage(title=_("appearance"), icon_name="preferences-desktop-theme-symbolic")
        self.add(self.appearance_page)

        self.appearance_group = Adw.PreferencesGroup(title=_("appearance"))
        self.appearance_page.add(self.appearance_group)

        self.accent_row = Adw.ComboRow(title=_("accent_color"))
        self.accent_row.set_model(Gtk.StringList.new(["Blue", "Red", "Green", "Purple", "Orange"]))
        
        current_accent = self.config.get("appearance", "accent_color") or "blue"
        accents = ["blue", "red", "green", "purple", "orange"]
        try:
            self.accent_row.set_selected(accents.index(current_accent))
        except:
            self.accent_row.set_selected(0)
            
        self.accent_row.connect("notify::selected", self.on_appearance_changed)
        self.appearance_group.add(self.accent_row)

        self.deep_dark_row = Adw.SwitchRow(title=_("deep_dark"))
        self.deep_dark_row.set_active(self.config.get("appearance", "deep_dark"))
        self.deep_dark_row.connect("notify::active", self.on_appearance_changed)
        self.appearance_group.add(self.deep_dark_row)


        # 2. Installation Page
        self.installation_page = Adw.PreferencesPage(title=_("installation"), icon_name="software-update-available-symbolic")
        self.add(self.installation_page)

        self.installation_group = Adw.PreferencesGroup(title=_("installation"))
        self.installation_page.add(self.installation_group)

        self.auto_deps_row = Adw.SwitchRow(title=_("auto_deps"))
        self.auto_deps_row.set_active(self.config.get("installation", "auto_install_deps"))
        self.auto_deps_row.connect("notify::active", lambda row, params: self.config.set("installation", "auto_install_deps", row.get_active()))
        self.installation_group.add(self.auto_deps_row)

        self.sudo_row = Adw.SwitchRow(title=_("sudo_mode"), subtitle=_("sudo_subtitle"))
        self.sudo_row.set_active(self.config.get("installation", "use_sudo"))
        self.sudo_row.connect("notify::active", lambda row, params: self.config.set("installation", "use_sudo", row.get_active()))
        self.installation_group.add(self.sudo_row)

        # 3. AppImage Page
        self.appimage_page = Adw.PreferencesPage(title=_("save_path"), icon_name="application-x-executable-symbolic")
        self.add(self.appimage_page)
        
        self.appimage_group = Adw.PreferencesGroup(title=_("advanced"))
        self.appimage_page.add(self.appimage_group)
        
        self.appimage_path = Adw.EntryRow(title="Save Path")
        self.appimage_path.set_text(self.config.get("appimage", "save_path"))
        self.appimage_path.connect("changed", lambda row: self.config.set("appimage", "save_path", row.get_text()))
        self.appimage_group.add(self.appimage_path)

        self.appimage_shortcut = Adw.SwitchRow(title="Create Desktop Shortcut", subtitle="Integrate with GNOME App Grid automatically")
        self.appimage_shortcut.set_active(self.config.get("appimage", "auto_shortcut"))
        self.appimage_shortcut.connect("notify::active", lambda row, params: self.config.set("appimage", "auto_shortcut", row.get_active()))
        self.appimage_group.add(self.appimage_shortcut)

        # 4. Security Page
        self.security_page = Adw.PreferencesPage(title=_("security"), icon_name="security-high-symbolic")
        self.add(self.security_page)

        self.security_group = Adw.PreferencesGroup(title=_("security"))
        self.security_page.add(self.security_group)

        self.warn_untrusted = Adw.SwitchRow(title="Warn Untrusted Sources", subtitle="Show warning for unofficial sources")
        self.warn_untrusted.set_active(self.config.get("security", "warn_untrusted"))
        self.warn_untrusted.connect("notify::active", lambda row, params: self.config.set("security", "warn_untrusted", row.get_active()))
        self.security_group.add(self.warn_untrusted)

        self.vt_api = Adw.PasswordEntryRow(title="VirusTotal API Key (Optional)")
        self.vt_api.set_text(self.config.get("security", "virustotal_api_key"))
        self.vt_api.connect("changed", lambda row: self.config.set("security", "virustotal_api_key", row.get_text()))
        self.security_group.add(self.vt_api)

        # 5. Advanced Options Page
        self.advanced_page = Adw.PreferencesPage(title=_("advanced"), icon_name="preferences-other-symbolic")
        self.add(self.advanced_page)

        self.advanced_group = Adw.PreferencesGroup(title=_("advanced"))
        self.advanced_page.add(self.advanced_group)

        self.debug_mode = Adw.SwitchRow(title="Debug Mode", subtitle="Enable detailed application logs")
        self.debug_mode.set_active(self.config.get("advanced", "debug_mode"))
        self.debug_mode.connect("notify::active", lambda row, params: self.config.set("advanced", "debug_mode", row.get_active()))
        self.advanced_group.add(self.debug_mode)
