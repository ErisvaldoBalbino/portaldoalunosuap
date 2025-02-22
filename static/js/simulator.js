// Constantes
const MEDIA_APROVACAO = 60;
const MEDIA_FINAL = 40;
const NOTA_MAXIMA = 100;
const NOTA_MINIMA = 0;
const CARGA_HORARIA_MAXIMA = 1000;

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Atualiza campos quando o tipo de curso muda
    document.querySelectorAll('input[name="courseType"]').forEach(radio => {
        radio.addEventListener('change', toggleCourseFields);
    });

    // Atualiza limite de faltas quando a carga horária muda
    const cargaHorariaInput = document.getElementById('cargaHoraria');
    cargaHorariaInput.addEventListener('input', atualizarLimiteFaltas);
    
    // Verifica se já existe valor na carga horária ao carregar a página
    if (cargaHorariaInput.value) {
        atualizarLimiteFaltas();
    }

    // Adiciona validação para os inputs de notas
    ['nota1', 'nota2', 'nota3', 'nota4'].forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('input', function() {
                validarNota(this);
            });
        }
    });

    // Adiciona validação para os inputs de faltas e carga horária
    ['faltas', 'cargaHoraria'].forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('input', function() {
                validarNumeroPositivo(this);
            });
        }
    });
});

// Função para validar notas
function validarNota(input) {
    let valor = parseFloat(input.value);
    
    if (isNaN(valor)) {
        input.value = '';
        return;
    }
    
    if (valor > NOTA_MAXIMA) {
        input.value = NOTA_MAXIMA;
        mostrarAlerta(`A nota não pode ser maior que ${NOTA_MAXIMA}`);
    } else if (valor < NOTA_MINIMA) {
        input.value = NOTA_MINIMA;
        mostrarAlerta(`A nota não pode ser menor que ${NOTA_MINIMA}`);
    }
}

// Função para validar números positivos (faltas e carga horária)
function validarNumeroPositivo(input) {
    let valor = parseFloat(input.value);
    
    if (isNaN(valor)) {
        input.value = '';
        return;
    }
    
    if (valor < 0) {
        input.value = 0;
        mostrarAlerta('O valor não pode ser negativo');
        return;
    }

    // Validações específicas para carga horária
    if (input.id === 'cargaHoraria') {
        if (valor > CARGA_HORARIA_MAXIMA) {
            input.value = CARGA_HORARIA_MAXIMA;
            mostrarAlerta(`A aulas não podem ultrapassar ${CARGA_HORARIA_MAXIMA}`);
        }
    }
    // Validações específicas para faltas
    else if (input.id === 'faltas') {
        const cargaHoraria = parseFloat(document.getElementById('cargaHoraria').value) || 0;
        if (valor > cargaHoraria) {
            input.value = cargaHoraria;
            mostrarAlerta('O número de faltas não pode ser maior que a carga horária');
        }
    }
}

// Função para mostrar alertas de validação
function mostrarAlerta(mensagem) {
    // Verifica se já existe um alerta
    let alertaExistente = document.querySelector('.alert-validacao');
    if (alertaExistente) {
        alertaExistente.remove();
    }

    // Cria o novo alerta
    const alerta = document.createElement('div');
    alerta.className = 'alert alert-warning alert-validacao';
    alerta.style.position = 'fixed';
    alerta.style.top = '20px';
    alerta.style.right = '20px';
    alerta.style.zIndex = '1050';
    alerta.style.maxWidth = '300px';
    alerta.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${mensagem}
        </div>
    `;

    // Adiciona o alerta ao documento
    document.body.appendChild(alerta);

    // Remove o alerta após 3 segundos
    setTimeout(() => {
        alerta.remove();
    }, 3000);
}

// Toggle campos específicos do curso técnico
function toggleCourseFields() {
    const isTechnical = document.getElementById('technical').checked;
    const technicalFields = document.querySelectorAll('.technical-only');
    
    technicalFields.forEach(field => {
        field.style.display = isTechnical ? 'block' : 'none';
    });

    // Limpa os campos quando muda o tipo
    if (!isTechnical) {
        document.getElementById('nota3').value = '';
        document.getElementById('nota4').value = '';
    }
}

// Atualiza o limite de faltas (25% da carga horária)
function atualizarLimiteFaltas() {
    const cargaHoraria = parseFloat(document.getElementById('cargaHoraria').value) || 0;
    const limiteFaltas = Math.floor(cargaHoraria * 0.25);
    document.getElementById('limiteFaltas').value = limiteFaltas;
}

// Calcula a média para curso superior
function calcularMediaSuperior(nota1, nota2) {
    if (isNaN(nota1) || isNaN(nota2)) return 0;
    return (2 * nota1 + 3 * nota2) / 5;
}

// Calcula a média para curso técnico
function calcularMediaTecnico(nota1, nota2, nota3, nota4) {
    if (isNaN(nota1) || isNaN(nota2) || isNaN(nota3) || isNaN(nota4)) return 0;
    return (2 * nota1 + 2 * nota2 + 3 * nota3 + 3 * nota4) / 10;
}

// Calcula as possibilidades de nota final para curso técnico
function calcularPossibilidadesTecnico(nota1, nota2, nota3, nota4) {
    const possibilidades = [];
    
    // Possibilidade 1: md + naf / 2
    const mediaAtual = calcularMediaTecnico(nota1, nota2, nota3, nota4);
    const naf1 = (MEDIA_APROVACAO * 2) - mediaAtual;
    if (naf1 <= 100) {
        possibilidades.push(Math.ceil(naf1));
    }

    // Possibilidade 2: (2*naf + 2*n2 + 3*n3 + 3*n4) / 10
    const naf2 = ((MEDIA_APROVACAO * 10) - (2 * nota2 + 3 * nota3 + 3 * nota4)) / 2;
    if (naf2 <= 100) {
        possibilidades.push(Math.ceil(naf2));
    }

    // Possibilidade 3: (2*n1 + 2*naf + 3*n3 + 3*n4) / 10
    const naf3 = ((MEDIA_APROVACAO * 10) - (2 * nota1 + 3 * nota3 + 3 * nota4)) / 2;
    if (naf3 <= 100) {
        possibilidades.push(Math.ceil(naf3));
    }

    // Possibilidade 4: (2*n1 + 2*n2 + 3*naf + 3*n4) / 10
    const naf4 = ((MEDIA_APROVACAO * 10) - (2 * nota1 + 2 * nota2 + 3 * nota4)) / 3;
    if (naf4 <= 100) {
        possibilidades.push(Math.ceil(naf4));
    }

    // Possibilidade 5: (2*n1 + 2*n2 + 3*n3 + 3*naf) / 10
    const naf5 = ((MEDIA_APROVACAO * 10) - (2 * nota1 + 2 * nota2 + 3 * nota3)) / 3;
    if (naf5 <= 100) {
        possibilidades.push(Math.ceil(naf5));
    }

    // Retorna a menor nota necessária
    return Math.min(...possibilidades);
}

// Calcula a nota necessária na final para curso superior
function calcularNotaFinalSuperior(media) {
    return (MEDIA_APROVACAO * 2) - media;
}

// Função principal de cálculo
function calcularSimulacao() {
    // Pega os valores dos inputs
    const isTechnical = document.getElementById('technical').checked;
    const nota1Input = document.getElementById('nota1');
    const nota2Input = document.getElementById('nota2');
    const nota3Input = document.getElementById('nota3');
    const nota4Input = document.getElementById('nota4');
    const cargaHorariaInput = document.getElementById('cargaHoraria');
    const faltasInput = document.getElementById('faltas');

    // Converte os valores para número, usando 0 como padrão se estiver vazio
    const nota1 = parseFloat(nota1Input.value) || 0;
    const nota2 = parseFloat(nota2Input.value) || 0;
    const nota3 = parseFloat(nota3Input.value) || 0;
    const nota4 = parseFloat(nota4Input.value) || 0;
    const cargaHoraria = parseFloat(cargaHorariaInput.value) || 0;
    const faltas = parseFloat(faltasInput.value) || 0;

    // Calcula a média
    const media = isTechnical ? 
        calcularMediaTecnico(nota1, nota2, nota3, nota4) : 
        calcularMediaSuperior(nota1, nota2);

    // Atualiza a média parcial
    document.getElementById('mediaParcial').textContent = media.toFixed(1);

    // Determina a situação
    let situacao = '';
    if (media >= MEDIA_APROVACAO) {
        situacao = '<span class="status-aprovado">Aprovado</span>';
    } else if (media < MEDIA_FINAL) {
        // Verifica se alguma nota foi preenchida antes de mostrar "Reprovado"
        if (!nota1Input.value.trim() && !nota2Input.value.trim()) {
            situacao = '<span class="text-muted">Insira as notas para ver a situação</span>';
        } else {
            situacao = '<span class="status-reprovado">Reprovado por Nota</span>';
        }
    } else {
        situacao = '<span class="status-final">Prova Final</span>';
    }

    // Atualiza a situação
    document.getElementById('situacaoAtual').innerHTML = situacao;

    // Calcula e mostra as possibilidades de final
    const necessidadeFinal = document.getElementById('necessidadeFinal');
    const possibilidadesFinais = document.getElementById('possibilidadesFinais');
    possibilidadesFinais.innerHTML = '';

    if (media >= MEDIA_FINAL && media < MEDIA_APROVACAO) {
        necessidadeFinal.style.display = 'block';
        
        if (isTechnical) {
            const notaNecessaria = calcularPossibilidadesTecnico(nota1, nota2, nota3, nota4);
            possibilidadesFinais.innerHTML = `
                <div class="possibilidade-item">
                    <strong>Nota necessária na final:</strong> ${notaNecessaria}
                </div>
            `;
        } else {
            const notaNecessaria = calcularNotaFinalSuperior(media);
            possibilidadesFinais.innerHTML = `
                <div class="possibilidade-item">
                    <strong>Nota necessária na final:</strong> ${notaNecessaria.toFixed(1)}
                </div>
            `;
        }
    } else {
        necessidadeFinal.style.display = 'none';
    }

    // Calcula situação das faltas
    const limiteFaltas = Math.floor(cargaHoraria * 0.25);
    const podeFaltar = limiteFaltas - faltas;
    const frequencia = ((cargaHoraria - faltas) / cargaHoraria) * 100;

    document.getElementById('podeFaltar').textContent = 
        podeFaltar >= 0 ? `${podeFaltar} aulas` : '0 aulas (Limite excedido)';
    document.getElementById('frequenciaAtual').textContent = `${frequencia.toFixed(1)}%`;

    // Mostra os resultados
    document.getElementById('resultados').style.display = 'block';
} 