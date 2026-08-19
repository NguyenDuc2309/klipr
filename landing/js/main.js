/**
 * Klipr Landing Page JavaScript
 * Multi-language (EN / VI), Release Fetching, Copy Toasts, Lightbox, and FAQ Accordions.
 */

// i18n Translations Dictionary
const translations = {
    en: {
        'nav.features': 'Features',
        'nav.screenshots': 'Screenshots',
        'nav.comparison': 'Why Klipr',
        'nav.install': 'Install',
        'nav.faq': 'FAQ',
        'nav.star': 'Star on GitHub',

        'hero.release_suffix': '— Latest Release',
        'hero.title': 'Clipboard history,<br><span class="gradient-text">made seamless for Linux.</span>',
        'hero.desc': 'Klipr captures everything you copy — text, code, commands, and screenshots. Native GTK4 desktop integration, zero Electron bloat, and instant fuzzy search.',
        'hero.download_deb': 'Download .deb',
        'hero.install_guide': 'Install Guide',
        'hero.pill_gtk': 'Native GTK4',
        'hero.pill_ram': '< 35MB RAM Usage',
        'hero.pill_privacy': '100% Offline & Private',
        'hero.pill_mit': 'MIT Open Source',

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

        'comparison.tag': 'Benchmark',
        'comparison.title': 'Why Developers Choose Klipr',
        'comparison.subtitle': 'Say goodbye to 400MB Electron clipboard utilities.',
        'comparison.th_metric': 'Feature / Metric',
        'comparison.th_klipr': 'Klipr (Native GTK4)',
        'comparison.th_electron': 'Electron-Based Apps',
        'comparison.th_standard': 'Standard Linux Clipboards',
        'comparison.r1_metric': 'RAM Consumption',
        'comparison.r2_metric': 'Launch & Hotkey Latency',
        'comparison.r2_val1': '< 0.15s (Instant)',
        'comparison.r3_metric': 'Image & Screenshot History',
        'comparison.r3_val1': '✓ Full Thumbnails',
        'comparison.r3_val2': '✓ Supported',
        'comparison.r3_val3': '✕ Text Only (Mostly)',
        'comparison.r4_metric': 'Pinned Favorites System',
        'comparison.r4_val1': '✓ Permanent Pinning',
        'comparison.r4_val2': '✓ Supported',
        'comparison.r4_val3': '✕ Limited',
        'comparison.r5_metric': 'Telemetry & Privacy',
        'comparison.r5_val1': '✓ 100% Offline & Safe',
        'comparison.r5_val2': 'Varies / Often Tracked',
        'comparison.r5_val3': '✓ Offline',
        'comparison.r6_metric': 'License',
        'comparison.r6_val1': 'MIT Open Source',
        'comparison.r6_val2': 'Proprietary / Open',
        'comparison.r6_val3': 'Open Source',

        'install.title': 'Install Klipr in Seconds',
        'install.subtitle': 'Choose your preferred installation method below:',
        'install.tab_deb': 'Ubuntu / Debian (.deb)',
        'install.tab_source': 'Build from Source',
        'install.tab_config': 'Settings Config',
        'install.note_deb_prefix': 'Download the latest release package directly from',
        'install.note_source': 'Requires Python 3.10+, GTK4, and PyGObject (`gir1.2-gtk-4.0`).',
        'install.note_config': 'Configure `historyLimit`, `theme`, `autostart`, and custom `shortcut` keys.',

        'faq.tag': 'FAQ',
        'faq.title': 'Frequently Asked Questions',
        'faq.subtitle': 'Quick answers to common questions about Klipr.',
        'faq.q1': 'Does Klipr work on Ubuntu, Debian, and other Linux distros?',
        'faq.a1': 'Yes! Klipr is packaged as a `.deb` for Ubuntu 22.04+, Debian 12+, Linux Mint, and Pop!_OS. It can also be run from source on Arch Linux, Fedora, or any distro with Python 3.10+ and GTK4.',
        'faq.q2': 'Are passwords or copied credentials sent anywhere?',
        'faq.a2': 'No. Klipr is 100% offline, privacy-first, and contains zero network telemetry or tracking. Your clipboard history stays strictly on your local disk at `~/.local/share/klipr`.',
        'faq.q3': 'Can I change the global toggle shortcut?',
        'faq.a3': 'Yes! You can change the global shortcut from the in-app Settings dialog or by editing the `"shortcut"` field in `~/.config/klipr/settings.json` (default: `Ctrl+Alt+M`).',
        'faq.q4': 'How is image clipboard history stored?',
        'faq.a4': 'When an image is copied (like from a screenshot tool or browser), Klipr saves an optimized image file with cached thumbnail generation, allowing one-click paste back to any application.',

        'footer.crafted': 'Klipr &bull; Crafted with passion by',
        'footer.repo': 'GitHub Repository',
        'footer.releases': 'Releases',
        'footer.license': 'MIT License',

        'toast.copied': 'Copied to clipboard!',
        'toast.failed': 'Failed to copy. Please copy manually.'
    },
    vi: {
        'nav.features': 'Tính năng',
        'nav.screenshots': 'Giao diện',
        'nav.comparison': 'Tại sao chọn Klipr',
        'nav.install': 'Cài đặt',
        'nav.faq': 'Hỏi đáp',
        'nav.star': 'Star trên GitHub',

        'hero.release_suffix': '— Bản phát hành mới nhất',
        'hero.title': 'Quản lý lịch sử clipboard,<br><span class="gradient-text">mượt mà cho Linux.</span>',
        'hero.desc': 'Klipr tự động lưu lại mọi nội dung bạn sao chép — văn bản, mã nguồn, lệnh terminal và ảnh chụp màn hình. Tích hợp GTK4 native, không dùng Electron nặng nề, tìm kiếm siêu nhanh.',
        'hero.download_deb': 'Tải gói .deb',
        'hero.install_guide': 'Hướng dẫn cài đặt',
        'hero.pill_gtk': 'GTK4 Native',
        'hero.pill_ram': '< 35MB RAM tiêu thụ',
        'hero.pill_privacy': '100% Offline & Bảo mật',
        'hero.pill_mit': 'Mã nguồn mở MIT',

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

        'comparison.tag': 'So sánh hiệu năng',
        'comparison.title': 'Vì sao nên chọn Klipr?',
        'comparison.subtitle': 'Nói không với các ứng dụng clipboard cồng kềnh ngốn hàng trăm MB RAM.',
        'comparison.th_metric': 'Tính năng / Tiêu chí',
        'comparison.th_klipr': 'Klipr (Native GTK4)',
        'comparison.th_electron': 'Ứng dụng nền Electron',
        'comparison.th_standard': 'Clipboard Linux cơ bản',
        'comparison.r1_metric': 'Mức tiêu thụ RAM',
        'comparison.r2_metric': 'Độ trễ mở phím tắt',
        'comparison.r2_val1': '< 0.15s (Tức thì)',
        'comparison.r3_metric': 'Lưu ảnh & Screenshot',
        'comparison.r3_val1': '✓ Đầy đủ Thumbnail',
        'comparison.r3_val2': '✓ Có hỗ trợ',
        'comparison.r3_val3': '✕ Thường chỉ lưu Text',
        'comparison.r4_metric': 'Hệ thống ghim Yêu thích',
        'comparison.r4_val1': '✓ Ghim vĩnh viễn',
        'comparison.r4_val2': '✓ Có hỗ trợ',
        'comparison.r4_val3': '✕ Hạn chế',
        'comparison.r5_metric': 'Bảo mật & Quyền riêng tư',
        'comparison.r5_val1': '✓ 100% Offline, không theo dõi',
        'comparison.r5_val2': 'Tùy app / Thường có thu thập',
        'comparison.r5_val3': '✓ Offline',
        'comparison.r6_metric': 'Giấy phép',
        'comparison.r6_val1': 'Mã nguồn mở MIT',
        'comparison.r6_val2': 'Thương mại / Đóng mã',
        'comparison.r6_val3': 'Mã nguồn mở',

        'install.title': 'Cài đặt Klipr dễ dàng',
        'install.subtitle': 'Chọn phương thức cài đặt phù hợp với bạn bên dưới:',
        'install.tab_deb': 'Ubuntu / Debian (.deb)',
        'install.tab_source': 'Build từ mã nguồn',
        'install.tab_config': 'Tùy chỉnh cài đặt',
        'install.note_deb_prefix': 'Tải gói phát hành trực tiếp từ',
        'install.note_source': 'Yêu cầu Python 3.10+, GTK4 và PyGObject (`gir1.2-gtk-4.0`).',
        'install.note_config': 'Tùy chỉnh `historyLimit`, `theme`, `autostart` và phím tắt `shortcut` theo ý muốn.',

        'faq.tag': 'Hỏi & Đáp',
        'faq.title': 'Câu hỏi thường gặp',
        'faq.subtitle': 'Giải đáp nhanh các thắc mắc phổ biến về Klipr.',
        'faq.q1': 'Klipr có chạy được trên Ubuntu, Debian và các bản Linux khác không?',
        'faq.a1': 'Có! Klipr có sẵn file cài đặt .deb cho Ubuntu 22.04+, Debian 12+, Linux Mint và Pop!_OS. Ngoài ra bạn có thể chạy từ mã nguồn trên Arch Linux, Fedora hoặc bất kỳ bản distro nào có Python 3.10+ và GTK4.',
        'faq.q2': 'Mật khẩu hoặc thông tin sao chép có bị gửi đi đâu không?',
        'faq.a2': 'Tuyệt đối không. Klipr hoạt động 100% offline, tôn trọng quyền riêng tư và không chứa bất kỳ mã theo dõi hay gửi dữ liệu qua mạng. Lịch sử được lưu trữ hoàn toàn nội bộ trên máy bạn tại `~/.local/share/klipr`.',
        'faq.q3': 'Tôi có thể đổi phím tắt mở ứng dụng không?',
        'faq.a3': 'Có! Bạn có thể đổi phím tắt từ bảng Cài đặt (Settings) trong ứng dụng hoặc chỉnh sửa trường `"shortcut"` trong file `~/.config/klipr/settings.json` (mặc định là `Ctrl+Alt+M`).',
        'faq.q4': 'Lịch sử ảnh được lưu trữ như thế nào?',
        'faq.a4': 'Khi bạn copy một bức ảnh (từ trình duyệt hoặc công cụ chụp màn hình), Klipr sẽ tối ưu và lưu vào bộ nhớ đệm kèm thumbnail, cho phép bạn dán lại vào bất kỳ ứng dụng nào chỉ với 1 click.',

        'footer.crafted': 'Klipr &bull; Phát triển bởi',
        'footer.repo': 'Kho mã nguồn GitHub',
        'footer.releases': 'Các bản phát hành',
        'footer.license': 'Giấy phép MIT',

        'toast.copied': 'Đã sao chép vào bộ nhớ tạm!',
        'toast.failed': 'Không thể sao chép. Vui lòng sao chép thủ công.'
    }
};

let currentLang = localStorage.getItem('klipr_lang') || 'en';
let currentReleaseTag = 'v1.2.3';

document.addEventListener('DOMContentLoaded', () => {
    initI18n();
    initScrollReveal();
    initNavbarScroll();
    initCopyButtons();
    initLightbox();
    initInstallTabs();
    initFaqAccordion();
    initBackToTop();
    fetchLatestRelease();
});

/**
 * Multi-Language (i18n) Engine
 */
function initI18n() {
    setLanguage(currentLang);

    const langBtns = document.querySelectorAll('.lang-btn');
    langBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.getAttribute('data-lang');
            if (lang && lang !== currentLang) {
                setLanguage(lang);
            }
        });
    });
}

function setLanguage(lang) {
    if (!translations[lang]) return;
    currentLang = lang;
    localStorage.setItem('klipr_lang', lang);
    document.documentElement.lang = lang;

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
        if (translations[lang][key]) {
            el.innerHTML = translations[lang][key];
        }
    });

    // Update version badge
    updateVersionBadge();
}

function updateVersionBadge() {
    const badge = document.getElementById('latest-version-badge');
    if (badge) {
        const suffix = translations[currentLang]['hero.release_suffix'] || '— Latest Release';
        badge.textContent = `${currentReleaseTag} ${suffix}`;
    }
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
                const msg = translations[currentLang]['toast.copied'] || 'Copied to clipboard!';
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
                const failMsg = translations[currentLang]['toast.failed'] || 'Failed to copy. Please copy manually.';
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

    try {
        const response = await fetch(`https://api.github.com/repos/${repo}/releases/latest`);
        if (!response.ok) return;

        const release = await response.json();
        currentReleaseTag = release.tag_name || 'v1.2.3';
        updateVersionBadge();

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
