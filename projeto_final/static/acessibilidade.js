(() => {
    'use strict';

    const body = document.body;
    const root = document.documentElement;
    const trigger = document.getElementById('abrirAcessibilidade');
    const panel = document.getElementById('painelAcessibilidade');
    const closeButton = document.getElementById('fecharAcessibilidade');
    const backdrop = document.getElementById('fundoAcessibilidade');
    const status = document.getElementById('statusAcessibilidade');
    const main = document.getElementById('conteudo-principal') || document.querySelector('main');
    const storageKey = 'smartmeds-acessibilidade-v2';

    if (!trigger || !panel || !backdrop) return;

    const defaults = {
        font: 'normal',
        contrast: false,
        monochrome: false,
        tabReading: false
    };
    let settings = { ...defaults };
    let keyboardNavigation = false;
    let speechQueue = [];
    let speechActive = false;
    let speechToken = 0;

    try {
        const saved = JSON.parse(localStorage.getItem(storageKey) || '{}');
        settings = { ...defaults, ...saved };
        if (!['smaller', 'normal', 'larger'].includes(settings.font)) settings.font = 'normal';
    } catch (_) {
        settings = { ...defaults };
    }

    const fontSizes = { smaller: '90%', normal: '100%', larger: '115%' };

    function announce(message) {
        if (status) status.textContent = message;
    }

    function saveSettings() {
        try {
            localStorage.setItem(storageKey, JSON.stringify(settings));
        } catch (_) {
            // O recurso continua funcionando mesmo quando o navegador bloqueia o armazenamento.
        }
    }

    function renderSettings() {
        root.style.fontSize = fontSizes[settings.font];
        body.classList.toggle('accessibility-high-contrast', settings.contrast);
        body.classList.toggle('accessibility-monochrome', settings.monochrome);

        panel.querySelectorAll('[data-font]').forEach(button => {
            const selected = button.dataset.font === settings.font;
            button.setAttribute('aria-pressed', String(selected));
        });
        document.getElementById('alternarContraste')?.setAttribute('aria-pressed', String(settings.contrast));
        document.getElementById('alternarMono')?.setAttribute('aria-pressed', String(settings.monochrome));
        document.getElementById('leituraTab')?.setAttribute('aria-pressed', String(settings.tabReading));
    }

    function openPanel() {
        panel.hidden = false;
        panel.removeAttribute('inert');
        panel.setAttribute('aria-hidden', 'false');
        backdrop.hidden = false;
        trigger.setAttribute('aria-expanded', 'true');
        trigger.setAttribute('aria-label', 'Fechar painel de acessibilidade');
        closeButton?.focus();
    }

    function closePanel(returnFocus = true) {
        panel.hidden = true;
        panel.setAttribute('inert', '');
        panel.setAttribute('aria-hidden', 'true');
        backdrop.hidden = true;
        trigger.setAttribute('aria-expanded', 'false');
        trigger.setAttribute('aria-label', 'Abrir painel de acessibilidade');
        if (returnFocus) trigger.focus();
    }

    trigger.addEventListener('click', () => {
        if (panel.hidden) openPanel();
        else closePanel(false);
    });
    closeButton?.addEventListener('click', () => closePanel());
    backdrop.addEventListener('click', () => closePanel());

    function stopSpeech() {
        speechToken += 1;
        speechQueue = [];
        speechActive = false;
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    }

    function speakChunks(chunks) {
        if (!('speechSynthesis' in window) || typeof SpeechSynthesisUtterance === 'undefined') {
            announce('A leitura em voz alta não é suportada neste navegador.');
            return;
        }
        stopSpeech();
        speechQueue = chunks.filter(Boolean);
        speechActive = speechQueue.length > 0;
        const currentToken = speechToken;
        speakNext(currentToken);
    }

    function speakNext(token) {
        if (token !== speechToken || !speechQueue.length) {
            speechActive = false;
            return;
        }
        const text = speechQueue.shift();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'pt-BR';
        utterance.rate = 1;
        utterance.onend = () => speakNext(token);
        utterance.onerror = () => speakNext(token);
        window.speechSynthesis.speak(utterance);
    }

    function splitText(text, limit = 210) {
        const sentences = text.match(/[^.!?]+[.!?]?/g) || [text];
        const chunks = [];
        let current = '';

        sentences.forEach(sentence => {
            const clean = sentence.trim();
            if (!clean) return;
            if ((current + ' ' + clean).trim().length <= limit) {
                current = (current + ' ' + clean).trim();
                return;
            }
            if (current) chunks.push(current);
            if (clean.length <= limit) {
                current = clean;
                return;
            }
            const words = clean.split(/\s+/);
            current = '';
            words.forEach(word => {
                if ((current + ' ' + word).trim().length > limit) {
                    if (current) chunks.push(current);
                    current = word;
                } else {
                    current = (current + ' ' + word).trim();
                }
            });
        });
        if (current) chunks.push(current);
        return chunks;
    }

    function textForElement(element) {
        if (!element) return '';
        const explicit = element.getAttribute('aria-label') || element.getAttribute('title');
        if (explicit) return explicit.trim();

        if (element instanceof HTMLInputElement || element instanceof HTMLSelectElement || element instanceof HTMLTextAreaElement) {
            const label = element.labels
                ? Array.from(element.labels).map(item => item.innerText.trim()).filter(Boolean).join('. ')
                : '';
            const value = element.type === 'password' ? 'Campo de senha' : (element.value || element.placeholder || '');
            const required = element.required ? 'Campo obrigatório.' : '';
            return [label, value, required].filter(Boolean).join('. ');
        }
        if (element instanceof HTMLImageElement) return element.alt || '';
        return (element.innerText || element.textContent || '').replace(/\s+/g, ' ').trim();
    }

    function speakFocusedElement(element) {
        const text = textForElement(element);
        if (text) speakChunks([text]);
    }

    function prepareReadableBlocks(scope = main) {
        if (!scope || !scope.querySelectorAll) return;
        const selector = 'h1,h2,h3,h4,h5,h6,p,li,td,th,figcaption,blockquote,legend,.form-text,.lead,.card-title,.card-text,.alert';
        scope.querySelectorAll(selector).forEach(element => {
            if (element.closest('[hidden],[aria-hidden="true"],[inert]')) return;
            if (element.closest('a,button,input,select,textarea,[contenteditable="true"]')) return;
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

    document.addEventListener('keydown', event => {
        if (event.key === 'Tab') keyboardNavigation = true;
        if (event.key === 'Escape' && !panel.hidden) closePanel();

        // Mantém o foco dentro do painel enquanto ele estiver aberto.
        if (event.key === 'Tab' && !panel.hidden) {
            const focusable = Array.from(panel.querySelectorAll('button:not([disabled]),a[href],input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])'))
                .filter(element => !element.hasAttribute('hidden'));
            if (!focusable.length) return;
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        }
    });
    document.addEventListener('pointerdown', () => { keyboardNavigation = false; }, true);

    document.addEventListener('focusin', event => {
        if (!keyboardNavigation || !settings.tabReading) return;
        const target = event.target;
        if (!target || !target.matches) return;
        if (target.matches('[data-accessibility-readable],a,button,input,select,textarea,[role="button"]')) {
            speakFocusedElement(target);
        }
    });

    panel.addEventListener('click', event => {
        const fontButton = event.target.closest('[data-font]');
        if (fontButton) {
            settings.font = fontButton.dataset.font;
            announce(settings.font === 'normal' ? 'Tamanho normal restaurado.' : settings.font === 'larger' ? 'Texto aumentado.' : 'Texto diminuído.');
            renderSettings();
            saveSettings();
            return;
        }

        const button = event.target.closest('button');
        if (!button) return;

        switch (button.id) {
            case 'alternarContraste':
                settings.contrast = !settings.contrast;
                announce(settings.contrast ? 'Alto contraste ativado.' : 'Alto contraste desativado.');
                break;
            case 'alternarMono':
                settings.monochrome = !settings.monochrome;
                announce(settings.monochrome ? 'Modo monocromático ativado.' : 'Modo monocromático desativado.');
                break;
            case 'leituraTab':
                settings.tabReading = !settings.tabReading;
                announce(settings.tabReading ? 'Leitura ao navegar com Tab ativada.' : 'Leitura ao navegar com Tab desativada.');
                break;
            case 'lerPagina': {
                if (!main) {
                    announce('Não foi encontrado conteúdo para leitura nesta página.');
                    break;
                }
                const clone = main.cloneNode(true);
                clone.querySelectorAll('script,style,button,input,select,textarea,[aria-hidden="true"],[hidden],[data-no-reading]').forEach(node => node.remove());
                const pageText = (clone.innerText || clone.textContent || '').replace(/\s+/g, ' ').trim();
                if (!pageText) {
                    announce('Não há conteúdo disponível para leitura.');
                    break;
                }
                announce('Iniciando a leitura do conteúdo da página.');
                speakChunks(splitText(pageText));
                break;
            }
            case 'pararLeitura':
                stopSpeech();
                announce('Leitura interrompida.');
                break;
            case 'restaurarAcessibilidade':
                stopSpeech();
                settings = { ...defaults };
                renderSettings();
                saveSettings();
                announce('Preferências de acessibilidade restauradas.');
                return;
        }
        renderSettings();
        saveSettings();
    });

    renderSettings();
})();
