// Picking an employee loads their details; changing the month clears the employee.
document.getElementById('empSel').addEventListener('change', () => document.getElementById('detailForm').submit());
document.getElementById('monthSel').addEventListener('change', () => {
    document.getElementById('empSel').value = '';
    document.getElementById('detailForm').submit();
});