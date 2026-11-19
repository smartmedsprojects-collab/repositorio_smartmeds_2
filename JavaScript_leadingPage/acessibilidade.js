(() => {
    'use strict';

    const root = document.documentElement;
    const body = document.body;
    const trigger = document.getElementById('accessibilityTrigger');
    const panel = document.getElementById('accessibilityPanel');
    const closeButton = document.getElementById('accessibilityClose');
    const status = document.getElementById('accessibilityStatus');
    const main = document.querySelector('main');
    const storageKey = 'smartmeds-acessibilidade';

    if (!trigger || !panel) return;

    const defaults = { fontScale: 1, contrast: false, speech: true };
    let settings = { ...defaults };
    let keyboardNavigation = false;
    try {
        settings = { ...defaults, ...JSON.parse(localStorage.getItem(storageKey) || '{}') };
    } catch (_) { /* Mantém os padrões quando o armazenamento estiver indisponível. */ }

    function announce(message) {
        if (status) status.textContent = message;
    }

    function saveSettings() {
        try { localStorage.setItem(storageKey, JSON.stringify(settings)); } catch (_) { /* opcional */ }
    }

    function renderSettings() {
        root.style.fontSize = `${Math.round(settings.fontScale * 100)}%`;
        body.classList.toggle('accessibility-high-contrast', settings.contrast);
        panel.querySelector('[data-access-action="contrast"]')?.setAttribute('aria-pressed', String(settings.contrast));
        const speechButton = panel.querySelector('[data-access-action="speech"]');
        if (speechButton) {
            speechButton.setAttribute('aria-pressed', String(settings.speech));
            const state = speechButton.querySelector('.accessibility-state');
            if (state) state.textContent = settings.speech ? 'Ativado' : 'Desativado';
        }
    }

    function openPanel() {
        panel.hidden = false;
        trigger.setAttribute('aria-expanded', 'true');
        trigger.setAttribute('aria-label', 'Fechar painel de acessibilidade');
        panel.querySelector('button')?.focus();
    }

    function closePanel(returnFocus = true) {
        panel.hidden = true;
        trigger.setAttribute('aria-expanded', 'false');
        trigger.setAttribute('aria-label', 'Abrir painel de acessibilidade');
        if (returnFocus) trigger.focus();
    }

    trigger.addEventListener('click', () => panel.hidden ? openPanel() : closePanel(false));
    closeButton?.addEventListener('click', () => closePanel());
    document.addEventListener('keydown', event => {
        if (event.key === 'Tab') keyboardNavigation = true;
        if (event.key === 'Escape' && !panel.hidden) closePanel();
    });
    document.addEventListener('pointerdown', () => { keyboardNavigation = false; }, true);

    function stopSpeech() {
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    }

    function textForElement(element) {
        if (!element) return '';
        const explicit = element.getAttribute('aria-label');
        if (explicit) return explicit;
        if (element instanceof HTMLInputElement || element instanceof HTMLSelectElement || element instanceof HTMLTextAreaElement) {
            const label = element.labels ? Array.from(element.labels).map(item => item.innerText.trim()).join('. ') : '';
            const value = element.type === 'password' ? 'Campo de senha' : (element.value || element.placeholder || '');
            const required = element.required ? 'Campo obrigatório.' : '';
            return [label, value, required].filter(Boolean).join('. ');
        }
        if (element instanceof HTMLImageElement) return element.alt || '';
        return (element.innerText || element.textContent || '').replace(/\s+/g, ' ').trim();
    }

    function speak(text) {
        if (!settings.speech || !text || !('speechSynthesis' in window)) return;
        stopSpeech();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'pt-BR';
        utterance.rate = 1;
        window.speechSynthesis.speak(utterance);
    }

    // Torna os blocos textuais navegáveis por Tab sem interferir em controles interativos.
    function prepareReadableBlocks(scope = main) {
        if (!scope) return;
        const selector = 'h1,h2,h3,h4,h5,h6,p,li,td,th,label,legend,figcaption,blockquote,span,strong,small,.form-text,.lead,.card-title,.card-text,.list-group-item,.alert';
        scope.querySelectorAll(selector).forEach(element => {
            if (element.closest('[hidden],[aria-hidden="true"]')) return;
            if (element !== scope && element.parentElement?.closest('[data-accessibility-readable]')) return;
            if (element.closest('a,button,input,select,textarea,label,[contenteditable="true"]') !== element && element.closest('a,button,input,select,textarea,label,[contenteditable="true"]')) return;
            if (element.querySelector('a,button,input,select,textarea,[contenteditable="true"]')) return;
            if (!(element.innerText || '').trim()) return;
            if (!element.hasAttribute('tabindex')) element.setAttribute('tabindex', '0');
            element.setAttribute('data-accessibility-readable', 'true');
        });
    }

    if (main) {
        prepareReadableBlocks();
        if ('MutationObserver' in window) {
            const observer = new MutationObserver(() => prepareReadableBlocks());
            observer.observe(main, { childList: true, subtree: true });
        }
    }

    // A fala acompanha o foco em qualquer área do sistema, inclusive menu e formulários.
    document.addEventListener('focusin', event => {
        if (!keyboardNavigation) return;
        const target = event.target;
        if (!target || !target.matches) return;
        if (target.matches('[data-accessibility-readable],a,button,input,select,textarea,[role="button"]')) {
            speak(textForElement(target));
        }
    });

    panel.addEventListener('click', event => {
        const button = event.target.closest('[data-access-action]');
        if (!button) return;
        const action = button.dataset.accessAction;

        switch (action) {
            case 'increase-font':
                settings.fontScale = Math.min(1.5, +(settings.fontScale + 0.1).toFixed(2));
                announce(`Texto aumentado para ${Math.round(settings.fontScale * 100)} por cento.`);
                break;
            case 'decrease-font':
                settings.fontScale = Math.max(0.9, +(settings.fontScale - 0.1).toFixed(2));
                announce(`Texto ajustado para ${Math.round(settings.fontScale * 100)} por cento.`);
                break;
            case 'contrast':
                settings.contrast = !settings.contrast;
                announce(settings.contrast ? 'Alto contraste ativado.' : 'Alto contraste desativado.');
                break;
            case 'speech':
                settings.speech = !settings.speech;
                if (!settings.speech) stopSpeech();
                announce(settings.speech ? 'Leitura automática ao navegar ativada.' : 'Leitura automática ao navegar desativada.');
                break;
            case 'stop-speech':
                stopSpeech();
                announce('Leitura interrompida.');
                break;
            case 'reset':
                settings = { ...defaults };
                stopSpeech();
                announce('Preferências de acessibilidade restauradas.');
                break;
        }
        renderSettings();
        saveSettings();
    });

    renderSettings();
})();
