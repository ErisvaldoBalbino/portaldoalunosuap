// Função para calcular média (2*N1 + 3*N2)/5
function calcularMedia(nota1, nota2) {
    if (!nota2) return (2 * nota1) / 5;
    return (2 * nota1 + 3 * nota2) / 5;
}

// Função para calcular média final
function calcularMediaFinal(mediaAtual, nota1, nota2, notaFinal) {
    // Opção 1: Média aritmética entre média parcial e nota final
    const mf1 = (mediaAtual + notaFinal) / 2;
    
    // Opção 2: Média ponderada entre nota final (peso 2) e N2 (peso 3)
    const mf2 = (2 * notaFinal + 3 * nota2) / 5;
    
    // Opção 3: Média ponderada entre N1 (peso 2) e nota final (peso 3)
    const mf3 = (2 * nota1 + 3 * notaFinal) / 5;
    
    // Retorna o melhor resultado
    return Math.max(mf1, mf2, mf3);
}

// Função para encontrar a nota necessária na final
function encontrarNotaNecessaria(mediaAtual, nota1, nota2) {
    let notaFinal = 0;
    while (notaFinal <= 100) {
        const mediaFinal = calcularMediaFinal(mediaAtual, nota1, nota2, notaFinal);
        if (mediaFinal >= 60) {
            return notaFinal;
        }
        notaFinal += 0.1;
    }
    return 100;
}

// Função para calcular nota necessária na N2
function calcularNota2Necessaria(nota1) {
    return (5 * 60 - 2 * nota1) / 3;
}

// Função para analisar situação e retornar HTML
function analisarSituacao(nota1, nota2) {
    const mediaAtual = calcularMedia(nota1, nota2);
    
    if (!nota2) {
        const nota2Necessaria = Math.ceil(calcularNota2Necessaria(nota1));
        return `${nota2Necessaria} na 2ª nota`;
    }
    
    const notaFinalNecessaria = Math.ceil(encontrarNotaNecessaria(mediaAtual, nota1, nota2));
    return `${notaFinalNecessaria} na final`;
}

// Inicializar cálculos quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    const disciplinas = document.querySelectorAll('[data-nota1]');
    disciplinas.forEach(disciplina => {
        const nota1 = parseFloat(disciplina.dataset.nota1) || 0;
        const nota2 = parseFloat(disciplina.dataset.nota2) || 0;
        const situacaoElement = disciplina.querySelector('.situacao-calculo');
        if (situacaoElement) {
            situacaoElement.innerHTML = analisarSituacao(nota1, nota2);
        }
    });
}); 