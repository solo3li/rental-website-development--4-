/**
 * CAIRO STUDENT HOUSING — DJANGO ADMIN RECEIPT LIGHTBOX & UX ENHANCEMENTS
 */

(function () {
    'use strict';

    let currentZoom = 1;
    let currentRotation = 0;

    function createLightboxDOM() {
        if (document.getElementById('receiptLightboxOverlay')) return;

        const overlay = document.createElement('div');
        overlay.id = 'receiptLightboxOverlay';
        overlay.className = 'receipt-lightbox-overlay';

        overlay.innerHTML = `
            <div class="receipt-lightbox-modal" role="dialog" aria-modal="true">
                <div class="receipt-lightbox-header">
                    <div class="receipt-lightbox-title">
                        <span>🧾 معاينة إيصال التحويل:</span>
                        <strong id="lightboxStudentTitle" style="color: #38bdf8;"></strong>
                    </div>
                    <div class="receipt-lightbox-toolbar">
                        <button type="button" class="lightbox-btn" id="lightboxZoomIn" title="تكبير">+</button>
                        <button type="button" class="lightbox-btn" id="lightboxZoomOut" title="تصغير">-</button>
                        <button type="button" class="lightbox-btn" id="lightboxRotate" title="تدوير 90 درجة">⟳ تدوير</button>
                        <button type="button" class="lightbox-btn" id="lightboxReset" title="إعادة الضبط">↺ الأصل</button>
                        <a id="lightboxOpenFull" href="#" target="_blank" class="lightbox-btn" style="text-decoration:none;" title="فتح في تبويب منفصل">↗ كامل</a>
                        <button type="button" class="lightbox-btn lightbox-btn-close" id="lightboxClose" title="إغلاق (Esc)">✕ إغلاق</button>
                    </div>
                </div>
                <div class="receipt-lightbox-body">
                    <img id="lightboxImage" class="receipt-lightbox-img" src="" alt="إيصال التحويل" />
                </div>
            </div>
        `;

        document.body.appendChild(overlay);

        // Bind Controls
        const img = document.getElementById('lightboxImage');
        const zoomInBtn = document.getElementById('lightboxZoomIn');
        const zoomOutBtn = document.getElementById('lightboxZoomOut');
        const rotateBtn = document.getElementById('lightboxRotate');
        const resetBtn = document.getElementById('lightboxReset');
        const closeBtn = document.getElementById('lightboxClose');

        function updateTransform() {
            img.style.transform = `scale(${currentZoom}) rotate(${currentRotation}deg)`;
        }

        zoomInBtn.addEventListener('click', () => {
            currentZoom = Math.min(currentZoom + 0.25, 3.0);
            updateTransform();
        });

        zoomOutBtn.addEventListener('click', () => {
            currentZoom = Math.max(currentZoom - 0.25, 0.5);
            updateTransform();
        });

        rotateBtn.addEventListener('click', () => {
            currentRotation = (currentRotation + 90) % 360;
            updateTransform();
        });

        resetBtn.addEventListener('click', () => {
            currentZoom = 1;
            currentRotation = 0;
            updateTransform();
        });

        function closeModal() {
            overlay.classList.remove('active');
            currentZoom = 1;
            currentRotation = 0;
            updateTransform();
            img.src = '';
        }

        closeBtn.addEventListener('click', closeModal);

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closeModal();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && overlay.classList.contains('active')) {
                closeModal();
            }
        });
    }

    function openLightbox(src, title) {
        createLightboxDOM();
        const overlay = document.getElementById('receiptLightboxOverlay');
        const img = document.getElementById('lightboxImage');
        const titleEl = document.getElementById('lightboxStudentTitle');
        const openFull = document.getElementById('lightboxOpenFull');

        img.src = src;
        titleEl.textContent = title || 'إيصال دفع';
        openFull.href = src;
        overlay.classList.add('active');
    }

    function initReceiptTriggers() {
        document.addEventListener('click', (e) => {
            const trigger = e.target.closest('.receipt-lightbox-trigger');
            if (trigger) {
                e.preventDefault();
                const src = trigger.getAttribute('data-lightbox-src') || trigger.getAttribute('href');
                const title = trigger.getAttribute('data-student') || '';
                if (src) {
                    openLightbox(src, title);
                }
            }
        });
    }

    function initQuickRejectPrompt() {
        document.addEventListener('click', (e) => {
            const rejectBtn = e.target.closest('.action-btn-reject');
            if (rejectBtn) {
                e.preventDefault();
                const defaultReason = 'إيصال غير مطابق أو صورة غير واضحة';
                const reason = prompt('يرجى توضيح سبب رفض الإيصال لإبلاغ الطالب:', defaultReason);
                
                if (reason === null) {
                    // Admin pressed cancel
                    return;
                }

                const trimmedReason = reason.trim() || defaultReason;
                let targetUrl = rejectBtn.getAttribute('href');
                const separator = targetUrl.includes('?') ? '&' : '?';
                targetUrl += `${separator}reason=${encodeURIComponent(trimmedReason)}`;
                window.location.href = targetUrl;
            }
        });
    }

    // Initialize on DOM Ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initReceiptTriggers();
            initQuickRejectPrompt();
        });
    } else {
        initReceiptTriggers();
        initQuickRejectPrompt();
    }
})();
