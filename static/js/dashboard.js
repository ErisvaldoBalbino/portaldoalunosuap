// Função para mostrar o loading ao trocar de período
function showTableLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function changePeriod(value) {
    if (!value) return;
    
    showTableLoading();
    const [ano, periodo] = value.split('.');
    if (ano && periodo) {
        // Fazer requisição AJAX em vez de recarregar a página
        fetch(`${window.location.pathname}?ano=${ano}&periodo=${periodo}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Recalcular o resumo acadêmico com base nos mesmos critérios da tabela
            if (data.grades && Array.isArray(data.grades)) {
                const summary = {
                    total_subjects: data.grades.length,
                    approved_subjects: 0,
                    at_risk_subjects: 0
                };

                data.grades.forEach(subject => {
                    const nota1 = subject.nota_etapa_1?.nota;
                    const nota2 = subject.nota_etapa_2?.nota;
                    const media = parseFloat(subject.media_disciplina || 0);

                    if (subject.situacao === "Aprovado" || 
                        (nota1 !== undefined && nota2 !== undefined && media >= 60)) {
                        summary.approved_subjects++;
                    } else {
                        summary.at_risk_subjects++;
                    }
                });

                // Atualizar o resumo na interface
                document.querySelector('.col-4:nth-child(1) h3').textContent = summary.total_subjects;
                document.querySelector('.col-4:nth-child(2) h3').textContent = summary.approved_subjects;
                document.querySelector('.col-4:nth-child(3) h3').textContent = summary.at_risk_subjects;
            }

            // Atualizar tabela de notas
            const tbody = document.querySelector('.table tbody');
            tbody.innerHTML = '';

            if (data.grades && Array.isArray(data.grades)) {
                data.grades.forEach(subject => {
                    const row = document.createElement('tr');
                    row.className = 'align-middle';

                    // Extrair valores com fallbacks seguros
                    const nota1 = subject.nota_etapa_1?.nota || '--';
                    const nota2 = subject.nota_etapa_2?.nota || '--';
                    const media = subject.media_disciplina || '--';
                    const final = subject.nota_avaliacao_final?.nota || '--';
                    const mediaFinal = subject.media_final_disciplina || '--';
                    const frequencia = (subject.percentual_carga_horaria_frequentada || 0).toFixed(1);

                    row.innerHTML = `
                        <td class="border-0">${subject.disciplina || ''}</td>
                        <td class="border-0 text-center">${subject.carga_horaria || '0'}</td>
                        <td class="border-0 text-center">${subject.carga_horaria_cumprida || '0'}</td>
                        <td class="border-0 text-center">${subject.numero_faltas || '0'}</td>
                        <td class="border-0 text-center">${frequencia}%</td>
                        <td class="border-0 text-center">${nota1}</td>
                        <td class="border-0 text-center">${nota2}</td>
                        <td class="border-0 text-center">${media}</td>
                        <td class="border-0 text-center">${final}</td>
                        <td class="border-0 text-center">${mediaFinal}</td>
                        <td class="border-0 text-center">
                            ${(subject.situacao === "Aprovado" || 
                               (nota1 !== '--' && nota2 !== '--' && parseFloat(media) >= 60))
                                ? '<span class="status-approved">Aprovado</span>'
                                : '<span class="status-ongoing">Cursando</span>'}
                        </td>
                        <td class="border-0 text-center">
                            <button class="btn btn-sm btn-info" onclick="calcularNecessario('${subject.disciplina}', ${nota1 === '--' ? 0 : nota1}, ${nota2 === '--' ? 0 : nota2}, ${subject.carga_horaria || 0}, ${subject.numero_faltas || 0})">
                                Calcular
                            </button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            }

            // Adicionar linha de totais
            if (data.totals) {
                const totalsRow = document.createElement('tr');
                totalsRow.className = 'table fw-bold';
                totalsRow.innerHTML = `
                    <td class="border-0 text-start">Total:</td>
                    <td class="border-0 text-center">${data.totals.total_classes || 0}</td>
                    <td class="border-0 text-center">${data.totals.total_classes_given || 0}</td>
                    <td class="border-0 text-center">${data.totals.total_absences || 0}</td>
                    <td class="border-0 text-center">${data.totals.total_frequency || 0}%</td>
                    <td class="border-0 text-center" colspan="7">--</td>
                `;
                tbody.appendChild(totalsRow);
            }

            // Atualizar URL sem recarregar
            const url = new URL(window.location);
            url.searchParams.set('ano', ano);
            url.searchParams.set('periodo', periodo);
            window.history.pushState({}, '', url);

            document.getElementById('loadingOverlay').style.display = 'none';
        })
        .catch(error => {
            console.error('Erro ao carregar dados:', error);
            document.getElementById('loadingOverlay').style.display = 'none';
            alert('Erro ao carregar os dados. Por favor, tente novamente.');
        });
    }
}

// Carregar dados iniciais quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    const periodoSelect = document.getElementById('periodoSelect');
    if (periodoSelect && periodoSelect.value) {
        changePeriod(periodoSelect.value);
    }
});

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
        necessidade = '<p class="status-approved">Você já está aprovado! 🎉</p>';
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
            `<span class="status-approved">Ainda pode faltar ${faltasRestantes} aulas</span>`;
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