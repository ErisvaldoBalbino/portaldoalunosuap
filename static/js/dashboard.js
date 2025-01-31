// Função para mostrar o loading ao trocar de período
function showTableLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function changePeriod(value) {
    if (!value) return;
    
    showTableLoading();
    const [ano, periodo] = value.split('.');
    if (ano && periodo) {
        window.location.href = `?ano=${ano}&periodo=${periodo}`;
    }
}

// Função para calcular notas necessárias
function calcularNecessario(disciplina, nota1, nota2, cargaHoraria, faltas) {
    // Mostrar o card de cálculos
    const calculosCard = document.getElementById('calculosCard');
    calculosCard.style.display = 'block';
    calculosCard.scrollIntoView({ behavior: 'smooth' });

    // Atualizar informações básicas
    document.getElementById('disciplinaNome').textContent = disciplina;
    document.getElementById('nota1Atual').textContent = nota1 || '--';
    document.getElementById('nota2Atual').textContent = nota2 || '--';

    // Cálculo da média (2*N1 + 3*N2)/5
    const mediaAtual = nota2 ? ((2 * nota1 + 3 * nota2) / 5) : (2 * nota1 / 5);
    document.getElementById('mediaAtual').textContent = mediaAtual.toFixed(1);

    // Análise da situação
    let situacao = '';
    let necessidade = '';

    if (mediaAtual >= 60) {
        situacao = '<span class="status-approved">Aprovado por média!</span>';
        necessidade = '<p class="text-success">Você já está aprovado! 🎉</p>';
    } else if (!nota2) {
        // Cálculo da nota 2 necessária: (5*60 - 2*N1)/3
        const nota2Necessaria = (5 * 60 - 2 * nota1) / 3;
        situacao = '<span class="status-risk">Pendente</span>';
        necessidade = `
            <p>Para aprovação direta (média 60):</p>
            <p>Você precisa tirar <strong>${nota2Necessaria.toFixed(1)}</strong> na 2ª nota</p>
        `;
    } else {
        situacao = '<span class="status-risk">Precisa de Final</span>';
        const notaFinalNecessaria = encontrarNotaNecessaria(mediaAtual, nota1, nota2);
        
        necessidade = `
            <p>Você precisará fazer a prova final</p>
            <p>Nota necessária na final: <strong>${notaFinalNecessaria.toFixed(1)}</strong></p>
            <p class="text-muted small">A média final será calculada usando a melhor entre:</p>
            <ul class="text-muted small">
                <li>Média entre a média parcial e nota final</li>
                <li>Média ponderada entre nota final (peso 2) e N2 (peso 3)</li>
                <li>Média ponderada entre N1 (peso 2) e nota final (peso 3)</li>
            </ul>
        `;
    }

    document.getElementById('situacaoAtual').innerHTML = situacao;
    document.getElementById('necessidadeNotas').innerHTML = necessidade;

    // Cálculos de faltas
    const limiteFaltas = cargaHoraria * 0.25;
    const faltasRestantes = Math.floor(limiteFaltas - faltas);

    document.getElementById('cargaHoraria').textContent = cargaHoraria;
    document.getElementById('limiteFaltas').textContent = limiteFaltas.toFixed(0);
    document.getElementById('faltasAtuais').textContent = faltas;
    
    if (faltasRestantes > 0) {
        document.getElementById('podeFaltar').innerHTML = 
            `<span class="text-success">Ainda pode faltar ${faltasRestantes} aulas</span>`;
    } else if (faltasRestantes === 0) {
        document.getElementById('podeFaltar').innerHTML = 
            `<span class="text-danger">ATENÇÃO: Você atingiu o limite de faltas!</span>`;
    } else {
        document.getElementById('podeFaltar').innerHTML = 
            `<span class="text-danger">ATENÇÃO: Limite de faltas ultrapassado!</span>`;
    }
}

// Função auxiliar para calcular a média final usando as três fórmulas
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
    return 100; // Se não encontrar, retorna 100
} 