// Track list: poll running analyses and confirm deletes in a native <dialog>.
(function () {
    // Poll the status of running analyses.
    const banner = document.getElementById('active-banner');
    const items = banner ? banner.querySelectorAll('.active-item') : [];
    if (items.length) {
        const poll = () => {
            items.forEach((item) => {
                const trackId = item.dataset.trackId;
                if (!trackId) return;
                fetch('/analyse/status/' + encodeURIComponent(trackId))
                    .then((r) => r.json())
                    .then((data) => {
                        const stepEl = item.querySelector('.active-step');
                        if (data.status === 'done') {
                            window.location.reload();
                        } else if (data.status === 'error') {
                            stepEl.textContent = 'Fout';
                            stepEl.classList.add('is-error');
                        } else if (data.step) {
                            stepEl.textContent = data.step;
                        }
                    })
                    .catch(() => {});
            });
        };
        setInterval(poll, 2000);
        poll();
    }

    // Delete confirmation. Without JavaScript the form submits directly.
    const dialog = document.getElementById('confirm-delete');
    if (!dialog || typeof dialog.showModal !== 'function') return;
    const nameEl = document.getElementById('confirm-delete-name');
    let pendingForm = null;

    document.addEventListener('submit', (event) => {
        const form = event.target;
        if (!(form instanceof HTMLFormElement) || !form.hasAttribute('data-confirm-delete')) return;
        event.preventDefault();
        pendingForm = form;
        nameEl.textContent = '"' + form.dataset.confirmDelete + '"';
        dialog.returnValue = '';
        dialog.showModal();
    });

    dialog.addEventListener('close', () => {
        const confirmed = dialog.returnValue === 'delete';
        dialog.returnValue = '';
        if (confirmed && pendingForm) pendingForm.submit();
        pendingForm = null;
    });

    // closedby="any" is not in every browser yet: add click-outside-to-close where it is missing.
    if (!('closedBy' in HTMLDialogElement.prototype)) {
        const outside = (e) => {
            const r = dialog.getBoundingClientRect();
            return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
        };
        let pressedOutside = false;
        dialog.addEventListener('pointerdown', (e) => { pressedOutside = outside(e); });
        dialog.addEventListener('pointerup', (e) => { if (pressedOutside && outside(e)) dialog.close(); });
    }
})();
