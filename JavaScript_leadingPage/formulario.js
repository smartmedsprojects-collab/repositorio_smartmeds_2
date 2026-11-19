// Envia o formulário de contato da landing page para o e-mail SmartMeds.
// O serviço FormSubmit exige uma confirmação inicial do endereço destinatário.
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('formContato');
    const status = document.getElementById('statusFormulario');

    if (!form || !status) return;

    const botao = form.querySelector('button[type="submit"]');
    const textoOriginal = botao ? botao.textContent.trim() : 'Enviar mensagem';

    form.addEventListener('submit', async (evento) => {
        evento.preventDefault();
        status.textContent = '';
        status.className = 'form-status';

        if (!form.checkValidity()) {
            form.reportValidity();
            status.textContent = 'Confira os campos obrigatórios e tente novamente.';
            status.classList.add('form-status-error');
            return;
        }

        if (botao) {
            botao.disabled = true;
            botao.textContent = 'Enviando...';
        }

        try {
            const resposta = await fetch('https://formsubmit.co/ajax/smartmedsprojects@gmail.com', {
                method: 'POST',
                body: new FormData(form),
                headers: { 'Accept': 'application/json' }
            });

            const resultado = await resposta.json().catch(() => ({}));
            const mensagem = String(resultado.message || '').toLowerCase();
            const envioConfirmado = resposta.ok && (
                resultado.success === 'true' || resultado.success === true ||
                mensagem.includes('success') || mensagem.includes('successful')
            );

            if (!envioConfirmado) {
                throw new Error(resultado.message || 'Não foi possível confirmar o envio.');
            }

            form.reset();
            status.textContent = 'Mensagem enviada com sucesso! A equipe SmartMeds entrará em contato.';
            status.classList.add('form-status-success');
        } catch (erro) {
            console.error('Erro ao enviar formulário:', erro);
            status.textContent = 'Não foi possível enviar sua mensagem agora. Tente novamente ou escreva para smartmedsprojects@gmail.com.';
            status.classList.add('form-status-error');
        } finally {
            if (botao) {
                botao.disabled = false;
                botao.textContent = textoOriginal;
            }
        }
    });
});
