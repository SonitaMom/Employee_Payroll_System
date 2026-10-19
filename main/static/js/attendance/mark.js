(function () {
  const dlg  = document.getElementById('markDialog');
  const form = document.getElementById('markForm');
  if (!dlg || !form) return;

  const $ = (id) => document.getElementById(id);
  const inEl  = $('m_in');
  const outEl = $('m_out');
  const st    = $('m_status');
  const err   = $('m_err');
  const shiftEnd = dlg.dataset.shiftEnd || '17:00';

  const toMin = (t) => { const p = t.split(':'); return +p[0] * 60 + +p[1]; };
  const pad   = (n) => String(n).padStart(2, '0');

  // Only "Present" has check-in / check-out and overtime
  const works = () => st.value.toLowerCase() === 'present';

  // Enable or disable the time boxes and update the overtime box
  function sync() {
    const w = works();
    inEl.disabled = outEl.disabled = !w;
    if (!w) { inEl.value = ''; outEl.value = ''; }

    let ot = 0;
    if (w && outEl.value && toMin(outEl.value) > toMin(shiftEnd)) {
      ot = toMin(outEl.value) - toMin(shiftEnd);
    }
    $('m_ot').textContent = ot
      ? '+' + (Math.floor(ot / 60) ? Math.floor(ot / 60) + 'h ' : '') + pad(ot % 60) + 'm'
      : '-';
  }

  // Open the popup from any Mark / Edit button
  document.addEventListener('click', function (e) {
    const b = e.target.closest('[data-mark]');
    if (!b) return;

    form.action = b.dataset.url;
    $('m_name').textContent = b.dataset.name;
    $('m_sub').textContent  = b.dataset.dept;
    const want = (b.dataset.status || '').trim().toLowerCase();
st.value = '';
for (const o of st.options) {
  if (o.value.trim().toLowerCase() === want) { st.value = o.value; break; }
}
    inEl.value  = b.dataset.in  || '';
    outEl.value = b.dataset.out || '';
    $('m_clear').hidden = !b.dataset.status;   // show "Clear mark" only if already marked
    err.textContent = '';
    sync();
    dlg.showModal();
  });

  // "Now" buttons, and click on the dark background to close
  dlg.addEventListener('click', function (e) {
    const n = e.target.closest('[data-now]');
    if (n) {
      const d = new Date();
      $(n.dataset.now).value = pad(d.getHours()) + ':' + pad(d.getMinutes());
      sync();
    }
    if (e.target === dlg) dlg.close();
  });

  st.addEventListener('change', function () { err.textContent = ''; sync(); });
  outEl.addEventListener('input', sync);
  $('m_cancel').addEventListener('click', function () { dlg.close(); });

  // Checks before saving
  form.addEventListener('submit', function (e) {
    if (e.submitter && e.submitter.name === 'clear') return;   // "Clear mark" skips the checks

    if (!st.value) {
      e.preventDefault(); err.textContent = 'Choose a status first.'; return;
    }
    if (works() && !inEl.value) {
      e.preventDefault(); err.textContent = 'Enter the check-in time.'; return;
    }
    if (works() && inEl.value && outEl.value && outEl.value <= inEl.value) {
      e.preventDefault(); err.textContent = 'Check-out must be after check-in.';
    }
  });
})();