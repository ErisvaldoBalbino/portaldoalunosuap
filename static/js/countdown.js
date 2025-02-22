document.addEventListener('DOMContentLoaded', function() {
    // Data das férias
    const endDate = new Date('2025-03-11T00:00:00').getTime();

    // Atualiza o contador a cada segundo
    const countdown = setInterval(function() {
        const now = new Date().getTime();
        const distance = endDate - now;

        // Cálculos para dias, horas, minutos e segundos
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Atualiza os elementos HTML
        document.getElementById('countdown-days').textContent = days;
        document.getElementById('countdown-hours').textContent = hours;
        document.getElementById('countdown-minutes').textContent = minutes;
        document.getElementById('countdown-seconds').textContent = seconds;

        // Se o contador chegou ao fim
        if (distance < 0) {
            clearInterval(countdown);
            document.getElementById('countdown-days').textContent = '0';
            document.getElementById('countdown-hours').textContent = '0';
            document.getElementById('countdown-minutes').textContent = '0';
            document.getElementById('countdown-seconds').textContent = '0';
        }
    }, 1000);
}); 