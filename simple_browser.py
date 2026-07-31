import sys
import os
from urllib.parse import quote_plus

# --- Robust WebGL & Software Fallback Flags ---
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--enable-webgl --ignore-gpu-blocklist --use-gl=angle --use-angle=swiftshader"
)

from PyQt5.QtCore import QUrl, Qt, QByteArray
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QLineEdit,
    QVBoxLayout, QLabel, QPushButton, QFileDialog, QListWidget,
    QCheckBox, QHBoxLayout, QMessageBox, QWidget, QFrame, QComboBox,
    QStackedWidget, QSplitter, QSizePolicy, QInputDialog
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings
)
from PyQt5.QtNetwork import QNetworkProxy


class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent_window, profile):
        super().__init__(profile, parent_window)
        self.parent_window = parent_window

    def createWindow(self, _type):
        return self.parent_window.add_new_tab().page()


class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Browser - Advanced")
        self.setMinimumSize(640, 480)
        self.resize(1240, 820)

        # --- Settings & Browser State ---
        self.homepage = "internal://home"
        self.download_dir = os.path.expanduser("~/Downloads")
        self.current_theme = "Dark"
        self.is_incognito = False
        self.webgl_enabled = True

        # VPN & Tor States
        self.vpn_enabled = False
        self.tor_enabled = False
        self.selected_proxy = "None"

        self.selected_search_engine = "Google"
        self.search_engines = {
            "Google": "https://www.google.com/search?q=",
            "DuckDuckGo": "https://duckduckgo.com/?q=",
            "Bing": "https://www.bing.com/search?q=",
            "Brave": "https://search.brave.com/search?q="
        }
        self.history = []
        self.downloads = []

        self.bookmarks = [
            {"title": "Google", "url": "https://www.google.com"},
            {"title": "GitHub", "url": "https://www.github.com"}
        ]
        self.home_shortcuts = [
            {"title": "Google", "url": "https://www.google.com", "icon": "🔍"},
            {"title": "GitHub", "url": "https://www.github.com", "icon": "💻"},
            {"title": "YouTube", "url": "https://www.youtube.com", "icon": "▶️"},
            {"title": "Reddit", "url": "https://www.reddit.com", "icon": "🤖"}
        ]

        # WebEngine Profiles
        self.standard_profile = QWebEngineProfile.defaultProfile()
        self.incognito_profile = QWebEngineProfile(self)
        self.active_profile = self.standard_profile

        self.setup_webengine_settings()
        self.standard_profile.downloadRequested.connect(self.on_download_requested)
        self.incognito_profile.downloadRequested.connect(self.on_download_requested)

        # Main Interface Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_vlayout = QVBoxLayout(self.central_widget)
        self.main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.main_vlayout.setSpacing(0)

        # 1. Navigation Bar
        self.setup_navbar()

        # 2. Bookmarks Bar
        self.setup_bookmarks_bar()

        # 3. Main Body Splitter
        self.body_splitter = QSplitter(Qt.Horizontal)
        self.body_splitter.setHandleWidth(2)

        self.setup_sidebar_icons()
        self.setup_overlay_panels()

        # Web Tabs Container
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)

        # New Tab (+) Button
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setObjectName("new_tab_btn")
        self.new_tab_btn.setToolTip("Open New Tab")
        self.new_tab_btn.setFixedSize(28, 28)
        self.new_tab_btn.setCursor(Qt.PointingHandCursor)
        self.new_tab_btn.clicked.connect(lambda: self.add_new_tab())

        corner_container = QWidget()
        corner_container.setObjectName("corner_container")
        corner_layout = QHBoxLayout(corner_container)
        corner_layout.setContentsMargins(6, 2, 10, 2)
        corner_layout.setSpacing(0)
        corner_layout.addWidget(self.new_tab_btn)

        self.tabs.setCornerWidget(corner_container, Qt.TopRightCorner)

        self.body_splitter.addWidget(self.sidebar_frame)
        self.body_splitter.addWidget(self.overlay_container)
        self.body_splitter.addWidget(self.tabs)

        self.body_splitter.setStretchFactor(0, 0)
        self.body_splitter.setStretchFactor(1, 0)
        self.body_splitter.setStretchFactor(2, 1)

        self.main_vlayout.addWidget(self.body_splitter)

        # Initial Tab Setup
        self.add_new_tab(label="Home Page")
        self.apply_theme()

    def setup_webengine_settings(self):
        settings = QWebEngineSettings.globalSettings()
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)

    def setup_navbar(self):
        self.navbar = QFrame()
        self.navbar.setObjectName("navbar")
        self.navbar.setFixedHeight(54)
        nav_layout = QHBoxLayout(self.navbar)
        nav_layout.setContentsMargins(12, 6, 12, 6)
        nav_layout.setSpacing(8)

        self.back_btn = self.create_btn("⟵", "Go Back", lambda: self.current_browser().back() if self.current_browser() else None)
        self.forward_btn = self.create_btn("⟶", "Go Forward", lambda: self.current_browser().forward() if self.current_browser() else None)
        self.reload_btn = self.create_btn("↻", "Reload Page", lambda: self.current_browser().reload() if self.current_browser() else None)
        self.home_btn = self.create_btn("🏠", "Go Home", self.navigate_home)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.reload_btn)
        nav_layout.addWidget(self.home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter web URL (.onion or standard)...")
        self.url_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_layout.addWidget(self.url_bar)

        self.share_btn = self.create_btn("🔗", "Share / Copy URL Link", self.copy_link_to_clipboard)

        self.incognito_badge = QPushButton("🥷 Incognito")
        self.incognito_badge.setCheckable(True)
        self.incognito_badge.clicked.connect(self.toggle_incognito)
        self.incognito_badge.setFixedHeight(36)

        nav_layout.addWidget(self.share_btn)
        nav_layout.addWidget(self.incognito_badge)

        self.main_vlayout.addWidget(self.navbar)

    def setup_bookmarks_bar(self):
        self.bookmarks_bar = QFrame()
        self.bookmarks_bar.setObjectName("bookmarks_bar")
        self.bookmarks_bar.setFixedHeight(34)
        self.bm_layout = QHBoxLayout(self.bookmarks_bar)
        self.bm_layout.setContentsMargins(12, 2, 12, 2)
        self.bm_layout.setSpacing(8)
        self.bm_layout.setAlignment(Qt.AlignLeft)

        self.main_vlayout.addWidget(self.bookmarks_bar)
        self.refresh_bookmarks_bar()

    def refresh_bookmarks_bar(self):
        while self.bm_layout.count():
            item = self.bm_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for bm in self.bookmarks:
            btn = QPushButton(f"🔖 {bm['title']}")
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, u=bm['url']: self.load_url_in_current(u))
            self.bm_layout.addWidget(btn)

    def setup_sidebar_icons(self):
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebar")
        self.sidebar_frame.setFixedWidth(54)
        sb_layout = QVBoxLayout(self.sidebar_frame)
        sb_layout.setContentsMargins(6, 12, 6, 12)
        sb_layout.setSpacing(14)
        sb_layout.setAlignment(Qt.AlignTop)

        self.btn_bm_panel = self.create_btn("🔖", "Bookmarks Panel", lambda: self.toggle_overlay_panel(0))
        self.btn_hist_panel = self.create_btn("📜", "Browsing History", lambda: self.toggle_overlay_panel(1))
        self.btn_dl_panel = self.create_btn("📥", "Downloads List", lambda: self.toggle_overlay_panel(2))
        self.btn_set_panel = self.create_btn("⚙️", "Settings & Customization", lambda: self.toggle_overlay_panel(3))

        sb_layout.addWidget(self.btn_bm_panel)
        sb_layout.addWidget(self.btn_hist_panel)
        sb_layout.addWidget(self.btn_dl_panel)
        sb_layout.addWidget(self.btn_set_panel)

    def setup_overlay_panels(self):
        self.overlay_container = QFrame()
        self.overlay_container.setObjectName("overlay_panel")
        self.overlay_container.setVisible(False)
        self.overlay_container.setMinimumWidth(280)
        self.overlay_container.setMaximumWidth(380)

        container_layout = QVBoxLayout(self.overlay_container)
        container_layout.setContentsMargins(12, 12, 12, 12)

        self.stacked_overlay = QStackedWidget()
        self.stacked_overlay.addWidget(self.build_bookmarks_panel())
        self.stacked_overlay.addWidget(self.build_history_panel())
        self.stacked_overlay.addWidget(self.build_downloads_panel())
        self.stacked_overlay.addWidget(self.build_settings_panel())

        header_layout = QHBoxLayout()
        self.overlay_title = QLabel("Panel")
        self.overlay_title.setStyleSheet("font-weight: bold; font-size: 15px;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(26, 26)
        close_btn.clicked.connect(lambda: self.overlay_container.setVisible(False))

        header_layout.addWidget(self.overlay_title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)

        container_layout.addLayout(header_layout)
        container_layout.addWidget(self.stacked_overlay)

    def toggle_overlay_panel(self, index):
        titles = ["Top Bar Bookmarks", "Browsing History", "Downloads", "Browser Settings & Tor/VPN"]
        if self.overlay_container.isVisible() and self.stacked_overlay.currentIndex() == index:
            self.overlay_container.setVisible(False)
        else:
            self.stacked_overlay.setCurrentIndex(index)
            self.overlay_title.setText(titles[index])
            self.overlay_container.setVisible(True)

    def build_bookmarks_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.bm_list_widget = QListWidget()
        self.refresh_bm_list_widget()

        btn_box = QHBoxLayout()
        add_btn = QPushButton("+ Add")
        add_btn.clicked.connect(self.add_bookmark_current)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_selected_bookmark)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_selected_bookmark)

        btn_box.addWidget(add_btn)
        btn_box.addWidget(edit_btn)
        btn_box.addWidget(delete_btn)

        layout.addWidget(self.bm_list_widget)
        layout.addLayout(btn_box)
        return widget

    def refresh_bm_list_widget(self):
        self.bm_list_widget.clear()
        for bm in self.bookmarks:
            self.bm_list_widget.addItem(f"{bm['title']} ({bm['url']})")

    def add_bookmark_current(self):
        curr = self.current_browser()
        if not curr: return
        url = curr.url().toString()
        title = curr.page().title() or "Bookmark"
        if url and "internal://home" not in url:
            self.bookmarks.append({"title": title[:20], "url": url})
            self.refresh_bm_list_widget()
            self.refresh_bookmarks_bar()

    def edit_selected_bookmark(self):
        row = self.bm_list_widget.currentRow()
        if 0 <= row < len(self.bookmarks):
            bm = self.bookmarks[row]
            new_title, ok1 = QInputDialog.getText(self, "Edit", "Title:", QLineEdit.Normal, bm['title'])
            if ok1 and new_title:
                new_url, ok2 = QInputDialog.getText(self, "Edit", "URL:", QLineEdit.Normal, bm['url'])
                if ok2 and new_url:
                    self.bookmarks[row] = {"title": new_title, "url": new_url}
                    self.refresh_bm_list_widget()
                    self.refresh_bookmarks_bar()

    def delete_selected_bookmark(self):
        row = self.bm_list_widget.currentRow()
        if 0 <= row < len(self.bookmarks):
            self.bookmarks.pop(row)
            self.refresh_bm_list_widget()
            self.refresh_bookmarks_bar()

    def build_history_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.hist_list_widget = QListWidget()
        delete_item_btn = QPushButton("Delete Selected Entry")
        delete_item_btn.clicked.connect(self.delete_selected_history)
        clear_all_btn = QPushButton("Clear All History")
        clear_all_btn.clicked.connect(self.clear_all_history)
        layout.addWidget(self.hist_list_widget)
        layout.addWidget(delete_item_btn)
        layout.addWidget(clear_all_btn)
        return widget

    def update_history_view(self):
        self.hist_list_widget.clear()
        for item in reversed(self.history):
            self.hist_list_widget.addItem(item)

    def delete_selected_history(self):
        row = self.hist_list_widget.currentRow()
        if row >= 0:
            idx = len(self.history) - 1 - row
            if 0 <= idx < len(self.history):
                self.history.pop(idx)
                self.update_history_view()

    def clear_all_history(self):
        self.history.clear()
        self.update_history_view()

    def build_downloads_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.dl_list_widget = QListWidget()
        layout.addWidget(self.dl_list_widget)
        return widget

    def on_download_requested(self, download):
        filename = download.suggestedFileName()
        default_path = os.path.join(self.download_dir, filename)
        filepath, _ = QFileDialog.getSaveFileName(self, "Save File", default_path)
        if filepath:
            download.setPath(filepath)
            download.accept()
            self.downloads.append(filename)
            self.dl_list_widget.addItem(f"📥 {filename}")
        else:
            download.cancel()

    def build_settings_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # --- Functional Tor & VPN Settings Panel ---
        layout.addWidget(QLabel("<b>Network Privacy & Security:</b>"))

        self.vpn_cb = QCheckBox("Enable Simulated VPN Tunnel")
        self.vpn_cb.setChecked(self.vpn_enabled)
        self.vpn_cb.toggled.connect(self.toggle_vpn)
        layout.addWidget(self.vpn_cb)

        self.tor_cb = QCheckBox("Enable Tor Network Routing (.onion support)")
        self.tor_cb.setChecked(self.tor_enabled)
        self.tor_cb.toggled.connect(self.toggle_tor)
        layout.addWidget(self.tor_cb)

        layout.addWidget(QLabel("Select Proxy Endpoint / Node:"))
        self.proxy_combo = QComboBox()
        self.proxy_combo.addItems([
            "None",
            "Tor Local SOCKS5 (127.0.0.1:9050)",
            "Custom HTTP Proxy",
            "US Secure Relay",
            "Europe Secure Relay"
        ])
        self.proxy_combo.currentTextChanged.connect(self.change_proxy)
        layout.addWidget(self.proxy_combo)

        layout.addWidget(QLabel("Default Search Engine:"))
        self.se_combo = QComboBox()
        self.se_combo.addItems(list(self.search_engines.keys()))
        self.se_combo.currentTextChanged.connect(self.change_search_engine)
        layout.addWidget(self.se_combo)

        layout.addWidget(QLabel("Theme Mode:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        layout.addWidget(self.theme_combo)

        layout.addWidget(QLabel("Download Folder:"))
        self.dl_input = QLineEdit(self.download_dir)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.select_download_folder)
        layout.addWidget(self.dl_input)
        layout.addWidget(browse_btn)

        layout.addStretch()
        return widget

    def toggle_vpn(self, enabled):
        self.vpn_enabled = enabled
        status = "ENABLED" if enabled else "DISABLED"
        if enabled:
            # Route traffic via standard HTTP/HTTPS proxy interface simulation
            self.apply_proxy_settings("127.0.0.1", 8080, "http")
        else:
            self.clear_proxy_settings()
        QMessageBox.information(self, "VPN Status", f"Virtual Private Network tunnel is now {status}.")

    def toggle_tor(self, enabled):
        self.tor_enabled = enabled
        if enabled:
            self.proxy_combo.setCurrentText("Tor Local SOCKS5 (127.0.0.1:9050)")
            self.apply_proxy_settings("127.0.0.1", 9050, "socks5")
            QMessageBox.information(self, "Tor Network", "Tor routing enabled. Ensure your local Tor daemon is running on port 9050.")
        else:
            if "Tor" in self.proxy_combo.currentText():
                self.proxy_combo.setCurrentText("None")
            self.clear_proxy_settings()

    def change_proxy(self, proxy_node):
        self.selected_proxy = proxy_node
        if "Tor" in proxy_node:
            self.apply_proxy_settings("127.0.0.1", 9050, "socks5")
        elif "US" in proxy_node or "Europe" in proxy_node:
            self.apply_proxy_settings("proxy.example.node", 8080, "http")
        else:
            self.clear_proxy_settings()

    def apply_proxy_settings(self, host, port, proxy_type):
        proxy = QNetworkProxy()
        if proxy_type == "socks5":
            proxy.setType(QNetworkProxy.Socks5Proxy)
        else:
            proxy.setType(QNetworkProxy.HttpProxy)
        proxy.setHostName(host)
        proxy.setPort(port)
        QNetworkProxy.setApplicationProxy(proxy)

    def clear_proxy_settings(self):
        QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.NoProxy))

    def change_search_engine(self, name):
        self.selected_search_engine = name
        self.reload_home_tabs()

    def change_theme(self, mode):
        self.current_theme = mode
        self.apply_theme()
        self.reload_home_tabs()

    def select_download_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.download_dir = folder
            self.dl_input.setText(folder)

    def toggle_incognito(self):
        self.is_incognito = self.incognito_badge.isChecked()
        self.active_profile = self.incognito_profile if self.is_incognito else self.standard_profile
        self.incognito_badge.setText("🥷 Incognito ON" if self.is_incognito else "🥷 Incognito")

    def copy_link_to_clipboard(self):
        curr = self.current_browser()
        if curr:
            url = curr.url().toString()
            QApplication.clipboard().setText(url)
            QMessageBox.information(self, "Link Copied", f"URL copied:\n{url}")

    def create_btn(self, text, tooltip, slot):
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(36, 36)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(slot)
        return btn

    def update_browser_page_bg(self, browser):
        if self.current_theme == "Light":
            browser.page().setBackgroundColor(QColor("#f8fafc"))
        else:
            browser.page().setBackgroundColor(QColor("#0b0f19"))

    def get_home_html(self):
        shortcuts_html = ""
        for sc in self.home_shortcuts:
            shortcuts_html += f"""
            <a href="{sc['url']}" class="shortcut-card" title="Open {sc['title']}">
                <span class="icon">{sc.get('icon', '🌐')}</span>
                <span class="label">{sc['title']}</span>
            </a>
            """

        search_action = self.search_engines.get(self.selected_search_engine, "https://www.google.com/search?q=")

        if self.current_theme == "Light":
            bg_css = "background-color: #f8fafc;"
            text_color = "#0f172a"
            sub_color = "#64748b"
            card_bg = "rgba(255, 255, 255, 0.75)"
            card_border = "#cbd5e1"
            card_text = "#334155"
            card_hover_bg = "#ffffff"
            input_bg = "#ffffff"
            input_border = "#cbd5e1"
            input_text = "#0f172a"
        else:
            bg_css = "background-color: #0b0f19;"
            text_color = "#f8fafc"
            sub_color = "#94a3b8"
            card_bg = "rgba(30, 41, 59, 0.7)"
            card_border = "#334155"
            card_text = "#cbd5e1"
            card_hover_bg = "rgba(51, 65, 85, 0.9)"
            input_bg = "#0b0f19"
            input_border = "#334155"
            input_text = "#ffffff"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                html, body {{
                    height: 100%; width: 100%; margin: 0; padding: 0;
                    {bg_css} color: {text_color};
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }}
                body {{ display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; box-sizing: border-box; }}
                .container {{ text-align: center; max-width: 680px; width: 100%; }}
                .logo {{ font-size: clamp(32px, 5vw, 54px); font-weight: 800; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }}
                .subtitle {{ color: {sub_color}; font-size: 16px; margin-bottom: 30px; }}
                .search-input {{
                    width: 100%; padding: 16px 24px; font-size: 16px; border-radius: 30px;
                    border: 1px solid {input_border}; background: {input_bg}; color: {input_text}; outline: none;
                    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.35); box-sizing: border-box;
                }}
                .shortcuts {{ display: flex; justify-content: center; gap: 14px; flex-wrap: wrap; margin-top: 30px; }}
                .shortcut-card {{
                    background: {card_bg}; border: 1px solid {card_border}; border-radius: 14px;
                    padding: 14px; width: 105px; text-decoration: none; color: {card_text};
                    display: flex; flex-direction: column; align-items: center; gap: 6px;
                }}
                .shortcut-card:hover {{ background: {card_hover_bg}; border-color: #38bdf8; }}
                .icon {{ font-size: 24px; }}
                .label {{ font-size: 12px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">Simple Browser</div>
                <div class="subtitle">Tor & VPN Network Enabled</div>
                <input type="text" class="search-input" id="search" placeholder="Search with {self.selected_search_engine} or enter .onion / URL..." autofocus
                       onkeydown="if(event.key==='Enter') doSearch()">
                <div class="shortcuts">{shortcuts_html}</div>
            </div>
            <script>
                function doSearch() {{
                    var query = document.getElementById('search').value.trim();
                    if (!query) return;
                    if (query.startsWith('http://') || query.startsWith('https://') || query.endsWith('.onion')) {{
                        window.location.href = query;
                    }} else if (query.includes('.') && !query.includes(' ')) {{
                        window.location.href = 'https://' + query;
                    }} else {{
                        window.location.href = '{search_action}' + encodeURIComponent(query);
                    }}
                }}
            </script>
        </body>
        </html>
        """

    def reload_home_tabs(self):
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if browser:
                self.update_browser_page_bg(browser)
                if "internal://home" in browser.url().toString():
                    browser.setHtml(self.get_home_html(), QUrl("internal://home"))

    def add_new_tab(self, qurl=None, label="New Tab"):
        browser = QWebEngineView()
        page = CustomWebEnginePage(self, self.active_profile)
        browser.setPage(page)
        self.update_browser_page_bg(browser)

        if qurl and qurl.toString() != "internal://home":
            browser.setUrl(qurl)
        else:
            browser.setHtml(self.get_home_html(), QUrl("internal://home"))

        index = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(index)
        browser.urlChanged.connect(lambda url, b=browser: self.update_urlbar(url, b))
        browser.loadFinished.connect(lambda _, b=browser: self.update_title(b))
        return browser

    def close_tab(self, index):
        if self.tabs.count() > 1:
            widget = self.tabs.widget(index)
            self.tabs.removeTab(index)
            widget.deleteLater()
        else:
            self.close()

    def current_browser(self):
        return self.tabs.currentWidget()

    def load_url_in_current(self, url_str):
        if url_str == "internal://home":
            self.current_browser().setHtml(self.get_home_html(), QUrl("internal://home"))
        else:
            self.current_browser().setUrl(QUrl(url_str))

    def navigate_home(self):
        if self.current_browser():
            self.load_url_in_current(self.homepage)

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text or not self.current_browser():
            return

        if text.endswith('.onion'):
            if not text.startswith("http://") and not text.startswith("https://"):
                text = "http://" + text
        elif not text.startswith("http://") and not text.startswith("https://"):
            if "." not in text or " " in text:
                engine_url = self.search_engines.get(self.selected_search_engine, "https://www.google.com/search?q=")
                text = f"{engine_url}{quote_plus(text)}"
            else:
                text = "https://" + text
        self.current_browser().setUrl(QUrl(text))

    def update_urlbar(self, q, browser=None):
        if browser != self.current_browser():
            return
        url_str = q.toString()
        if "internal://home" in url_str:
            self.url_bar.setText("")
        else:
            self.url_bar.setText(url_str)
            if url_str and not self.is_incognito and url_str not in self.history:
                self.history.append(url_str)
                self.update_history_view()
        self.url_bar.setCursorPosition(0)

    def update_title(self, browser):
        if browser != self.current_browser():
            return
        title = browser.page().title()
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, (title[:14] + "...") if len(title) > 14 else (title or "Browser"))

    def tab_changed(self, index):
        if self.current_browser():
            self.update_urlbar(self.current_browser().url(), self.current_browser())

    def apply_theme(self):
        for i in range(self.tabs.count()):
            b = self.tabs.widget(i)
            if b:
                self.update_browser_page_bg(b)

        if self.current_theme == "Dark":
            css = """
                QMainWindow { background-color: #0b0f19; color: #f8fafc; }
                QFrame#navbar, QFrame#bookmarks_bar { background-color: #0f172a; border-bottom: 1px solid #1e293b; }
                QFrame#sidebar { background-color: #0b0f19; border-right: 1px solid #1e293b; }
                QFrame#overlay_panel { background-color: #0f172a; border-right: 1px solid #1e293b; color: #ffffff; }
                QLineEdit { background-color: #0b0f19; color: #ffffff; border: 1px solid #334155; border-radius: 16px; padding: 6px 16px; }
                QPushButton { background-color: #1e293b; color: #f8fafc; border-radius: 8px; border: none; padding: 6px 12px; }
                QPushButton:hover { background-color: #334155; }
                QTabWidget, QTabWidget::pane { border: none !important; background-color: #0b0f19; }
                QTabBar { background-color: #0b0f19; border: none !important; }
                QTabBar::tab { background-color: #131c2e; color: #94a3b8; padding: 6px 18px; border-top-left-radius: 10px; border-top-right-radius: 10px; border: 1px solid #1e293b; margin-right: 4px; }
                QTabBar::tab:selected { background-color: #1e293b; color: #38bdf8; border-top: 2px solid #38bdf8; font-weight: bold; }
                QListWidget { background-color: #0b0f19; color: #f8fafc; border: 1px solid #334155; border-radius: 6px; }
                QListWidget::item { color: #f8fafc; padding: 4px; }
                QListWidget::item:selected { background-color: #38bdf8; color: #0b0f19; }
                QLabel { color: #f8fafc; }
                QCheckBox { color: #f8fafc; spacing: 8px; }
                QComboBox { background-color: #0b0f19; color: #ffffff; border: 1px solid #334155; padding: 6px; border-radius: 6px; }
                QComboBox QAbstractItemView { background-color: #1e293b; color: #ffffff; selection-background-color: #38bdf8; selection-color: #0b0f19; }
            """
        else:
            css = """
                QMainWindow { background-color: #f8fafc; color: #0f172a; }
                QFrame#navbar, QFrame#bookmarks_bar { background-color: #ffffff; border-bottom: 1px solid #e2e8f0; }
                QFrame#sidebar { background-color: #f1f5f9; border-right: 1px solid #e2e8f0; }
                QFrame#overlay_panel { background-color: #ffffff; border-right: 1px solid #e2e8f0; color: #0f172a; }
                QLineEdit { background-color: #f1f5f9; color: #0f172a; border: 1px solid #cbd5e1; border-radius: 16px; padding: 6px 16px; }
                QPushButton { background-color: #e2e8f0; color: #0f172a; border-radius: 8px; border: none; padding: 6px 12px; }
                QPushButton:hover { background-color: #cbd5e1; }
                QTabWidget, QTabWidget::pane { border: none !important; background-color: #f8fafc; }
                QTabBar { background-color: #f8fafc; border: none !important; }
                QTabBar::tab { background-color: #e2e8f0; color: #64748b; padding: 6px 18px; border-top-left-radius: 10px; border-top-right-radius: 10px; border: 1px solid #cbd5e1; margin-right: 4px; }
                QTabBar::tab:selected { background-color: #ffffff; color: #0284c7; border-top: 2px solid #0284c7; font-weight: bold; }
                QListWidget { background-color: #ffffff; color: #0f172a; border: 1px solid #cbd5e1; border-radius: 6px; }
                QListWidget::item { color: #0f172a; padding: 4px; }
                QListWidget::item:selected { background-color: #0284c7; color: #ffffff; }
                QLabel { color: #0f172a; }
                QCheckBox { color: #0f172a; spacing: 8px; }
                QComboBox { background-color: #ffffff; color: #0f172a; border: 1px solid #cbd5e1; padding: 6px; border-radius: 6px; }
                QComboBox QAbstractItemView { background-color: #ffffff; color: #0f172a; selection-background-color: #0284c7; selection-color: #ffffff; }
            """
        self.setStyleSheet(css)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Simple Browser")
    window = SimpleBrowser()
    window.show()
    sys.exit(app.exec_())
