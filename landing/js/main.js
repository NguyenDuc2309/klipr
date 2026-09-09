/**
 * Klipr Landing Page JavaScript
 * Multi-language (EN / VI), Release Fetching, Copy Toasts, Lightbox, and FAQ Accordions.
 */

// i18n Translations Dictionary
const translations = {
    en: {
        'nav.features': 'Features',
        'nav.ai_features': 'AI Features',
        'nav.screenshots': 'Demo',
        'nav.install': 'Install',
        'nav.faq': 'FAQ',
        'nav.star': 'Star on GitHub',

        'hero.release_suffix': '— Latest Release',
        'hero.title': 'Clipboard history,<br><span class="gradient-text">made seamless for Ubuntu & Linux.</span>',
        'hero.desc': 'Klipr is a native clipboard manager for Linux and Ubuntu that captures everything you copy — text, code, commands, and screenshots. Zero Electron bloat, instant fuzzy search over your clipboard history.',
        'hero.install_guide': 'Install Now',
        'hero.download_deb': 'Download .deb',
        'hero.pill_free': 'Open Source',
        'hero.pill_gtk': 'Native GTK4 (~41MB RAM)',
        'hero.pill_privacy': 'Offline & Private',
        'hero.pill_no_account': 'No Account Required',

        'showcase.tag': 'Demo',
        'showcase.title': 'Clean, focused clipboard manager UI',
        'showcase.subtitle': 'Fits right at home on Ubuntu and every major Linux desktop environment — GNOME, XFCE, and KDE.',
        'showcase.window1_title': 'Klipr — History & Favorites',
        'showcase.window1_caption': 'Clipboard History with Thumbnail Previews',
        'showcase.window2_title': 'Klipr — Settings & Customization',
        'showcase.window2_caption': 'Themes, Global Hotkeys & Tray Settings',
        'showcase.zoom': 'Click to Zoom',

        'features.tag': 'Features',
        'features.title': 'Everything a Linux clipboard manager should do',
        'features.subtitle': 'Core clipboard history features for Ubuntu, Fedora, and every major Linux desktop — no bloat, no subscriptions.',
        'features.f1_title': 'Automatic History',
        'features.f1_desc': 'Quietly records snippets and automatically prunes older items based on your configured limit.',
        'features.f2_title': 'Instant Fuzzy Search',
        'features.f2_desc': 'Search across your entire clipboard history with zero input latency and full multilingual IME support.',
        'features.f3_title': 'Pinned Favorites',
        'features.f3_desc': 'Bookmark recurring commands, passwords, or snippets. Pinned items are protected from auto-pruning.',
        'features.f4_title': 'Image & Screenshot Capture',
        'features.f4_desc': 'Preserves copied images and screenshots with thumbnail previews, one-click paste back, and AI OCR text extraction.',
        'features.f5_title': 'Dark, Light & System',
        'features.f5_desc': 'Seamlessly synchronizes with your Linux desktop theme or choose your preferred look manually.',
        'features.f6_title': 'Pure Native Performance',
        'features.f6_desc': 'Built with Python and GTK4. Tiny memory footprint that runs silently in the system tray.',

        'ai.tag': 'Bonus: AI Powered',
        'ai.title': 'Extract text from any image in seconds',
        'ai.subtitle': 'On top of clipboard history, Klipr can turn screenshots, invoices, and receipts into clean, editable text.',
        'ai.showcase_title': 'Klipr AI — Image & Invoice Text Extraction',
        'ai.showcase_caption': 'Smart layout-preserved extraction for receipts, bills, and code',
        'ai.point1_title': 'Fast & Accurate',
        'ai.point1_desc': 'Powered by Google Gemini & OpenAI. High-speed extraction in seconds with superior accuracy.',
        'ai.point2_title': 'Bills, Receipts & Docs',
        'ai.point2_desc': 'Effortlessly extracts data from paper receipts, invoices, tables, and documents into clean text.',
        'ai.point3_title': 'Clean & Aligned Output',
        'ai.point3_desc': 'Smart plain-text column alignment with zero markdown clutter. Ready to paste anywhere.',
        'ai.point4_title': '100% Private (BYOK)',
        'ai.point4_desc': 'Bring Your Own Key. Your keys are stored locally with direct API calls and zero tracking.',

        'install.title': 'Install the Klipr Clipboard Manager in Seconds',
        'install.subtitle': 'One command on Ubuntu or any Snap-enabled Linux distro.',
        'install.note_apt': 'Works out of the box on Ubuntu, Fedora, Arch, and other major Linux distributions. Future updates then arrive through `sudo snap refresh` automatically.',

        'faq.tag': 'FAQ',
        'faq.title': 'Frequently Asked Questions',
        'faq.subtitle': 'Quick answers to common questions about Klipr.',
        'faq.q0': 'Is Klipr really 100% free? Are there any hidden fees or Pro tiers?',
        'faq.a0': 'Yes. Klipr is 100% free and open source under the permissive MIT License. There are no paid tiers, subscriptions, hidden fees, upgrade prompts, or advertisements — ever.',
        'faq.q1': 'Which Linux distributions and desktop environments are supported?',
        'faq.a1': 'Klipr runs on any modern Linux distribution with GTK4 and D-Bus support, including Ubuntu, Debian, Fedora, Arch Linux, and Linux Mint. It works seamlessly across GNOME, KDE Plasma, XFCE, Cinnamon, and MATE.',
        'faq.q2': 'Is my clipboard data sent anywhere?',
        'faq.a2': 'No. Klipr operates 100% offline by default. All text, code snippets, and image history are stored strictly on your local device in a local SQLite database with zero telemetry. The only exception is the optional AI OCR feature, which only calls out to your own configured Gemini/OpenAI API key — see the next question.',
        'faq.q3': 'How many clipboard items does Klipr keep?',
        'faq.a3': 'By default, Klipr stores your last 50 items. You can easily adjust this limit to 100 or 150 items in the Settings dialog to fit your workflow.',
        'faq.q4': 'Are my pinned items deleted when the history fills up?',
        'faq.a4': 'Never. Pinned favorites are stored separately and protected from automatic pruning. They remain safely pinned until you explicitly remove them.',
        'faq.q5': 'How are copied images stored?',
        'faq.a5': 'Copied images and screenshots are saved as optimized PNG files in your local cache directory (~/.cache/klipr/images/) with instant thumbnail previews. Deduplication ensures identical images are not saved twice.',
        'faq.q6': 'How does the AI OCR text extraction work? Is my data private?',
        'faq.a6': 'Klipr uses Bring Your Own Key (BYOK) for Google Gemini and OpenAI. Your API keys are stored locally on your device. When you extract text, images are sent directly to the official AI provider endpoint with zero telemetry or middleman servers. If you don\'t configure an API key, Klipr remains 100% offline.',

        'footer.crafted': 'Klipr &bull; Created by',
        'footer.free_note': 'Open Source under the MIT License.',
        'footer.repo': 'GitHub Repository',
        'footer.releases': 'Releases',
        'footer.license': 'MIT License',

        'toast.copied': 'Copied to clipboard!',
        'toast.failed': 'Failed to copy. Please copy manually.'
    },
    vi: {
        'nav.features': 'Tính năng',
        'nav.ai_features': 'Tính năng AI',
        'nav.screenshots': 'Demo',
        'nav.install': 'Cài đặt',
        'nav.faq': 'Hỏi đáp',
        'nav.star': 'Star trên GitHub',

        'hero.release_suffix': '— Bản phát hành mới nhất',
        'hero.title': 'Quản lý lịch sử clipboard,<br><span class="gradient-text">mượt mà cho Ubuntu & Linux.</span>',
        'hero.desc': 'Klipr là ứng dụng quản lý clipboard (clipboard manager) native cho Linux và Ubuntu, tự động lưu lại mọi nội dung bạn sao chép — văn bản, mã nguồn, lệnh terminal và ảnh chụp màn hình. Không dùng Electron nặng nề, tìm kiếm lịch sử clipboard siêu nhanh.',
        'hero.install_guide': 'Cài đặt ngay',
        'hero.download_deb': 'Tải gói .deb',
        'hero.pill_free': 'Mã nguồn mở',
        'hero.pill_gtk': 'GTK4 Native (~41MB RAM)',
        'hero.pill_privacy': 'Offline & Bảo mật',
        'hero.pill_no_account': 'Không cần tài khoản',

        'showcase.tag': 'Demo',
        'showcase.title': 'Giao diện quản lý clipboard gọn gàng, tập trung',
        'showcase.subtitle': 'Hoạt động hoàn hảo trên Ubuntu và mọi môi trường desktop Linux phổ biến như GNOME, XFCE và KDE.',
        'showcase.window1_title': 'Klipr — Lịch sử & Yêu thích',
        'showcase.window1_caption': 'Lịch sử clipboard kèm hình ảnh thumbnail trực quan',
        'showcase.window2_title': 'Klipr — Cài đặt & Tùy biến',
        'showcase.window2_caption': 'Tùy biến giao diện Sáng/Tối, phím tắt & khay hệ thống',
        'showcase.zoom': 'Bấm để phóng to',

        'features.tag': 'Tính năng',
        'features.title': 'Đầy đủ những gì một clipboard manager Linux cần có',
        'features.subtitle': 'Tính năng quản lý lịch sử clipboard cốt lõi cho Ubuntu, Fedora và mọi bản Linux phổ biến — không nặng máy, không thu phí.',
        'features.f1_title': 'Lưu trữ tự động',
        'features.f1_desc': 'Âm thầm ghi nhớ các đoạn văn bản, tự động dọn dẹp các mục cũ theo giới hạn bạn đặt.',
        'features.f2_title': 'Tìm kiếm tức thì',
        'features.f2_desc': 'Tìm kiếm nhanh chóng trong toàn bộ lịch sử với độ trễ bằng 0, hỗ trợ tốt gõ tiếng Việt (IME).',
        'features.f3_title': 'Ghim mục yêu thích',
        'features.f3_desc': 'Đánh dấu các lệnh hay dùng hoặc ghi chú quan trọng. Các mục ghim không bao giờ bị xóa tự động.',
        'features.f4_title': 'Lưu ảnh & Ảnh chụp màn hình',
        'features.f4_desc': 'Giữ lại các hình ảnh đã copy với thumbnail xem trước, dán lại nhanh chóng và trích xuất chữ bằng AI OCR.',
        'features.f5_title': 'Dark, Light & Theo hệ thống',
        'features.f5_desc': 'Tự động đồng bộ theo giao diện Sáng/Tối của Linux hoặc tùy chọn thủ công theo sở thích.',
        'features.f6_title': 'Hiệu năng Native vượt trội',
        'features.f6_desc': 'Viết bằng Python và GTK4. Chiếm cực ít bộ nhớ RAM và chạy ẩn trên khay hệ thống.',

        'ai.tag': 'Bonus: Trí tuệ nhân tạo (AI)',
        'ai.title': 'Trích xuất chữ từ hình ảnh & hóa đơn tức thì',
        'ai.subtitle': 'Ngoài lịch sử clipboard, Klipr còn biến ảnh chụp màn hình, hóa đơn và bill thanh toán thành văn bản sạch sẽ, ngay ngắn.',
        'ai.showcase_title': 'Klipr AI — Trích xuất chữ từ Ảnh & Hóa đơn / Bill',
        'ai.showcase_caption': 'Thông minh nhận diện và căn chỉnh cột cho hóa đơn, biên lai, bảng biểu và mã nguồn',
        'ai.point1_title': 'Nhanh chóng & Chuẩn xác',
        'ai.point1_desc': 'Hỗ trợ Google Gemini & OpenAI. Nhận diện chữ siêu tốc với độ chính xác cao.',
        'ai.point2_title': 'Hóa đơn, Biên lai & Tài liệu',
        'ai.point2_desc': 'Chuyên trị hóa đơn bán lẻ, bill thanh toán, bảng số liệu, tài liệu scan và ảnh chụp màn hình.',
        'ai.point3_title': 'Căn chỉnh cột ngay ngắn',
        'ai.point3_desc': 'Tự động định dạng thẳng hàng dạng văn bản thuần, không dính ký tự thừa markdown, dán được ngay.',
        'ai.point4_title': 'Bảo mật tuyệt đối (BYOK)',
        'ai.point4_desc': 'Dùng API Key cá nhân của bạn. Key lưu an toàn trên máy, kết nối trực tiếp không qua máy chủ trung gian.',

        'install.title': 'Cài đặt Klipr — Clipboard Manager cho Linux',
        'install.subtitle': 'Một câu lệnh duy nhất trên Ubuntu hoặc mọi bản Linux hỗ trợ Snap.',
        'install.note_apt': 'Chạy được ngay trên Ubuntu, Fedora, Arch và các bản phân phối Linux phổ biến khác. Các bản cập nhật sau đó sẽ tự động tới qua `sudo snap refresh`.',

        'faq.tag': 'Hỏi & Đáp',
        'faq.title': 'Câu hỏi thường gặp',
        'faq.subtitle': 'Giải đáp nhanh các thắc mắc phổ biến về Klipr.',
        'faq.q0': 'Klipr có thực sự miễn phí 100% không? Có chi phí ẩn hay gói Pro không?',
        'faq.a0': 'Có. Klipr hoàn toàn miễn phí 100% và là phần mềm mã nguồn mở theo giấy phép MIT. Không có bản trả phí, không thuê bao, không chi phí ẩn, không mời mọc nâng cấp và không quảng cáo — mãi mãi.',
        'faq.q1': 'Những bản phân phối Linux và môi trường desktop nào được hỗ trợ?',
        'faq.a1': 'Klipr chạy trên mọi bản phân phối Linux hiện đại hỗ trợ GTK4 và D-Bus, bao gồm Ubuntu, Debian, Fedora, Arch Linux và Linux Mint. Ứng dụng hoạt động mượt mà trên GNOME, KDE Plasma, XFCE, Cinnamon và MATE.',
        'faq.q2': 'Dữ liệu clipboard của tôi có bị gửi đi đâu không?',
        'faq.a2': 'Không. Mặc định Klipr hoạt động 100% offline. Toàn bộ văn bản, đoạn mã và hình ảnh sao chép được lưu trữ cục bộ trong cơ sở dữ liệu SQLite trên máy bạn, tuyệt đối không có telemetry. Ngoại lệ duy nhất là tính năng AI OCR (tùy chọn), chỉ gọi tới API key Gemini/OpenAI do chính bạn cấu hình — xem câu hỏi tiếp theo.',
        'faq.q3': 'Klipr lưu trữ được bao nhiêu mục clipboard?',
        'faq.a3': 'Mặc định Klipr lưu trữ 50 mục gần nhất. Bạn có thể dễ dàng điều chỉnh giới hạn này thành 100 hoặc 150 mục trong bảng Cài đặt để phù hợp với nhu cầu.',
        'faq.q4': 'Các mục đã ghim có bị xóa khi lịch sử clipboard bị đầy không?',
        'faq.a4': 'Tuyệt đối không. Các mục yêu thích đã ghim được bảo vệ và tách biệt khỏi cơ chế tự động dọn dẹp. Chúng sẽ luôn được giữ an toàn cho đến khi bạn tự tay bỏ ghim.',
        'faq.q5': 'Hình ảnh sao chép được lưu trữ như thế nào?',
        'faq.a5': 'Hình ảnh và ảnh chụp màn hình được lưu dưới dạng file PNG tối ưu trong thư mục bộ nhớ đệm cục bộ (~/.cache/klipr/images/) kèm thumbnail xem trước. Cơ chế lọc trùng giúp không lưu lặp lại cùng một ảnh.',
        'faq.q6': 'Tính năng AI OCR trích xuất chữ hoạt động ra sao? Dữ liệu có bảo mật không?',
        'faq.a6': 'Klipr áp dụng cơ chế Bring Your Own Key (BYOK) với Google Gemini và OpenAI. Khóa API lưu hoàn toàn cục bộ trên máy bạn. Khi bạn trích xuất chữ, hình ảnh được gửi thẳng đến API chính thức của nhà cung cấp AI, không qua máy chủ trung gian. Nếu bạn không cài đặt API key, Klipr tiếp tục hoạt động 100% offline.',

        'footer.crafted': 'Klipr &bull; Phát triển bởi',
        'footer.free_note': 'Mã nguồn mở theo giấy phép MIT.',
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
let currentReleaseTag = 'v1.2.7';

/**
 * Public function to set language
 */
window.setLanguage = function(lang) {
    if (!translations[lang]) return;
    currentLang = lang;
    safeSetStorage('klipr_lang', lang);
    document.documentElement.lang = lang;

    document.title = lang === 'vi'
        ? 'Klipr - Ứng dụng quản lý Clipboard cho Ubuntu & Linux'
        : 'Klipr - Clipboard Manager & History for Ubuntu & Linux';

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

    try {
        const response = await fetch(`https://api.github.com/repos/${repo}/releases/latest`);
        if (!response.ok) return;

        const release = await response.json();
        currentReleaseTag = release.tag_name || 'v1.2.7';
        updateVersionBadge();

        const debAsset = release.assets?.find(asset => asset.name.endsWith('.deb'));
        if (debAsset && downloadBtn) {
            downloadBtn.href = debAsset.browser_download_url;
            downloadBtn.setAttribute('title', `Download ${debAsset.name}`);
        }
    } catch (error) {
        console.info('Using fallback release metadata:', error);
    }
}
