// Pay modal
document.querySelectorAll('.pay-btn').forEach(b => b.addEventListener('click', () => {
    document.getElementById('payForm').action = b.dataset.url;
    document.getElementById('payName').textContent = b.dataset.name;
    document.getElementById('payAmount').textContent = '($' + b.dataset.amount + ')';
    document.querySelectorAll('#payMethods input').forEach(i => i.checked = (i.value === b.dataset.method));
}));