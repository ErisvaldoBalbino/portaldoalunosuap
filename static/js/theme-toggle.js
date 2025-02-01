document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Função para definir o tema
    function setTheme(theme) {
        document.documentElement.dataset.theme = theme;
        localStorage.setItem('theme', theme);
        updateThemeIcon(theme);
    }
    
    // Função para atualizar o ícone
    function updateThemeIcon(theme) {
        const lightIcon = themeToggle.querySelector('.theme-icon-light');
        const darkIcon = themeToggle.querySelector('.theme-icon-dark');
        
        if (theme === 'dark') {
            lightIcon.style.display = 'none';
            darkIcon.style.display = 'inline-block';
        } else {
            lightIcon.style.display = 'inline-block';
            darkIcon.style.display = 'none';
        }
    }
    
    // Inicializar tema
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else if (prefersDarkScheme.matches) {
        setTheme('dark');
    } else {
        setTheme('light');
    }
    
    // Event listener para o botão de toggle
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.dataset.theme;
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });
    
    // Event listener para mudanças nas preferências do sistema
    prefersDarkScheme.addListener((e) => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}); 