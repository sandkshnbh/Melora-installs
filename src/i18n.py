import locale
import os
from gi.repository import Gtk

TRANSLATIONS = {
    "en": {
        "app_name": "Melora Installer",
        "preferences": "Preferences",
        "about": "About Melora",
        "general": "General",
        "appearance": "Appearance",
        "installation": "Installation",
        "security": "Security",
        "advanced": "Advanced",
        "select_file": "Select Installation File",
        "drop_hint": "Drop your Linux package here (.deb, .rpm, .AppImage, .flatpakref)",
        "installing": "Installing...",
        "uninstalling": "Uninstalling {0}...",
        "install_success": "Installation Complete!",
        "install_failed": "Installation Failed.",
        "accent_color": "Accent Color",
        "deep_dark": "Deep Dark Mode",
        "language": "Language",
        "sudo_mode": "Install as Root (Sudo)",
        "sudo_subtitle": "Use pkexec for system-wide package installations",
        "apps_manager": "App Manager",
        "no_apps": "No applications installed via Melora yet.",
        "uninstall": "Uninstall",
        "notifications": "Enable Notifications",
        "startup": "Run at Startup",
        "auto_deps": "Auto Install Dependencies",
        "save_path": "Save Path",
        "shortcuts": "Create Desktop Shortcut",
        "warn_untrusted": "Warn Untrusted Sources",
        "debug_mode": "Debug Mode",
    },
    "ar": {
        "app_name": "مثبت ميلورا",
        "preferences": "التفضيلات",
        "about": "حول ميلورا",
        "general": "عام",
        "appearance": "المظهر",
        "installation": "التثبيت",
        "security": "الأمان",
        "advanced": "متقدم",
        "select_file": "اختر ملف التثبيت",
        "drop_hint": "أفلت حزمة لينكس هنا (.deb, .rpm, .AppImage, .flatpakref)",
        "installing": "جاري التثبيت...",
        "uninstalling": "جاري حذف {0}...",
        "install_success": "اكتمل التثبيت بنجاح!",
        "install_failed": "فشل التثبيت.",
        "accent_color": "اللون المميز",
        "deep_dark": "وضع السواد العميق",
        "language": "اللغة",
        "sudo_mode": "التثبيت بصلاحيات Root (Sudo)",
        "sudo_subtitle": "استخدام pkexec لتثبيت الحزم على مستوى النظام",
        "apps_manager": "مدير التطبيقات",
        "no_apps": "لا توجد تطبيقات مثبتة عبر ميلورا بعد.",
        "uninstall": "حذف",
        "notifications": "تفعيل التنبيهات",
        "startup": "تشغيل عند البدء",
        "auto_deps": "تثبيت التبعيات تلقائياً",
        "save_path": "مسار الحفظ",
        "shortcuts": "إنشاء اختصار سطح المكتب",
        "warn_untrusted": "التحذير من المصادر غير الموثوقة",
        "debug_mode": "وضع التصحيح (Debug)",
    },
    "tr": {
        "app_name": "Melora Kurucu",
        "preferences": "Tercihler",
        "about": "Melora Hakkında",
        "general": "Genel",
        "appearance": "Görünüm",
        "installation": "Kurulum",
        "security": "Güvenlik",
        "advanced": "Gelişmiş",
        "select_file": "Kurulum Dosyası Seç",
        "drop_hint": "Linux paketini buraya bırakın (.deb, .rpm, .AppImage, .flatpakref)",
        "installing": "Kuruluyor...",
        "uninstalling": "{0} kaldırılıyor...",
        "install_success": "Kurulum Tamamlandı!",
        "install_failed": "Kurulum Başarısız.",
        "accent_color": "Vurgu Rengi",
        "deep_dark": "Derin Karanlık Mod",
        "language": "Dil",
        "sudo_mode": "Kök (Sudo) Olarak Kur",
        "sudo_subtitle": "Sistem genelinde paket kurulumları için pkexec kullanın",
        "apps_manager": "Uygulama Yöneticisi",
        "no_apps": "Henüz Melora üzerinden yüklü uygulama yok.",
        "uninstall": "Kaldır",
        "notifications": "Bildirimleri Etkinleştir",
        "startup": "Başlangıçta Çalıştır",
        "auto_deps": "Bağımlılıkları Otomatik Kur",
        "save_path": "Kaydetme Yolu",
        "shortcuts": "Masaüstü Kısayolu Oluştur",
        "warn_untrusted": "Güvenilmeyen Kaynakları Uyar",
        "debug_mode": "Hata Ayıklama Modu",
    },
    "ru": {
        "app_name": "Установщик Melora",
        "preferences": "Настройки",
        "about": "О Melora",
        "general": "Общие",
        "appearance": "Внешний вид",
        "installation": "Установка",
        "security": "Безопасность",
        "advanced": "Дополнительно",
        "select_file": "Выберите файл для установки",
        "drop_hint": "Перетащите пакет Linux сюда (.deb, .rpm, .AppImage, .flatpakref)",
        "installing": "Установка...",
        "uninstalling": "Удаление {0}...",
        "install_success": "Установка завершена!",
        "install_failed": "ошибка установки.",
        "accent_color": "Акцентный цвет",
        "deep_dark": "Глубокий темный режим",
        "language": "Язык",
        "sudo_mode": "Установка от Root (Sudo)",
        "sudo_subtitle": "Использовать pkexec для системной установки пакетов",
        "apps_manager": "Менеджер приложений",
        "no_apps": "Приложений, установленных через Melora, пока нет.",
        "uninstall": "Удалить",
        "notifications": "Включить уведомления",
        "startup": "Запуск при загрузке",
        "auto_deps": "Автоустановка зависимостей",
        "save_path": "Путь сохранения",
        "shortcuts": "Создать ярлык на рабочем столе",
        "warn_untrusted": "Предупреждать о ненадежных источниках",
        "debug_mode": "Режим отладки",
    },
    "zh": {
        "app_name": "Melora 安装程序",
        "preferences": "首选项",
        "about": "关于 Melora",
        "general": "通用",
        "appearance": "外观",
        "installation": "安装",
        "security": "安全",
        "advanced": "高级",
        "select_file": "选择安装文件",
        "drop_hint": "将 Linux 软件包拖到此处 (.deb, .rpm, .AppImage, .flatpakref)",
        "installing": "正在安装...",
        "uninstalling": "正在卸载 {0}...",
        "install_success": "安装完成！",
        "install_failed": "安装失败。",
        "accent_color": "强调色",
        "deep_dark": "深色模式",
        "language": "语言",
        "sudo_mode": "以 Root (Sudo) 身份安装",
        "sudo_subtitle": "使用 pkexec 进行系统级软件包安装",
        "apps_manager": "应用管理器",
        "no_apps": "尚未通过 Melora 安装任何应用程序。",
        "uninstall": "卸载",
        "notifications": "启用通知",
        "startup": "开机启动",
        "auto_deps": "自动安装依赖项",
        "save_path": "保存路径",
        "shortcuts": "创建桌面快捷方式",
        "warn_untrusted": "警告不受信任的来源",
        "debug_mode": "调试模式",
    },
    "ko": {
        "app_name": "Melora 설치 관리자",
        "preferences": "환경 설정",
        "about": "Melora 정보",
        "general": "일반",
        "appearance": "모양",
        "installation": "설치",
        "security": "보안",
        "advanced": "고급",
        "select_file": "설치 파일 선택",
        "drop_hint": "Linux 패키지를 여기에 놓으십시오 (.deb, .rpm, .AppImage, .flatpakref)",
        "installing": "설치 중...",
        "uninstalling": "{0} 삭제 중...",
        "install_success": "설치 완료!",
        "install_failed": "설치 실패.",
        "accent_color": "강조 색상",
        "deep_dark": "딥 다크 모드",
        "language": "언어",
        "sudo_mode": "Root(Sudo)로 설치",
        "sudo_subtitle": "시스템 전체 패키지 설치에 pkexec 사용",
        "apps_manager": "앱 관리자",
        "no_apps": "Melora를 통해 설치된 애플리케이션이 없습니다.",
        "uninstall": "삭제",
        "notifications": "알림 활성화",
        "startup": "시작 시 실행",
        "auto_deps": "종속성 자동 설치",
        "save_path": "저장 경로",
        "shortcuts": "바탕 화면 바로 가기 생성",
        "warn_untrusted": "신뢰할 수 없는 소스 경고",
        "debug_mode": "디버그 모드",
    },
    "de": {
        "app_name": "Melora Installer",
        "preferences": "Einstellungen",
        "about": "Über Melora",
        "general": "Allgemein",
        "appearance": "Aussehen",
        "installation": "Installation",
        "security": "Sicherheit",
        "advanced": "Erweitert",
        "select_file": "Installationsdatei auswählen",
        "drop_hint": "Linux-Paket hier ablegen (.deb, .rpm, .AppImage, .flatpakref)",
        "installing": "Installieren...",
        "uninstalling": "{0} wird deinstalliert...",
        "install_success": "Installation abgeschlossen!",
        "install_failed": "Installation fehlgeschlagen.",
        "accent_color": "Akzentfarbe",
        "deep_dark": "Tiefer Dunkelmodus",
        "language": "Sprache",
        "sudo_mode": "Als Root (Sudo) installieren",
        "sudo_subtitle": "Verwenden Sie pkexec für systemweite Paketinstallationen",
        "apps_manager": "App-Manager",
        "no_apps": "Noch keine Anwendungen über Melora installiert.",
        "uninstall": "Deinstallieren",
        "notifications": "Benachrichtigungen aktivieren",
        "startup": "Beim Start ausführen",
        "auto_deps": "Abhängigkeiten automatisch installieren",
        "save_path": "Speicherpfad",
        "shortcuts": "Desktop-Verknüpfung erstellen",
        "warn_untrusted": "Vor nicht vertrauenswürdigen Quellen warnen",
        "debug_mode": "Debug-Modus",
    },
    "fa": {
        "app_name": "نصب‌کننده ملورا",
        "preferences": "تنظیمات",
        "about": "درباره ملورا",
        "general": "عمومی",
        "appearance": "ظاهر",
        "installation": "نصب",
        "security": "امنیت",
        "advanced": "پیشرفته",
        "select_file": "انتخاب فایل نصب",
        "drop_hint": "بسته لینوکس را اینجا رها کنید (.deb, .rpm, .AppImage, .flatpakref)",
        "installing": "در حال نصب...",
        "uninstalling": "در حال حذف {0}...",
        "install_success": "نصب با موفقیت انجام شد!",
        "install_failed": "نصب با شکست مواجه شد.",
        "accent_color": "رنگ شاخص",
        "deep_dark": "حالت تیره عمیق",
        "language": "زبان",
        "sudo_mode": "نصب به عنوان روت (Sudo)",
        "sudo_subtitle": "استفاده از pkexec برای نصب بسته‌ها در سطح سیستم",
        "apps_manager": "مدیریت برنامه‌ها",
        "no_apps": "هنوز هیچ برنامه‌ای توسط ملورا نصب نشده است.",
        "uninstall": "حذف",
        "notifications": "فعال‌سازی اعلان‌ها",
        "startup": "اجرا در هنگام راه‌اندازی",
        "auto_deps": "نصب خودکار وابستگی‌ها",
        "save_path": "مسیر ذخیره",
        "shortcuts": "ایجاد میانبر دسکتاپ",
        "warn_untrusted": "هشدار برای منابع نامعتبر",
        "debug_mode": "حالت عیب‌یابی",
    }
}

class I18nManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(I18nManager, cls).__new__(cls)
            cls._instance.current_lang = "en"
        return cls._instance
    
    def set_language(self, lang_code):
        if lang_code == "auto":
            self.current_lang = self.detect_system_language()
        elif lang_code in TRANSLATIONS:
            self.current_lang = lang_code
        else:
            self.current_lang = "en"
            
        # Apply RTL to GTK if needed
        self.apply_direction()

    def detect_system_language(self):
        try:
            # Check LANGUAGE env first (often used for prioritized list)
            env_langs = os.environ.get('LANGUAGE', '')
            if env_langs:
                for lang in env_langs.split(':'):
                    code = lang.split('_')[0].split('.')[0]
                    if code in TRANSLATIONS:
                        return code
            
            # Check LANG env
            env_lang = os.environ.get('LANG', '')
            if env_lang:
                code = env_lang.split('_')[0].split('.')[0]
                if code in TRANSLATIONS:
                    return code
            
            # Fallback to locale module
            lang_tuple = locale.getlocale()
            if lang_tuple and lang_tuple[0]:
                code = lang_tuple[0].split('_')[0]
                if code in TRANSLATIONS:
                    return code
        except:
            pass
        return "en"

    def get(self, key, *args):
        text = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"]).get(key, key)
        if args:
            return text.format(*args)
        return text

    def apply_direction(self):
        rtl_langs = ["ar", "fa"]
        if self.current_lang in rtl_langs:
            Gtk.Widget.set_default_direction(Gtk.TextDirection.RTL)
        else:
            Gtk.Widget.set_default_direction(Gtk.TextDirection.LTR)

# Global helper function
def _(key, *args):
    return I18nManager().get(key, *args)
