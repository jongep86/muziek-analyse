// Polling for active analysis status
(function() {
    const banner = document.getElementById('active-banner');
    if (!banner) return;

    const items = banner.querySelectorAll('.active-item');
    if (!items.length) return;

    function poll() {
        items.forEach(item => {
            const trackId = item.dataset.trackId;
            if (!trackId) return;

            fetch('/analyse/status/' + trackId)
                .then(r => r.json())
                .then(data => {
                    const stepEl = item.querySelector('.active-step');
                    if (data.status === 'done') {
                        // Reload page to show completed track
                        window.location.reload();
                    } else if (data.status === 'error') {
                        stepEl.textContent = 'Fout!';
                        stepEl.style.color = '#e74c3c';
                    } else if (data.step) {
                        stepEl.textContent = data.step;
                    }
                })
                .catch(() => {});
        });
    }

    setInterval(poll, 2000);
    poll();
})();
