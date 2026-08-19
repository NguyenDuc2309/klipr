/**
 * Klipr Landing Page JavaScript
 * Includes Interactive Clipboard Simulator, Release Fetching, Copy Toasts, Lightbox, and FAQ Accordions.
 */

document.addEventListener('DOMContentLoaded', () => {
    initScrollReveal();
    initNavbarScroll();
    initCopyButtons();
    initLightbox();
    initClipboardDemo();
    initInstallTabs();
    initFaqAccordion();
    initBackToTop();
    fetchLatestRelease();
});

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
            // Prevent duplicate triggers if clicking an inner button
            e.stopPropagation();
            const textToCopy = block.getAttribute('data-copy');
            if (!textToCopy) return;

            try {
                await navigator.clipboard.writeText(textToCopy);
                showToast('Copied to clipboard!');
                
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
                showToast('Failed to copy. Please copy manually.');
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
 * Interactive Clipboard Simulator / Live Demo
 */
const mockClips = [
    {
        id: '1',
        title: 'git commit -m "feat: enhance native GTK4 UI and memory performance"',
        content: 'git commit -m "feat: enhance native GTK4 UI and memory performance"',
        type: 'code',
        tag: 'Bash',
        time: 'Just now',
        starred: true,
        icon: 'terminal'
    },
    {
        id: '2',
        title: 'const options = { theme: "dark", autoPrune: true, limit: 100 };',
        content: 'const options = { theme: "dark", autoPrune: true, limit: 100 };',
        type: 'code',
        tag: 'JavaScript',
        time: '2m ago',
        starred: false,
        icon: 'code'
    },
    {
        id: '3',
        title: 'Screenshot_2026-08-19_Window_Capture.png (1920x1080)',
        content: '[Image Binary Data: 1920x1080 Screenshot]',
        type: 'image',
        tag: 'Image',
        time: '5m ago',
        starred: true,
        icon: 'image'
    },
    {
        id: '4',
        title: 'https://github.com/NguyenDuc2309/klipr/releases/latest',
        content: 'https://github.com/NguyenDuc2309/klipr/releases/latest',
        type: 'text',
        tag: 'URL',
        time: '12m ago',
        starred: false,
        icon: 'link'
    },
    {
        id: '5',
        title: 'sudo apt update && sudo apt install gir1.2-gtk-4.0 python3-pil',
        content: 'sudo apt update && sudo apt install gir1.2-gtk-4.0 python3-pil',
        type: 'code',
        tag: 'Bash',
        time: '25m ago',
        starred: false,
        icon: 'terminal'
    },
    {
        id: '6',
        title: '🎨 Primary Brand Palette: #58a6ff | #3fb950 | #a855f7',
        content: '#58a6ff #3fb950 #a855f7',
        type: 'text',
        tag: 'Color',
        time: '1h ago',
        starred: true,
        icon: 'color'
    }
];

function initClipboardDemo() {
    const listContainer = document.getElementById('demo-clips-container');
    const searchInput = document.getElementById('demo-search');
    const tabs = document.querySelectorAll('.demo-tab-btn');
    if (!listContainer) return;

    let currentFilter = 'all';
    let searchQuery = '';

    function renderClips() {
        const filtered = mockClips.filter(clip => {
            const matchesTab = currentFilter === 'all' || 
                (currentFilter === 'starred' && clip.starred) || 
                (currentFilter === clip.type);
            const matchesSearch = clip.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                clip.tag.toLowerCase().includes(searchQuery.toLowerCase());
            return matchesTab && matchesSearch;
        });

        if (filtered.length === 0) {
            listContainer.innerHTML = `
                <div style="text-align:center; padding: 36px 0; color: var(--text-muted);">
                    <p style="font-size: 0.95rem;">No matching clips found in history.</p>
                </div>
            `;
            return;
        }

        listContainer.innerHTML = filtered.map(clip => `
            <div class="demo-clip-item" data-clip-content="${escapeHtml(clip.content)}" title="Click to copy">
                <div class="demo-clip-left">
                    <div class="demo-clip-icon">
                        ${getClipIcon(clip.icon)}
                    </div>
                    <div class="demo-clip-info">
                        <div class="demo-clip-title">${escapeHtml(clip.title)}</div>
                        <div class="demo-clip-meta">
                            <span class="demo-clip-tag">${clip.tag}</span>
                            <span>&bull;</span>
                            <span>${clip.time}</span>
                        </div>
                    </div>
                </div>
                <div class="demo-clip-actions">
                    <button class="demo-star-btn ${clip.starred ? 'starred' : ''}" data-star-id="${clip.id}" title="${clip.starred ? 'Unpin favorite' : 'Pin to favorites'}" onclick="event.stopPropagation(); toggleStar('${clip.id}')">
                        <svg width="16" height="16" fill="${clip.starred ? 'currentColor' : 'none'}" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                        </svg>
                    </button>
                    <span class="demo-copy-badge">Copy</span>
                </div>
            </div>
        `).join('');

        // Attach click to copy
        listContainer.querySelectorAll('.demo-clip-item').forEach(item => {
            item.addEventListener('click', async () => {
                const text = item.getAttribute('data-clip-content');
                if (text) {
                    try {
                        await navigator.clipboard.writeText(text);
                        showToast('Copied snippet from Klipr!');
                    } catch {
                        showToast('Copied to clipboard!');
                    }
                }
            });
        });
    }

    window.toggleStar = function(id) {
        const item = mockClips.find(c => c.id === id);
        if (item) {
            item.starred = !item.starred;
            renderClips();
        }
    };

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value;
            renderClips();
        });
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentFilter = tab.getAttribute('data-tab');
            renderClips();
        });
    });

    renderClips();
}

function getClipIcon(type) {
    switch (type) {
        case 'terminal':
            return `<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`;
        case 'code':
            return `<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>`;
        case 'image':
            return `<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`;
        case 'link':
            return `<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/></svg>`;
        default:
            return `<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>`;
    }
}

function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
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
 * Dynamic GitHub Release & Stars Fetching
 */
async function fetchLatestRelease() {
    const repo = 'NguyenDuc2309/klipr';
    const downloadBtn = document.getElementById('download-deb-btn');
    const badgeVersion = document.getElementById('latest-version-badge');
    const installCmdBlock = document.getElementById('install-code-box');
    const installCmdText = document.getElementById('install-cmd-text');

    try {
        const response = await fetch(`https://api.github.com/repos/${repo}/releases/latest`);
        if (!response.ok) return;

        const release = await response.json();
        const tag = release.tag_name || 'v1.2.3';

        if (badgeVersion) {
            badgeVersion.textContent = `${tag} — Latest Release`;
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
