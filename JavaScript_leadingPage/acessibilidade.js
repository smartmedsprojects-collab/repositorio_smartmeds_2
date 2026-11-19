(() => {
    const body = document.body;
    const panel = document.getElementById('painelAcessibilidade');
    const trigger = document.getElementById('abrirAcessibilidade');
    const closeButton = document.getElementById('fecharAcessibilidade');
    const backdrop = document.getElementById('fundoAcessibilidade');
    const status = document.getElementById('statusAcessibilidade');
    const speech = window.speechSynthesis;
    let readOnTab = false;
    let previousFocus = null;

    const announce = message => { if (status) status.textContent = message; };
    const speak = text => {
        if (!speech || !text) return;
        speech.cancel();
        const utterance = new SpeechSynthesisUtterance(text.trim().slice(0, 900));
        utterance.lang = 'pt-BR';
        speech.speak(utterance);
    };
    const stopSpeech = () => { if (speech) speech.cancel(); };

    function openPanel() {
        previousFocus = document.activeElement;
        panel.classList.add('is-open');
        panel.removeAttribute('inert');
        panel.setAttribute('aria-hidden', 'false');
        trigger.setAttribute('aria-expanded', 'true');
        backdrop.hidden = false;
        closeButton.focus();
    }
    function closePanel() {
        panel.classList.remove('is-open');
        panel.setAttribute('aria-hidden', 'true');
        panel.setAttribute('inert', '');
        trigger.setAttribute('aria-expanded', 'false');
        backdrop.hidden = true;
        if (previousFocus) previousFocus.focus();
    }
    trigger.addEventListener('click', openPanel);
    closeButton.addEventListener('click', closePanel);
    backdrop.addEventListener('click', closePanel);
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && panel.classList.contains('is-open')) closePanel();
        if (event.key === 'Tab' && panel.classList.contains('is-open')) {
            const items = [...panel.querySelectorAll('button:not([disabled])')];
            const first = items[0], last = items[items.length - 1];
            if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
            else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
        }
    });

    document.querySelectorAll('[data-font]').forEach(button => {
        button.addEventListener('click', () => {
            body.classList.remove('accessibility-font-small', 'accessibility-font-normal', 'accessibility-font-large');
            const value = button.dataset.font;
            body.classList.add(`accessibility-font-${value}`);
            document.querySelectorAll('[data-font]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
            announce('Tamanho do texto atualizado.');
        });
    });

    function toggleMode(id, className, label) {
        const button = document.getElementById(id);
        button.addEventListener('click', () => {
            const active = body.classList.toggle(className);
            button.setAttribute('aria-pressed', String(active));
            announce(`${label} ${active ? 'ativado' : 'desativado'}.`);
        });
    }
    toggleMode('alternarContraste', 'accessibility-contrast', 'Alto contraste');
    toggleMode('alternarMono', 'accessibility-monochrome', 'Modo monocromático');

    const tabButton = document.getElementById('leituraTab');
    tabButton.addEventListener('click', () => {
        readOnTab = !readOnTab;
        tabButton.setAttribute('aria-pressed', String(readOnTab));
        if (!readOnTab) stopSpeech();
        announce(readOnTab ? 'Leitura por foco ativada. Use Tab para ouvir os elementos.' : 'Leitura por foco desativada.');
    });
    document.addEventListener('focusin', event => {
        if (!readOnTab || event.target.closest('#painelAcessibilidade')) return;
        const el = event.target;
        const text = el.getAttribute('aria-label') || el.getAttribute('title') || el.innerText || el.value || el.getAttribute('alt') || '';
        speak(text);
    });

    document.getElementById('lerPagina').addEventListener('click', () => {
        const main = document.querySelector('main');
        speak(main ? main.innerText : document.body.innerText);
        announce('Leitura da página iniciada.');
    });
    document.getElementById('pararLeitura').addEventListener('click', () => {
        stopSpeech(); announce('Leitura interrompida.');
    });
    document.getElementById('restaurarAcessibilidade').addEventListener('click', () => {
        body.classList.remove('accessibility-contrast', 'accessibility-monochrome', 'accessibility-font-small', 'accessibility-font-large');
        body.classList.add('accessibility-font-normal');
        readOnTab = false;
        stopSpeech();
        tabButton.setAttribute('aria-pressed', 'false');
        document.querySelectorAll('#alternarContraste, #alternarMono').forEach(button => button.setAttribute('aria-pressed', 'false'));
        document.querySelectorAll('[data-font]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.font === 'normal')));
        announce('Configurações restauradas.');
    });
})();
