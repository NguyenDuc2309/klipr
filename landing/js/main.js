/**
 * Klipr Landing Page JavaScript
 * Multi-language (EN / VI), Release Fetching, Copy Toasts, Lightbox, and FAQ Accordions.
 */

// i18n Translations Dictionary
const translations = {
    en: {
        'nav.features': 'Features',
        'nav.screenshots': 'Screenshots',
        'nav.install': 'Install',
        'nav.faq': 'FAQ',
        'nav.star': 'Star on GitHub',

        'hero.release_suffix': '— Latest Release',
        'hero.title': 'Clipboard history,<br><span class="gradient-text">made seamless for Linux.</span>',
        'hero.desc': 'Klipr captures everything you copy — text, code, commands, and screenshots. Native GTK4 desktop integration, zero Electron bloat, and instant fuzzy search.',
        'hero.download_deb': 'Download .deb',
        'hero.install_guide': 'Install Guide',
        'hero.trust_free': '100% Free Forever &bull; No Ads &bull; No Subscriptions &bull; Zero Telemetry',
        'hero.pill_free': '100% Free & Open Source',
        'hero.pill_gtk': 'Native GTK4 (~41MB RAM idle)',
        'hero.pill_privacy': '100% Offline & Private',
        'hero.pill_no_account': 'No Account Required',

        'promise.tag': '100% Free & Open Source',
        'promise.title': 'Free forever without catches or compromises',
        'promise.subtitle': 'Klipr is built as an open utility for the Linux community. No paywalls, no monetization, no tracking.',
        'promise.c1_title': '100% Free Forever ($0)',
        'promise.c1_desc': 'No paid tiers, no pro subscriptions, and no locked features. Everything is free for everyone.',
        'promise.c2_title': 'Zero Advertisements',
        'promise.c2_desc': 'No sponsored banners, no upgrade prompts, and no annoying popups. Clean and focused.',
        'promise.c3_title': '100% Offline & Private',
        'promise.c3_desc': 'All snippets and history remain strictly on your local disk. Nothing is uploaded to any cloud server.',
        'promise.c4_title': 'Permissive MIT License',
        'promise.c4_desc': 'Free for both personal and commercial use. Inspect, modify, or fork the full codebase on GitHub.',

        'showcase.tag': 'App Showcase',
        'showcase.title': 'Clean, focused GTK4 interface',
        'showcase.subtitle': 'Fits right at home on modern Linux desktop environments including GNOME, XFCE, and KDE.',
        'showcase.window1_title': 'Klipr — History & Favorites',
        'showcase.window1_caption': 'Clipboard History with Thumbnail Previews',
        'showcase.window2_title': 'Klipr — Settings & Customization',
        'showcase.window2_caption': 'Themes, Global Hotkeys & Tray Settings',
        'showcase.zoom': 'Click to Zoom',

        'features.tag': 'Features',
        'features.title': 'Built for daily developer productivity',
        'features.subtitle': 'Everything you need to effortlessly manage clipboard history without bloat.',
        'features.f1_title': 'Automatic History',
        'features.f1_desc': 'Quietly records snippets and automatically prunes older items based on your configured limit.',
        'features.f2_title': 'Instant Fuzzy Search',
        'features.f2_desc': 'Search across your entire clipboard history with zero input latency and full multilingual IME support.',
        'features.f3_title': 'Pinned Favorites',
        'features.f3_desc': 'Bookmark recurring commands, passwords, or snippets. Pinned items are protected from auto-pruning.',
        'features.f4_title': 'Image & Screenshot Capture',
        'features.f4_desc': 'Preserves copied images and screenshots with instant thumbnail previews and one-click paste back.',
        'features.f5_title': 'Dark, Light & System',
        'features.f5_desc': 'Seamlessly synchronizes with your Linux desktop theme or choose your preferred look manually.',
        'features.f6_title': 'Pure Native Performance',
        'features.f6_desc': 'Built with Python and GTK4. Tiny memory footprint that runs silently in the system tray.',


        'install.title': 'Install Klipr in Seconds',
        'install.subtitle': 'Choose your preferred installation method below:',
        'install.tab_deb': 'Ubuntu / Debian (.deb) (Recommended)',
        'install.tab_apt': 'APT Repository',
        'install.tab_source': 'Build from Source',
        'install.tab_config': 'Settings Config',
        'install.note_apt': 'Adds Klipr\'s self-hosted, signed APT repository. Future releases arrive through `sudo apt upgrade` like any other package.',
        'install.note_deb_prefix': 'Download the latest release package directly from',
        'install.note_source': 'Requires Python 3.10+, GTK4, and PyGObject (`gir1.2-gtk-4.0`).',
        'install.note_config': 'Configure `historyLimit`, `theme`, `autostart`, and custom `shortcut` keys.',

        'faq.tag': 'FAQ',
        'faq.title': 'Frequently Asked Questions',
        'faq.subtitle': 'Quick answers to common questions about Klipr.',
        'faq.q0': 'Is Klipr really 100% free? Are there any hidden fees or Pro tiers?',
        'faq.a0': 'Yes. Klipr is free and open source under the MIT license — no paid tiers, no subscriptions, no ads, and no locked features. Free for personal and commercial use.',
        'faq.q1': 'Which Linux distributions and desktops are supported?',
        'faq.a1': 'Klipr ships as a `.deb` for Ubuntu 22.04+, Debian 12+, Linux Mint and Pop!_OS, and runs from source on any distro with Python 3.10+, GTK4 and PyGObject. Note that it runs on X11 only — on a Wayland session it launches through XWayland.',
        'faq.q2': 'Is my clipboard data sent anywhere?',
        'faq.a2': 'No. Klipr contains no networking code at all — nothing is uploaded, and there is no telemetry or tracking. History lives in a local SQLite file at `~/.local/share/klipr/clipboard.db`. Be aware that, like most clipboard managers, this file is not encrypted, so treat it as you would any other file in your home directory.',
        'faq.q3': 'Can I change the global toggle shortcut?',
        'faq.a3': 'Yes, from the in-app Settings dialog, or by editing the `"shortcut"` field in `~/.config/klipr/setting.json` (default: `Ctrl+Alt+M`). The hotkey is registered as a GNOME custom keybinding, so on non-GNOME desktops you will need to bind the `klipr --toggle` command yourself in your desktop\'s keyboard settings.',
        'faq.q4': 'How many items does Klipr keep?',
        'faq.a4': 'The Settings dialog offers a history limit of 50, 100 or 150 items. Once the limit is reached, the oldest entries are pruned automatically as new ones arrive.',
        'faq.q5': 'Are my pinned favorites deleted when the history fills up?',
        'faq.a5': 'No. Favorites are stored in a separate table that automatic pruning never touches, so a pinned snippet stays until you remove it yourself.',
        'faq.q6': 'How are copied images stored?',
        'faq.a6': 'Copied images are written as PNG files to `~/.cache/klipr/images/` and referenced from the history database. Identical images are de-duplicated by content hash, and the list shows a downscaled thumbnail rather than holding the full-resolution image in memory. Files are deleted once no history entry or favorite references them.',
        'faq.q7': 'The tray icon does not appear — what is wrong?',
        'faq.a7': 'Klipr implements the StatusNotifierItem (SNI) tray protocol, which needs a tray host on your desktop. KDE Plasma, XFCE, Cinnamon and MATE support it out of the box; on GNOME install `gnome-shell-extension-appindicator` and enable it. You can still open the window with the global shortcut or by running `klipr --toggle`.',
        'faq.q8': 'Does closing the window quit Klipr?',
        'faq.a8': 'No. By default closing the window hides it to the tray so clipboard capture keeps running. Turn off "Close to tray" in Settings if you would rather have the window close quit the app; you can always quit from the tray menu.',

        'footer.crafted': 'Klipr &bull; Crafted with passion by',
        'footer.free_note': '100% Free &amp; Open Source forever under the MIT License.',
        'footer.repo': 'GitHub Repository',
        'footer.releases': 'Releases',
        'footer.license': 'MIT License',

        'toast.copied': 'Copied to clipboard!',
        'toast.failed': 'Failed to copy. Please copy manually.'
    },
    vi: {
        'nav.features': 'Tính năng',
        'nav.screenshots': 'Giao diện',
        'nav.install': 'Cài đặt',
        'nav.faq': 'Hỏi đáp',
        'nav.star': 'Star trên GitHub',

        'hero.release_suffix': '— Bản phát hành mới nhất',
        'hero.title': 'Quản lý lịch sử clipboard,<br><span class="gradient-text">mượt mà cho Linux.</span>',
        'hero.desc': 'Klipr tự động lưu lại mọi nội dung bạn sao chép — văn bản, mã nguồn, lệnh terminal và ảnh chụp màn hình. Tích hợp GTK4 native, không dùng Electron nặng nề, tìm kiếm siêu nhanh.',
        'hero.download_deb': 'Tải gói .deb',
        'hero.install_guide': 'Hướng dẫn cài đặt',
        'hero.trust_free': '100% Miễn phí vĩnh viễn &bull; Không quảng cáo &bull; Không gói trả phí &bull; Không thu thập dữ liệu',
        'hero.pill_free': '100% Miễn phí & Mã nguồn mở',
        'hero.pill_gtk': 'GTK4 Native (~41MB RAM khi rảnh)',
        'hero.pill_privacy': '100% Offline & Bảo mật',
        'hero.pill_no_account': 'Không cần tài khoản',

        'promise.tag': 'Cam kết Miễn phí 100%',
        'promise.title': 'Miễn phí thực sự, không bẫy trả phí',
        'promise.subtitle': 'Klipr được xây dựng như một công cụ hữu ích hoàn toàn miễn phí phục vụ cộng đồng Linux.',
        'promise.c1_title': 'Miễn phí vĩnh viễn ($0)',
        'promise.c1_desc': 'Không có bản Pro, không thu phí bản quyền, không khóa tính năng. Mọi tính năng đều miễn phí cho tất cả mọi người.',
        'promise.c2_title': 'Không quảng cáo',
        'promise.c2_desc': 'Không pop-up mời nâng cấp, không banner quảng cáo, không làm phiền trải nghiệm làm việc của bạn.',
        'promise.c3_title': '100% Offline & Bảo mật',
        'promise.c3_desc': 'Toàn bộ nội dung sao chép lưu trữ nội bộ trên máy bạn. Tuyệt đối không gửi dữ liệu lên bất kỳ máy chủ nào.',
        'promise.c4_title': 'Mã nguồn mở MIT',
        'promise.c4_desc': 'Hoàn toàn tự do sử dụng cho cá nhân lẫn thương mại. Thoải mái kiểm tra, chỉnh sửa mã nguồn trên GitHub.',

        'showcase.tag': 'Giao diện',
        'showcase.title': 'Thiết kế GTK4 tinh tế & gọn gàng',
        'showcase.subtitle': 'Hoạt động hoàn hảo trên các môi trường desktop Linux hiện đại như GNOME, XFCE và KDE.',
        'showcase.window1_title': 'Klipr — Lịch sử & Yêu thích',
        'showcase.window1_caption': 'Lịch sử clipboard kèm hình ảnh thumbnail trực quan',
        'showcase.window2_title': 'Klipr — Cài đặt & Tùy biến',
        'showcase.window2_caption': 'Tùy biến giao diện Sáng/Tối, phím tắt & khay hệ thống',
        'showcase.zoom': 'Bấm để phóng to',

        'features.tag': 'Tính năng',
        'features.title': 'Tối ưu cho hiệu suất làm việc mỗi ngày',
        'features.subtitle': 'Mọi thứ bạn cần để quản lý nội dung clipboard mà không gây nặng máy.',
        'features.f1_title': 'Lưu trữ tự động',
        'features.f1_desc': 'Âm thầm ghi nhớ các đoạn văn bản, tự động dọn dẹp các mục cũ theo giới hạn bạn đặt.',
        'features.f2_title': 'Tìm kiếm tức thì',
        'features.f2_desc': 'Tìm kiếm nhanh chóng trong toàn bộ lịch sử với độ trễ bằng 0, hỗ trợ tốt gõ tiếng Việt (IME).',
        'features.f3_title': 'Ghim mục yêu thích',
        'features.f3_desc': 'Đánh dấu các lệnh hay dùng hoặc ghi chú quan trọng. Các mục ghim không bao giờ bị xóa tự động.',
        'features.f4_title': 'Lưu ảnh & Ảnh chụp màn hình',
        'features.f4_desc': 'Giữ lại các hình ảnh đã copy với thumbnail xem trước, dán lại chỉ với 1 click chuột.',
        'features.f5_title': 'Dark, Light & Theo hệ thống',
        'features.f5_desc': 'Tự động đồng bộ theo giao diện Sáng/Tối của Linux hoặc tùy chọn thủ công theo sở thích.',
        'features.f6_title': 'Hiệu năng Native vượt trội',
        'features.f6_desc': 'Viết bằng Python và GTK4. Chiếm cực ít bộ nhớ RAM và chạy ẩn trên khay hệ thống.',


        'install.title': 'Cài đặt Klipr dễ dàng',
        'install.subtitle': 'Chọn phương thức cài đặt phù hợp với bạn bên dưới:',
        'install.tab_deb': 'Ubuntu / Debian (.deb) (Khuyên dùng)',
        'install.tab_apt': 'Kho APT',
        'install.tab_source': 'Build từ mã nguồn',
        'install.tab_config': 'Tùy chỉnh cài đặt',
        'install.note_apt': 'Thêm kho APT tự lưu trữ, có ký số của Klipr. Các bản cập nhật sau này sẽ tới qua `sudo apt upgrade` như mọi package khác.',
        'install.note_deb_prefix': 'Tải gói phát hành trực tiếp từ',
        'install.note_source': 'Yêu cầu Python 3.10+, GTK4 và PyGObject (`gir1.2-gtk-4.0`).',
        'install.note_config': 'Tùy chỉnh `historyLimit`, `theme`, `autostart` và phím tắt `shortcut` theo ý muốn.',

        'faq.tag': 'Hỏi & Đáp',
        'faq.title': 'Câu hỏi thường gặp',
        'faq.subtitle': 'Giải đáp nhanh các thắc mắc phổ biến về Klipr.',
        'faq.q0': 'Klipr có thực sự miễn phí 100% không? Có phí ẩn hay bản Pro không?',
        'faq.a0': 'Có. Klipr miễn phí và mã nguồn mở theo giấy phép MIT — không có bản trả phí, không thuê bao, không quảng cáo, không khoá tính năng. Dùng thoải mái cho cả cá nhân lẫn thương mại.',
        'faq.q1': 'Klipr hỗ trợ những bản phân phối và desktop nào?',
        'faq.a1': 'Klipr đóng gói `.deb` cho Ubuntu 22.04+, Debian 12+, Linux Mint và Pop!_OS, đồng thời chạy được từ mã nguồn trên mọi distro có Python 3.10+, GTK4 và PyGObject. Lưu ý app chỉ chạy trên X11 — nếu bạn đang dùng phiên Wayland thì nó chạy thông qua XWayland.',
        'faq.q2': 'Dữ liệu clipboard của tôi có bị gửi đi đâu không?',
        'faq.a2': 'Không. Klipr hoàn toàn không có mã kết nối mạng — không gửi gì lên đâu, không thu thập dữ liệu. Lịch sử nằm trong file SQLite cục bộ tại `~/.local/share/klipr/clipboard.db`. Cần lưu ý file này không được mã hoá (giống hầu hết app clipboard khác), nên hãy đối xử với nó như mọi file khác trong thư mục home.',
        'faq.q3': 'Tôi đổi được phím tắt mở nhanh không?',
        'faq.a3': 'Được, đổi trong bảng Cài đặt của app hoặc sửa trường `"shortcut"` trong `~/.config/klipr/setting.json` (mặc định `Ctrl+Alt+M`). Phím tắt được đăng ký dưới dạng custom keybinding của GNOME, nên trên desktop không phải GNOME bạn cần tự gán lệnh `klipr --toggle` trong cài đặt bàn phím của desktop đó.',
        'faq.q4': 'Klipr lưu được bao nhiêu mục?',
        'faq.a4': 'Bảng Cài đặt cho chọn giới hạn 50, 100 hoặc 150 mục. Khi đạt giới hạn, các mục cũ nhất sẽ tự động bị xoá bớt khi có mục mới.',
        'faq.q5': 'Mục đã ghim có bị xoá khi lịch sử đầy không?',
        'faq.a5': 'Không. Mục yêu thích được lưu ở bảng riêng mà cơ chế tự động dọn không bao giờ đụng tới, nên đã ghim là còn cho tới khi bạn tự xoá.',
        'faq.q6': 'Ảnh sao chép được lưu như thế nào?',
        'faq.a6': 'Ảnh sao chép được ghi thành file PNG trong `~/.cache/klipr/images/` và được tham chiếu từ cơ sở dữ liệu lịch sử. Ảnh trùng nhau được khử trùng lặp bằng mã băm nội dung, và danh sách chỉ hiển thị ảnh thu nhỏ thay vì giữ ảnh gốc trong bộ nhớ. File sẽ được xoá khi không còn mục lịch sử hay mục yêu thích nào tham chiếu tới.',
        'faq.q7': 'Không thấy biểu tượng ở khay hệ thống thì sao?',
        'faq.a7': 'Klipr dùng giao thức khay StatusNotifierItem (SNI), giao thức này cần desktop có sẵn tray host. KDE Plasma, XFCE, Cinnamon và MATE hỗ trợ sẵn; riêng GNOME cần cài `gnome-shell-extension-appindicator` rồi bật lên. Trong lúc đó bạn vẫn mở được cửa sổ bằng phím tắt hoặc lệnh `klipr --toggle`.',
        'faq.q8': 'Đóng cửa sổ thì Klipr có thoát hẳn không?',
        'faq.a8': 'Không. Mặc định đóng cửa sổ chỉ ẩn xuống khay để việc ghi nhận clipboard vẫn tiếp tục. Nếu muốn đóng là thoát hẳn, tắt tuỳ chọn "Close to tray" trong Cài đặt; bạn cũng luôn có thể thoát từ menu ở khay.',

        'footer.crafted': 'Klipr &bull; Phát triển bởi',
        'footer.free_note': '100% Miễn phí &amp; Mã nguồn mở vĩnh viễn theo giấy phép MIT.',
        'footer.repo': 'Kho mã nguồn GitHub',
        'footer.releases': 'Các bản phát hành',
        'footer.license': 'Giấy phép MIT',

        'toast.copied': 'Đã sao chép vào bộ nhớ tạm!',
        'toast.failed': 'Không thể sao chép. Vui lòng sao chép thủ công.'
    }
};

function safeGetStorage(key, fallback) {
    try {
        return localStorage.getItem(key) || fallback;
    } catch (e) {
        return fallback;
    }
}

function safeSetStorage(key, val) {
    try {
        localStorage.setItem(key, val);
    } catch (e) {}
}

let currentLang = safeGetStorage('klipr_lang', 'en');
let currentReleaseTag = 'v1.2.4';

/**
 * Public function to set language
 */
window.setLanguage = function(lang) {
    if (!translations[lang]) return;
    currentLang = lang;
    safeSetStorage('klipr_lang', lang);
    document.documentElement.lang = lang;

    if (lang === 'vi') {
        document.title = 'Klipr — Quản lý lịch sử Clipboard cho Linux (100% Miễn phí & GTK4 Native)';
    } else {
        document.title = 'Klipr — 100% Free, Native GTK4 Clipboard History for Linux';
    }

    // Update active button state
    document.querySelectorAll('.lang-btn').forEach(btn => {
        if (btn.getAttribute('data-lang') === lang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Translate all elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key] !== undefined) {
            el.innerHTML = translations[lang][key];
        }
    });

    // Update version badge
    updateVersionBadge();
};

function updateVersionBadge() {
    const badge = document.getElementById('latest-version-badge');
    if (badge) {
        const suffix = (translations[currentLang] && translations[currentLang]['hero.release_suffix']) || '— Latest Release';
        badge.textContent = `${currentReleaseTag} ${suffix}`;
    }
}

// Initialize on DOM ready
function init() {
    window.setLanguage(currentLang);
    initScrollReveal();
    initNavbarScroll();
    initCopyButtons();
    initLightbox();
    initInstallTabs();
    initFaqAccordion();
    initBackToTop();
    fetchLatestRelease();

    // Attach click listeners to language buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const lang = btn.getAttribute('data-lang');
            if (lang) window.setLanguage(lang);
        });
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

/**
 * Scroll Reveal Animations
 */
function initScrollReveal() {
    const revealElements = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) {
        revealElements.forEach(el => el.classList.add('active'));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -30px 0px'
    });

    revealElements.forEach(el => observer.observe(el));
}

/**
 * Navbar Background Styling on Scroll
 */
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 20) {
            navbar.style.background = 'rgba(7, 10, 15, 0.92)';
            navbar.style.borderColor = 'rgba(255, 255, 255, 0.12)';
        } else {
            navbar.style.background = 'rgba(7, 10, 15, 0.75)';
            navbar.style.borderColor = 'var(--border-subtle)';
        }
    }, { passive: true });
}

/**
 * Copy to Clipboard Handlers
 */
function initCopyButtons() {
    const copyBlocks = document.querySelectorAll('[data-copy]');
    
    copyBlocks.forEach(block => {
        block.addEventListener('click', async (e) => {
            e.stopPropagation();
            const textToCopy = block.getAttribute('data-copy');
            if (!textToCopy) return;

            try {
                await navigator.clipboard.writeText(textToCopy);
                const msg = (translations[currentLang] && translations[currentLang]['toast.copied']) || 'Copied to clipboard!';
                showToast(msg);
                
                const btn = block.querySelector('.copy-btn');
                if (btn) {
                    const originalHTML = btn.innerHTML;
                    btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3fb950" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
                    setTimeout(() => {
                        btn.innerHTML = originalHTML;
                    }, 2000);
                }
            } catch (err) {
                console.error('Failed to copy:', err);
                const failMsg = (translations[currentLang] && translations[currentLang]['toast.failed']) || 'Failed to copy. Please copy manually.';
                showToast(failMsg);
            }
        });
    });
}

/**
 * Toast Notification System
 */
function showToast(message) {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Installation Options Tab Switcher
 */
function initInstallTabs() {
    const tabBtns = document.querySelectorAll('.install-tab-btn');
    const panels = document.querySelectorAll('.install-panel');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetId = btn.getAttribute('data-install-target');
            const targetPanel = document.getElementById(targetId);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

/**
 * FAQ Accordion Handlers
 */
function initFaqAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const questionBtn = item.querySelector('.faq-question');
        if (questionBtn) {
            questionBtn.addEventListener('click', () => {
                const isActive = item.classList.contains('active');
                faqItems.forEach(i => i.classList.remove('active'));
                if (!isActive) {
                    item.classList.add('active');
                }
            });
        }
    });
}

/**
 * Back to Top Floating Button
 */
function initBackToTop() {
    const btn = document.getElementById('back-to-top');
    if (!btn) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            btn.classList.add('visible');
        } else {
            btn.classList.remove('visible');
        }
    }, { passive: true });

    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

/**
 * Screenshot Lightbox Viewer
 */
function initLightbox() {
    const frames = document.querySelectorAll('.window-frame');
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxClose = document.getElementById('lightbox-close');

    if (!lightbox || !lightboxImg) return;

    frames.forEach(frame => {
        frame.addEventListener('click', () => {
            const img = frame.querySelector('.window-img');
            if (img) {
                lightboxImg.src = img.src;
                lightboxImg.alt = img.alt || 'Screenshot Preview';
                lightbox.classList.add('active');
            }
        });
    });

    const closeLightbox = () => {
        lightbox.classList.remove('active');
    };

    if (lightboxClose) {
        lightboxClose.addEventListener('click', closeLightbox);
    }

    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && lightbox.classList.contains('active')) {
            closeLightbox();
        }
    });
}

/**
 * Dynamic GitHub Release Fetching
 */
async function fetchLatestRelease() {
    const repo = 'NguyenDuc2309/klipr';
    const downloadBtn = document.getElementById('download-deb-btn');
    const installCmdBlock = document.getElementById('install-code-box');
    const installCmdText = document.getElementById('install-cmd-text');
    const releaseLink = document.getElementById('release-link');

    try {
        const response = await fetch(`https://api.github.com/repos/${repo}/releases/latest`);
        if (!response.ok) return;

        const release = await response.json();
        currentReleaseTag = release.tag_name || 'v1.2.4';
        updateVersionBadge();

        if (releaseLink && release.html_url) {
            releaseLink.href = release.html_url;
        }

        const debAsset = release.assets?.find(asset => asset.name.endsWith('.deb'));
        if (debAsset) {
            if (downloadBtn) {
                downloadBtn.href = debAsset.browser_download_url;
                downloadBtn.setAttribute('title', `Download ${debAsset.name}`);
            }

            const installCmd = `sudo apt install ./${debAsset.name}`;
            if (installCmdBlock) {
                installCmdBlock.setAttribute('data-copy', installCmd);
            }
            if (installCmdText) {
                installCmdText.textContent = installCmd;
            }
        }
    } catch (error) {
        console.info('Using fallback release metadata:', error);
    }
}
