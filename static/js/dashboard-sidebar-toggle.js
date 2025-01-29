// Inicializa o sidebar expandido
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const toggleButton = document.getElementById('sidebarToggle');

// Event listener para o botão toggle
toggleButton.addEventListener('click', function() {
    sidebar.classList.toggle('active');
    mainContent.classList.toggle('expanded');
    toggleButton.classList.toggle('active');
});

// Adiciona listener para redimensionamento da janela
window.addEventListener('resize', function() {
    // Apenas para garantir que o overlay seja removido em telas maiores
    if (window.innerWidth > 768) {
        mainContent.classList.remove('expanded');
        sidebar.classList.remove('active');
        toggleButton.classList.remove('active');
    }
});