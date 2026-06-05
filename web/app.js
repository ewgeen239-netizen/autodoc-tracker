function sendData() {
    const date = document.getElementById('date').value || new Date().toISOString().split('T')[0];
    const pieces = parseInt(document.getElementById('pieces').value);
    const hours = parseFloat(document.getElementById('hours').value);
    const station = document.getElementById('station').value;

    if (!pieces || !hours) {
        document.getElementById('result').innerText = 'Заполни пики и часы';
        return;
    }

    Telegram.WebApp.sendData(JSON.stringify({date, pieces, hours, station}));
    document.getElementById('result').innerText = '✅ Отправлено!';
}