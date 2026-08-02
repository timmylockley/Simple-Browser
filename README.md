Simple Browser 🚀🌐
===================

A lightweight, feature-rich, and modern custom web browser built using **Python**, **PyQt5**, and **QtWebEngine**. Designed with a sleek dark/light user interface, split-pane history/bookmarks panels, tab management, incognito mode, and custom search engines.

✨ Features
----------

*   **Modern & Clean UI**: Fusion-styled interface with support for dynamic Dark and Light themes.
    
*   **Multi-Tab Browsing**: Fully dynamic tab management with sleek custom close buttons, drag-and-drop tab reordering, and a quick-add + tab bar action.
    
*   **Side Overlay Panels**: Easily slide open dedicated panels for **Bookmarks**, **Browsing History**, **Downloads Management**, and **Settings**.
    
*   **Incognito / Private Browsing**: Isolated browsing profile that doesn't record session history.
    
*   **Custom Homepage & Shortcuts**: Interactive home dashboard supporting customizable quick-launch shortcut cards (Google, GitHub, YouTube, Reddit, etc.).
    
*   **Multiple Search Engines**: Seamlessly switch between Google, DuckDuckGo, Bing, and Brave directly from the settings panel.
    
*   **Download Manager**: Real-time download prompt dialogs tracking files saved to your designated directory.
    

🛠️ System Requirements & Constraints
-------------------------------------

*   **Operating System**: macOS, Linux, or Windows.
    
*   **Python**: Version 3.8 or higher.
    
*   **QtWebEngine Dependency**:
    
    *   _Note on JavaScript & Modern Web Standards_: PyQt5's QtWebEngine relies on an embedded Chromium runtime instance. If you run into JavaScript errors like crypto.randomUUID is not a function, .at() is not a function, or structuredClone is not defined, it means your local system installation of PyQt5 is bound to an older Chromium version. Updating PyQt5 to its latest stable release (pip install --upgrade PyQt5 PyQt5-WebEngine) will pull the newest available browser core for your environment.
        
    *   _WebGL Blocklisting_: On some macOS hardware configurations, macOS graphics sandboxing may blocklist default hardware-accelerated WebGL. The application handles this via software fallbacks (--disable-gpu-rasterization), but high-performance 3D graphics/WebGL content might run on software-rendering mode.
        
    *   _Tor (.onion) Networks_: To access .onion links, a local SOCKS5 proxy daemon (such as the official Tor background service) must be actively running on your machine (typically at 127.0.0.1:9050).
        

📦 Installation & Setup
-----------------------

Follow these steps to set up and run the browser locally on your machine:

### 1\. Clone the Repository

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   git clone https://github.com/your-username/simple-browser.git  cd simple-browser   `

### 2\. Create a Virtual Environment (Recommended)

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python3 -m venv venv  source venv/bin/activate  # On Windows use: venv\Scripts\activate   `

### 3\. Install Dependencies

Install the required PyQt5 and WebEngine packages via pip:

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   pip install PyQt5 PyQt5-WebEngine   `

_(Optional)_ If you need to ensure you have the latest patch releases compatible with your system architecture:

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   pip install --upgrade PyQt5 PyQt5-WebEngine   `

### Or:
1. Install the .deb
2. Curl using this link: curl -sSL https://raw.githubusercontent.com/timmylockley/Simple-Browser/main/simple_browser_install.sh | bash
   
🚀 Usage
--------

Run the browser script from your terminal:

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python3 simple_browser.py   `

### Navigating the Interface:

*   **Address Bar**: Type standard URLs (e.g., https://github.com) or keywords to search using your preferred search engine.
    
*   **Sidebar Icons**:
    
    *   🔖 **Bookmarks**: Manage and jump to saved pages.
        
    *   📜 **History**: Review or clear your browsing session history.
        
    *   📥 **Downloads**: View tracked files downloaded during your session.
        
    *   ⚙️ **Settings**: Toggle themes, manage home screen shortcuts, change default search engines, and configure download directories.
        
*   **Incognito Mode**: Click the **🥷 Incognito** badge on the navigation bar to launch private browsing sessions.
    

📂 Project Structure
--------------------

Plaintext

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   simple-browser/  │  ├── simple_browser.py      # Main application source code  ├── README.md              # Project documentation  └── venv/                  # Python virtual environment (ignored in git)   `

🤝 Contributing
---------------

Contributions, bug reports, and feature requests are welcome! Feel free to check out the [issues page](https://www.google.com/search?q=https://github.com/your-username/simple-browser/issues).

1.  Fork the Project
    
2.  Create your Feature Branch (git checkout -b feature/AmazingFeature)
    
3.  Commit your Changes (git commit -m 'Add some AmazingFeature')
    
4.  Push to the Branch (git push origin feature/AmazingFeature)
    
5.  Open a Pull Request
    

📝 License
----------

Distributed under the MIT License. See LICENSE for more information.
