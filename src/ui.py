from gi.repository import Gtk, Adw, Gdk, Gio, GLib
import math
import cairo

from src.engine import run_installation, run_uninstallation
from src.config import ConfigManager
from src.database import AppDatabase
from src.i18n import _

class PulseWidget(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_content_width(120)
        self.set_content_height(120)
        self.set_draw_func(self.on_draw)
        self.phase = 0
        self.running = False
        self.timer_id = 0

    def on_draw(self, area, ctx, width, height, data=None):
        if not self.running: return
        xc, yc = width / 2, height / 2
        radius = min(width, height) / 3.5
        
        # Get accent color from config
        config = ConfigManager()
        accent = config.get("appearance", "accent_color") or "blue"
        
        colors = {
            "blue": (0.2, 0.5, 0.9),
            "red": (0.9, 0.1, 0.1),
            "green": (0.1, 0.7, 0.4),
            "purple": (0.6, 0.3, 0.8),
            "orange": (1.0, 0.5, 0.0)
        }
        r, g, b = colors.get(accent, (0.2, 0.5, 0.9))
        
        # 1. Background Glow (Pulsing)
        glow_pulse = (math.sin(self.phase * 2 * math.pi) + 1) / 2
        glow_size = radius * (1.2 + 0.3 * glow_pulse)
        grad = cairo.RadialGradient(xc, yc, 0, xc, yc, glow_size)
        grad.add_color_stop_rgba(0, r, g, b, 0.2)
        grad.add_color_stop_rgba(1, r, g, b, 0)
        ctx.set_source(grad)
        ctx.arc(xc, yc, glow_size, 0, 2 * math.pi)
        ctx.fill()

        # 2. Expanding Echoes
        for i in range(2):
            pr = (self.phase + i * 0.5) % 1.0
            ctx.set_source_rgba(r, g, b, (1.0 - pr) * 0.3)
            ctx.set_line_width(2)
            ctx.arc(xc, yc, pr * radius * 1.8, 0, 2 * math.pi)
            ctx.stroke()

        # 3. Orbital Ring (Rotating)
        ctx.set_line_width(5)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        
        start_angle = self.phase * 4 * math.pi
        end_angle = start_angle + math.pi * 0.7
        
        # Draw ring with a soft glow effect (double stroke)
        ctx.set_source_rgba(r, g, b, 0.2)
        ctx.set_line_width(8)
        ctx.arc(xc, yc, radius, start_angle, end_angle)
        ctx.stroke()
        
        ctx.set_source_rgba(r, g, b, 0.9)
        ctx.set_line_width(4)
        ctx.arc(xc, yc, radius, start_angle, end_angle)
        ctx.stroke()

    def update(self):
        self.phase = (self.phase + 0.012) % 1.0 # Smoother, slightly slower but consistent
        self.queue_draw()
        return self.running

    def start(self):
        if not self.running:
            self.running = True
            self.timer_id = GLib.timeout_add(16, self.update) # ~60 FPS

    def stop(self):
        self.running = False
        self.queue_draw()

class InstallerWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("app_name"))
        self.set_default_size(600, 450)
        self.config = ConfigManager()
        
        self.build_ui()
        self.setup_drag_and_drop()

    def build_ui(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(vbox)

        # 1. Seamless Header (Transparent/Flat for window controls only)
        header = Adw.HeaderBar()
        header.add_css_class("flat") # Makes it blend with background
        vbox.append(header)

        # Menu Button in a Corner (instead of top right header)
        self.menu_button = Gtk.MenuButton()
        self.menu_button.set_icon_name("open-menu-symbolic")
        menu = Gio.Menu()
        menu.append(_("preferences"), "app.preferences")
        menu.append(_("about"), "app.about")
        self.menu_button.set_menu_model(menu)
        header.pack_start(self.menu_button) # Pack start for a balanced look

        # Main View Stack
        self.view_stack = Adw.ViewStack()
        self.view_stack.set_vexpand(True)
        vbox.append(self.view_stack)

        # 2. Bottom Navigation (Modern Mobile-like)
        self.view_switcher_bar = Adw.ViewSwitcherBar()
        self.view_switcher_bar.set_stack(self.view_stack)
        self.view_switcher_bar.set_reveal(True)
        vbox.append(self.view_switcher_bar)

        # 1. Installer Page (The original drop zone)
        installer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        self.stack = Gtk.Stack() # Logic stack for drop/install states
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_vexpand(True)
        installer_box.append(self.stack)
        
        # Installer Tab Info
        self.installer_page_obj = self.view_stack.add_titled(installer_box, "installer", _("installation"))
        self.installer_page_obj.set_icon_name("list-add-symbolic")

        # Welcome/Drop Page
        self.drop_page = Adw.StatusPage()
        self.drop_page.set_title(_("drop_hint").split(" (")[0]) # title part
        self.drop_page.set_description(_("drop_hint"))
        self.drop_page.set_icon_name("sk")
        
        # Add a "Select File" button under the main area
        btn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        
        self.select_button = Gtk.Button(label=_("select_file"))
        self.select_button.add_css_class("pill")
        self.select_button.add_css_class("suggested-action")
        self.select_button.set_size_request(200, -1)
        self.select_button.connect("clicked", self.on_select_file_clicked)
        btn_box.append(self.select_button)
        
        self.drop_page.set_child(btn_box)
        self.stack.add_named(self.drop_page, "drop")

        # Install Page (Logs & Progress)
        install_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        install_box.set_margin_top(20)
        install_box.set_margin_bottom(20)
        install_box.set_margin_start(20)
        install_box.set_margin_end(20)
        
        self.status_label = Gtk.Label(label=_("installing"))
        self.status_label.add_css_class("title-2")
        install_box.append(self.status_label)

        self.pulse = PulseWidget()
        self.pulse.set_halign(Gtk.Align.CENTER)
        install_box.append(self.pulse)

        # Scrolled Window for Logs
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.log_buffer = Gtk.TextBuffer()
        self.log_view = Gtk.TextView(buffer=self.log_buffer)
        self.log_view.set_editable(False)
        self.log_view.set_cursor_visible(False)
        self.log_view.add_css_class("monospace")
        scrolled.set_child(self.log_view)
        
        install_box.append(scrolled)
        
        self.stack.add_named(install_box, "install")

        # 2. Manager Page (Uninstall list)
        self.manager_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.manager_box.set_margin_top(20)
        self.manager_box.set_margin_bottom(20)
        self.manager_box.set_margin_start(20)
        self.manager_box.set_margin_end(20)
        
        self.manager_label = Gtk.Label(label=_("apps_manager"))
        self.manager_label.add_css_class("title-1")
        self.manager_box.append(self.manager_label)
        
        scrolled_manager = Gtk.ScrolledWindow()
        scrolled_manager.set_vexpand(True)
        
        self.app_list = Gtk.ListBox()
        self.app_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.app_list.add_css_class("boxed-list")
        scrolled_manager.set_child(self.app_list)
        self.manager_box.append(scrolled_manager)
        
        self.manager_page_obj = self.view_stack.add_titled(self.manager_box, "manager", _("advanced"))
        self.manager_page_obj.set_icon_name("system-software-install-symbolic")
        
        # Refresh manager list when switching to it
        self.view_stack.connect("notify::visible-child", self.on_view_switch)
        self.refresh_app_list()
        self.update_ui_strings()

    def update_ui_strings(self):
        """Update all strings in the UI to the current language."""
        self.set_title(_("app_name"))
        
        # Bottom Navigation Titles
        self.installer_page_obj.set_title(_("installation"))
        self.manager_page_obj.set_title(_("advanced"))
        
        # Installer Page Content
        self.drop_page.set_title(_("drop_hint").split(" (")[0])
        self.drop_page.set_description(_("drop_hint"))
        self.select_button.set_label(_("select_file"))
        
        self.status_label.set_label(_("installing")) # Default or current state
        
        # Manager Page Content
        self.manager_label.set_label(_("apps_manager"))
        self.refresh_app_list() # Re-translates "No apps" if needed

    def setup_drag_and_drop(self):
        # Allow dropping multiple files, though we currently only process the first one
        drop_target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        drop_target.connect("drop", self.on_file_drop)
        self.add_controller(drop_target)
        
    def on_file_drop(self, target, value, x, y):
        # value is a Gdk.FileList
        files = value.get_files()
        if not files:
            return False
            
        # Get the first dumped file
        file_path = files[0].get_path()
        if not file_path:
            return False
            
        self.start_installation(file_path)
        return True

    def on_select_file_clicked(self, button):
        dialog = Gtk.FileDialog(title=_("select_file"))
        
        # Setup Filters
        filters = Gio.ListStore.new(Gtk.FileFilter)
        
        all_filter = Gtk.FileFilter()
        all_filter.set_name("All Linux Packages")
        all_filter.add_pattern("*.deb")
        all_filter.add_pattern("*.rpm")
        all_filter.add_pattern("*.AppImage")
        all_filter.add_pattern("*.flatpakref")
        filters.append(all_filter)
        
        deb_filter = Gtk.FileFilter()
        deb_filter.set_name("Debian Packages (.deb)")
        deb_filter.add_pattern("*.deb")
        filters.append(deb_filter)
        
        rpm_filter = Gtk.FileFilter()
        rpm_filter.set_name("RPM Packages (.rpm)")
        rpm_filter.add_pattern("*.rpm")
        filters.append(rpm_filter)
        
        dialog.set_filters(filters)
        
        dialog.open(self, None, self.on_file_dialog_open_done)

    def on_file_dialog_open_done(self, dialog, result):
        try:
            file_obj = dialog.open_finish(result)
            if file_obj:
                file_path = file_obj.get_path()
                if file_path:
                    self.start_installation(file_path)
        except Exception as e:
            print(f"File selection error: {e}")

    def start_installation(self, file_path):
        self.stack.set_visible_child_name("install")
        self.log_buffer.set_text("")
        self.pulse.start()
        self.status_label.set_text(_("installing"))
        
        # Start engine installation logic
        run_installation(file_path, self.log_callback, self.done_callback)
        
        # Hide logs if silent mode is enabled
        if self.config.get("installation", "silent_mode"):
            self.log_view.get_parent().set_visible(False)
        else:
            self.log_view.get_parent().set_visible(True)

    def log_callback(self, text):
        # Use idle_add to ensure UI updates happen on main GTK thread
        GLib.idle_add(self._append_log, text)

    def _append_log(self, text):
        end_iter = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end_iter, text)
        
        # Scroll to bottom
        adj = self.log_view.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        return False

    def done_callback(self, success):
        GLib.idle_add(self._install_done, success)

    def _install_done(self, success):
        self.pulse.stop()
        if success:
            self.status_label.set_text(_("install_success"))
            self._send_notification(_("install_success"), _("install_success"))
        else:
            self.status_label.set_text(_("install_failed"))
            self._send_notification(_("install_failed"), _("install_failed"))
        return False
        
    def _send_notification(self, title, body):
        if self.config.get("general", "notifications"):
            notification = Gio.Notification.new(title)
            notification.set_body(body)
            # Use default icon
            notification.set_icon(Gio.ThemedIcon.new("software-update-available-symbolic"))
            app = self.get_application()
            if app:
                app.send_notification("melora-install", notification)
        
        # Refresh list in case they are on manager page
        self.refresh_app_list()

    def on_view_switch(self, stack, pspec):
        if stack.get_visible_child_name() == "manager":
            self.refresh_app_list()

    def refresh_app_list(self):
        # Clear current list
        while child := self.app_list.get_first_child():
            self.app_list.remove(child)
            
        apps = AppDatabase().get_all()
        if not apps:
            empty_row = Adw.ActionRow(title=_("no_apps"))
            self.app_list.append(empty_row)
            return

        for app in apps:
            row = Adw.ActionRow(title=app['name'], subtitle=f"Type: {app['type']} | Date: {app['date']}")
            
            uninstall_btn = Gtk.Button()
            uninstall_btn.set_icon_name("user-trash-symbolic")
            uninstall_btn.set_tooltip_text(_("uninstall"))
            uninstall_btn.set_valign(Gtk.Align.CENTER)
            uninstall_btn.add_css_class("destructive-action")
            uninstall_btn.connect("clicked", self.on_uninstall_clicked, app)
            
            row.add_suffix(uninstall_btn)
            self.app_list.append(row)

    def on_uninstall_clicked(self, button, app_data):
        self.view_stack.set_visible_child_name("installer")
        self.start_uninstallation(app_data)

    def start_uninstallation(self, app_data):
        self.stack.set_visible_child_name("install")
        self.log_buffer.set_text("")
        self.pulse.start()
        self.status_label.set_text(_("uninstalling", app_data['name']))
        
        run_uninstallation(app_data, self.log_callback, self.done_callback)


