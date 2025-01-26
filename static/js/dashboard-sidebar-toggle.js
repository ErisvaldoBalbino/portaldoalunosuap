// Inicializa o sidebar expandido
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const toggleButton = document.getElementById('sidebarToggle')

// Função para atualizar a posição do botão toggle
function updateTogglePosition() {
    if (window.innerWidth <= 768) {
        if (sidebar.classList.contains('active')) {
            toggleButton.style.left = '290px';
        } else {
            toggleButton.style.left = '1rem';
        }
    } else {
        if (sidebar.classList.contains('active')) {
            toggleButton.style.left = '1rem';
        } else {
            toggleButton.style.left = '260px';
        }
    }
};

// Event listener para o botão toggle
toggleButton.addEventListener('click', function() {
    sidebar.classList.toggle('active');
    mainContent.classList.toggle('expanded');
    updateTogglePosition();
});

// Atualiza a posição do botão quando a janela é redimensionada
window.addEventListener('resize', updateTogglePosition)

// Posiciona o botão inicialmente
updateTogglePosition();