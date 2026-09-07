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
        'hero.title': 'Clipboard history,<br><span class="gradient-text">made seamless for Linux.</span>',
        'hero.desc': 'Klipr captures everything you copy — text, code, commands, and screenshots. Native GTK4 desktop integration, zero Electron bloat, and instant fuzzy search.',
        'hero.install_guide': 'Install Now',
        'hero.download_deb': 'Download .deb',
        'hero.pill_free': 'Open Source',
        'hero.pill_gtk': 'Native GTK4 (~41MB RAM)',
        'hero.pill_privacy': 'Offline & Private',
        'hero.pill_no_account': 'No Account Required',

        'promise.tag': 'Open Source',
        'promise.title': 'Built openly for the Linux community',
        'promise.subtitle': 'Klipr is lightweight and transparent. No paywalls, no monetization, no tracking.',
        'promise.c1_title': 'Community Driven',
        'promise.c1_desc': 'No paid tiers, subscriptions, or locked features. Built as an open tool for everyone.',
        'promise.c2_title': 'Zero Advertisements',
        'promise.c2_desc': 'No sponsored banners, no upgrade prompts, and no annoying popups. Clean and focused.',
        'promise.c3_title': 'Offline & Private',
        'promise.c3_desc': 'All snippets and history remain strictly on your local disk. Nothing is uploaded to any cloud server.',
        'promise.c4_title': 'Permissive MIT License',
        'promise.c4_desc': 'Free for both personal and commercial use. Inspect, modify, or fork the full codebase on GitHub.',

        'showcase.tag': 'Demo',
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
        'features.f4_desc': 'Preserves copied images and screenshots with thumbnail previews, one-click paste back, and AI OCR text extraction.',
        'features.f5_title': 'Dark, Light & System',
        'features.f5_desc': 'Seamlessly synchronizes with your Linux desktop theme or choose your preferred look manually.',
        'features.f6_title': 'Pure Native Performance',
        'features.f6_desc': 'Built with Python and GTK4. Tiny memory footprint that runs silently in the system tray.',

        'ai.tag': 'AI Features',
        'ai.title': 'Smarter clipboard with Next-Gen AI',
        'ai.subtitle': 'Boost your productivity with seamless AI capabilities built directly into your desktop workflow.',
        'ai.ocr_badge': 'AI OCR &bull; Instant Text Extraction',
        'ai.ocr_title': 'Extract text from copied images in one click',
        'ai.ocr_desc': 'Copy any screenshot or image to your clipboard. Klipr can immediately send a desktop notification to extract text using AI, or click the OCR button on any image entry in your history to instantly copy detected text to your clipboard.',
        'ai.feat1_title': '1-Click Desktop Notification',
        'ai.feat1_desc': 'Detects when screenshots are copied and shows a quick action notification to transcribe text immediately.',
        'ai.feat2_title': 'Gemini & OpenAI Integration',
        'ai.feat2_desc': 'Choose between Google Gemini or OpenAI. Use custom models like gemini-3.1-flash-lite or gpt-4o-mini.',
        'ai.feat3_title': 'Bring Your Own Key (BYOK)',
        'ai.feat3_desc': '100% private. Your API keys are stored locally on your device with direct API calls and zero third-party proxy.',
        'ai.step1_label': 'Copy Screenshot',
        'ai.step1_detail': 'Press PrtScn or copy any image',
        'ai.step2_label': 'AI Extraction',
        'ai.step2_detail': 'Gemini / OpenAI extracts high-precision text',
        'ai.step3_label': 'Auto-Copied & Ready',
        'ai.step3_detail': 'Text added to history, ready to paste',
        'ai.future_tag': 'Future AI Features',
        'ai.future_desc': 'Designed for future expansion: intelligent text summarization, instant code translation, and contextual helpers are on the roadmap.',

        'install.title': 'Install Klipr in Seconds',
        'install.subtitle': 'Copy, paste, run. That\'s it.',
        'install.note_apt': 'Works on any Ubuntu system out of the box. Future updates then arrive through `sudo snap refresh` automatically.',

        'faq.tag': 'FAQ',
        'faq.title': 'Frequently Asked Questions',
        'faq.subtitle': 'Quick answers to common questions about Klipr.',
        'faq.q0': 'Is Klipr really 100% free? Are there any hidden fees or Pro tiers?',
        'faq.a0': 'Yes. Klipr is 100% free and open source under the permissive MIT License. There are no paid tiers, subscriptions, hidden fees, or advertisements.',
        'faq.q1': 'Which Linux distributions and desktop environments are supported?',
        'faq.a1': 'Klipr runs on any modern Linux distribution with GTK4 and D-Bus support, including Ubuntu, Debian, Fedora, Arch Linux, and Linux Mint. It works seamlessly across GNOME, KDE Plasma, XFCE, Cinnamon, and MATE.',
        'faq.q2': 'Is my clipboard data sent anywhere?',
        'faq.a2': 'No. Klipr operates 100% offline. All text, code snippets, and image history are stored strictly on your local device in a local SQLite database with zero telemetry or network calls.',
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
        'hero.title': 'Quản lý lịch sử clipboard,<br><span class="gradient-text">mượt mà cho Linux.</span>',
        'hero.desc': 'Klipr tự động lưu lại mọi nội dung bạn sao chép — văn bản, mã nguồn, lệnh terminal và ảnh chụp màn hình. Tích hợp GTK4 native, không dùng Electron nặng nề, tìm kiếm siêu nhanh.',
        'hero.install_guide': 'Cài đặt ngay',
        'hero.download_deb': 'Tải gói .deb',
        'hero.pill_free': 'Mã nguồn mở',
        'hero.pill_gtk': 'GTK4 Native (~41MB RAM)',
        'hero.pill_privacy': 'Offline & Bảo mật',
        'hero.pill_no_account': 'Không cần tài khoản',

        'promise.tag': 'Mã nguồn mở',
        'promise.title': 'Mã nguồn mở và minh bạch',
        'promise.subtitle': 'Klipr được phát triển công khai cho cộng đồng Linux. Không thu phí, không theo dõi.',
        'promise.c1_title': 'Hoàn toàn mở',
        'promise.c1_desc': 'Không có bản Pro, không thu phí bản quyền, không khóa tính năng. Mọi tính năng đều miễn phí cho tất cả mọi người.',
        'promise.c2_title': 'Không quảng cáo',
        'promise.c2_desc': 'Không pop-up mời nâng cấp, không banner quảng cáo, không làm phiền trải nghiệm làm việc của bạn.',
        'promise.c3_title': 'Offline & Bảo mật',
        'promise.c3_desc': 'Toàn bộ nội dung sao chép lưu trữ nội bộ trên máy bạn. Tuyệt đối không gửi dữ liệu lên bất kỳ máy chủ nào.',
        'promise.c4_title': 'Mã nguồn mở MIT',
        'promise.c4_desc': 'Hoàn toàn tự do sử dụng cho cá nhân lẫn thương mại. Thoải mái kiểm tra, chỉnh sửa mã nguồn trên GitHub.',

        'showcase.tag': 'Demo',
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
        'features.f4_desc': 'Giữ lại các hình ảnh đã copy với thumbnail xem trước, dán lại nhanh chóng và trích xuất chữ bằng AI OCR.',
        'features.f5_title': 'Dark, Light & Theo hệ thống',
        'features.f5_desc': 'Tự động đồng bộ theo giao diện Sáng/Tối của Linux hoặc tùy chọn thủ công theo sở thích.',
        'features.f6_title': 'Hiệu năng Native vượt trội',
        'features.f6_desc': 'Viết bằng Python và GTK4. Chiếm cực ít bộ nhớ RAM và chạy ẩn trên khay hệ thống.',

        'ai.tag': 'Tính năng AI',
        'ai.title': 'Quản lý clipboard thông minh cùng AI thế hệ mới',
        'ai.subtitle': 'Nâng tầm hiệu suất làm việc với các khả năng AI mạnh mẽ được tích hợp trực tiếp vào quy trình máy tính của bạn.',
        'ai.ocr_badge': 'AI OCR &bull; Trích xuất văn bản tức thì',
        'ai.ocr_title': 'Trích xuất văn bản từ hình ảnh sao chép chỉ với 1 click',
        'ai.ocr_desc': 'Bất cứ khi nào bạn chụp màn hình hoặc sao chép hình ảnh, Klipr có thể gửi thông báo desktop để bạn trích xuất chữ tức thì bằng AI, hoặc bấm nút OCR trên ảnh trong lịch sử để sao chép văn bản vào clipboard ngay lập tức.',
        'ai.feat1_title': 'Thông báo Desktop 1-Click',
        'ai.feat1_desc': 'Tự nhận diện khi chụp ảnh màn hình và hiện thông báo thao tác nhanh để chuyển ảnh thành văn bản ngay.',
        'ai.feat2_title': 'Tích hợp Gemini & OpenAI',
        'ai.feat2_desc': 'Linh hoạt chọn giữa Google Gemini hoặc OpenAI. Tùy biến các model như gemini-3.1-flash-lite hay gpt-4o-mini.',
        'ai.feat3_title': 'Dùng API Key của bạn (BYOK)',
        'ai.feat3_desc': 'Hoàn toàn bảo mật. API key lưu cục bộ trên máy, gửi trực tiếp đến nhà cung cấp AI mà không qua bất kỳ máy chủ trung gian nào.',
        'ai.step1_label': 'Chụp / Copy hình ảnh',
        'ai.step1_detail': 'Bấm phím chụp màn hình hoặc copy ảnh',
        'ai.step2_label': 'AI trích xuất chữ',
        'ai.step2_detail': 'Gemini / OpenAI nhận diện chữ chuẩn xác',
        'ai.step3_label': 'Tự động sao chép',
        'ai.step3_detail': 'Lưu vào lịch sử, sẵn sàng dán mọi nơi',
        'ai.future_tag': 'Mở rộng tính năng AI trong tương lai',
        'ai.future_desc': 'Kiến trúc module sẵn sàng cho nhiều tính năng mới: tóm tắt văn bản thông minh, dịch thuật ngôn ngữ, giải thích code...',

        'install.title': 'Cài đặt Klipr dễ dàng',
        'install.subtitle': 'Copy, dán, chạy. Vậy là xong.',
        'install.note_apt': 'Chạy được ngay trên mọi máy Ubuntu. Các bản cập nhật sau đó sẽ tự động tới qua `sudo snap refresh`.',

        'faq.tag': 'Hỏi & Đáp',
        'faq.title': 'Câu hỏi thường gặp',
        'faq.subtitle': 'Giải đáp nhanh các thắc mắc phổ biến về Klipr.',
        'faq.q0': 'Klipr có thực sự miễn phí 100% không? Có chi phí ẩn hay gói Pro không?',
        'faq.a0': 'Có. Klipr hoàn toàn miễn phí 100% và là phần mềm mã nguồn mở theo giấy phép MIT. Không có bản trả phí, không thuê bao, không chi phí ẩn và không quảng cáo.',
        'faq.q1': 'Những bản phân phối Linux và môi trường desktop nào được hỗ trợ?',
        'faq.a1': 'Klipr chạy trên mọi bản phân phối Linux hiện đại hỗ trợ GTK4 và D-Bus, bao gồm Ubuntu, Debian, Fedora, Arch Linux và Linux Mint. Ứng dụng hoạt động mượt mà trên GNOME, KDE Plasma, XFCE, Cinnamon và MATE.',
        'faq.q2': 'Dữ liệu clipboard của tôi có bị gửi đi đâu không?',
        'faq.a2': 'Không. Klipr hoạt động 100% offline. Toàn bộ văn bản, đoạn mã và hình ảnh sao chép được lưu trữ cục bộ trong cơ sở dữ liệu SQLite trên máy bạn, tuyệt đối không có telemetry hay kết nối mạng.',
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

    document.title = 'Klipr - Linux Clipboard Manager';

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
        currentReleaseTag = release.tag_name || 'v1.2.5';
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
