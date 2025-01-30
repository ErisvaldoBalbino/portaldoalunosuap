from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_http_methods
import secrets
import logging
from api import SUAPAPI
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import datetime

logger = logging.getLogger('student_portal')

def login(request):
    """Inicia o fluxo de login OAuth2"""
    # Se o usuário clica no botão de login na página de login
    if request.GET.get('auth') == 'suap':
        suap_api = SUAPAPI()
        state = secrets.token_urlsafe(32)
        request.session['oauth_state'] = state
        
        redirect_uri = request.build_absolute_uri(reverse('portal_estudante:oauth_callback'))
        #logger.debug(f"Redirect URI: {redirect_uri}")
        auth_url = suap_api.get_authorization_url(redirect_uri, state)
        #logger.debug(f"Full Auth URL: {auth_url}")
        
        return redirect(auth_url)
    
    # Exibe a página de login
    return render(request, 'portal_estudante/login.html')

@require_http_methods(["POST"])
def logout(request):
    """Limpa a sessão e redireciona para a página de login"""
    request.session.flush()
    return redirect('portal_estudante:login')

def oauth_callback(request):
    """Gerencia a callback do OAuth2 do SUAP"""
    error = request.GET.get('error')
    if error:
        return JsonResponse({'error': error}, status=400)
    
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    if not state or state != request.session.get('oauth_state'):
        return JsonResponse({'error': 'Parâmetro de estado inválido'}, status=400)
    
    suap_api = SUAPAPI()
    redirect_uri = request.build_absolute_uri(reverse('portal_estudante:oauth_callback'))
    
    access_token = suap_api.get_token_from_code(code, redirect_uri)
    if not access_token:
        return JsonResponse({'error': 'Não foi possível obter o token de acesso'}, status=400)
    
    user_data = suap_api.get_user_data(access_token)
    if not user_data:
        return JsonResponse({'error': 'Não foi possível obter os dados do usuário'}, status=400)
    
    request.session['access_token'] = access_token
    request.session['user_data'] = user_data
    
    return redirect('portal_estudante:dashboard')

def dashboard(request):
    """Renderiza o dashboard com os dados do usuário"""
    if not request.session.get('access_token'):
        return redirect('portal_estudante:login')
    
    suap_api = SUAPAPI()
    suap_api.access_token = request.session.get('access_token')
    
    try:
        user_data = request.session.get('user_data', {})
        periods = suap_api.get_academic_periods()
        
        # Se não houver período selecionado, usa o mais recente
        selected_year = request.GET.get('ano')
        selected_period = request.GET.get('periodo')
        
        if not selected_year or not selected_period:
            if periods:
                latest_period = periods[0]  # O primeiro é o mais recente
                selected_year = latest_period.get('ano_letivo') or latest_period.get('ano')
                selected_period = latest_period.get('periodo_letivo') or latest_period.get('periodo')
                # Redireciona para a URL com os parâmetros corretos
                return redirect(f"{reverse('portal_estudante:dashboard')}?ano={selected_year}&periodo={selected_period}")
        
        grades = suap_api.get_user_grades(selected_year, selected_period) if selected_year and selected_period else []
        semester = f"{selected_year}/{selected_period}"
        disciplines = suap_api.get_diaries(semester) if selected_year and selected_period else []
        
        # Cálculo dos totais
        totals = calculate_totals(grades) if grades else {
            'total_classes': 0,
            'total_absences': 0,
            'total_frequency': 0,
            'total_classes_given': 0
        }
        
        # Cálculo do resumo
        summary = calculate_summary(grades) if grades else {
            'total_subjects': 0,
            'approved_subjects': 0,
            'at_risk_subjects': 0
        }
        
        context = {
            'user_data': user_data,
            'periods': periods,
            'grades': grades,
            'disciplines': disciplines,
            'totals': totals,
            'summary': summary
        }
        
        return render(request, 'portal_estudante/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao acessar dados do SUAP: {str(e)}")
        request.session.flush()
        return redirect('portal_estudante:login')

def get_student_info(request, registration):
    """Busca informações do estudante pela SUAP API"""
    if 'access_token' not in request.session:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    suap_api = SUAPAPI()
    suap_api.access_token = request.session['access_token']
    
    # Busca dados do estudante
    student_data = suap_api.get_student_data(registration)
    if not student_data:
        return JsonResponse({'error': 'Não foi possível buscar dados do estudante'}, status=400)
    
    # Busca notas do estudante
    grades_data = suap_api.get_student_grades(registration)
    if not grades_data:
        return JsonResponse({'error': 'Não foi possível buscar notas do estudante'}, status=400)
    
    # Processa notas e frequência
    processed_data = {
        'student': student_data,
        'grades': grades_data,
        'summary': {
            'total_subjects': len(grades_data) if isinstance(grades_data, list) else 0,
            'approved_subjects': 0,
            'at_risk_subjects': 0
        }
    }
    
    # Calcula estatísticas
    if isinstance(grades_data, list):
        for subject in grades_data:
            if subject.get('situacao') == 'Aprovado':
                processed_data['summary']['approved_subjects'] += 1
            else:
                processed_data['summary']['at_risk_subjects'] += 1
    
    return JsonResponse(processed_data)

def report(request):
    """Gera relatório detalhado de notas e faltas do período selecionado"""
    if 'access_token' not in request.session:
        return redirect('portal_estudante:login')
    
    suap_api = SUAPAPI()
    suap_api.access_token = request.session['access_token']
    
    # Busca dados do usuário e notas
    user_data = request.session.get('user_data', {})
    selected_year = request.GET.get('ano')
    selected_period = request.GET.get('periodo')
    
    if not selected_year or not selected_period:
        return redirect('portal_estudante:dashboard')
    
    grades_data = suap_api.get_user_grades(selected_year, selected_period)
    
    # Processa os dados para o relatório
    report_data = []
    if isinstance(grades_data, list):
        for subject in grades_data:
            nota1 = float(subject.get('nota_etapa_1', {}).get('nota', 0) or 0)
            nota2 = float(subject.get('nota_etapa_2', {}).get('nota', 0) or 0)
            media = float(subject.get('media_disciplina', 0) or 0)
            final = float(subject.get('nota_avaliacao_final', {}).get('nota', 0) or 0)
            media_final = float(subject.get('media_final_disciplina', 0) or 0)
            faltas = int(subject.get('numero_faltas', 0))
            carga_horaria = int(subject.get('carga_horaria', 0))
            
            # Calcula informações adicionais
            max_faltas = carga_horaria * 0.25  # 25% da carga horária
            faltas_restantes = max_faltas - faltas if faltas < max_faltas else 0
            
            report_data.append({
                'disciplina': subject.get('disciplina', ''),
                'nota1': nota1,
                'nota2': nota2,
                'media': media,
                'final': final,
                'media_final': media_final,
                'situacao': subject.get('situacao', 'Cursando'),
                'faltas': faltas,
                'max_faltas': max_faltas,
                'faltas_restantes': faltas_restantes,
                'carga_horaria': carga_horaria
            })
    
    context = {
        'user_data': user_data,
        'selected_year': selected_year,
        'selected_period': selected_period,
        'report_data': report_data
    }
    
    return render(request, 'portal_estudante/report.html', context)

def calculate_totals(grades):
    """Calcula os totais de aulas e frequência"""
    totals = {
        'total_classes': 0,
        'total_classes_given': 0,
        'total_absences': 0,
        'total_frequency': 0
    }
    
    for subject in grades:
        ch = int(subject.get('carga_horaria', 0))
        ch_cumprida = int(subject.get('carga_horaria_cumprida', 0))
        faltas = int(subject.get('numero_faltas', 0))
        
        totals['total_classes'] += ch
        totals['total_classes_given'] += ch_cumprida
        totals['total_absences'] += faltas
    
    if totals['total_classes_given'] > 0:
        totals['total_frequency'] = round(
            ((totals['total_classes_given'] - totals['total_absences']) / totals['total_classes_given']) * 100,
            2
        )
    
    return totals

def calculate_summary(grades):
    """Calcula o resumo de disciplinas"""
    summary = {
        'total_subjects': len(grades),
        'approved_subjects': 0,
        'at_risk_subjects': 0
    }
    
    for subject in grades:
        if subject.get('situacao') == 'Aprovado':
            summary['approved_subjects'] += 1
        else:
            summary['at_risk_subjects'] += 1
    
    return summary

def export_pdf(request):
    """Exporta o relatório em formato PDF"""
    if 'access_token' not in request.session:
        return redirect('portal_estudante:login')
    
    # Obtém os dados do relatório
    suap_api = SUAPAPI()
    suap_api.access_token = request.session['access_token']
    user_data = request.session.get('user_data', {})
    selected_year = request.GET.get('ano')
    selected_period = request.GET.get('periodo')
    
    if not selected_year or not selected_period:
        return redirect('portal_estudante:dashboard')
    
    grades_data = suap_api.get_user_grades(selected_year, selected_period)
    
    # Cria o buffer para o PDF
    buffer = BytesIO()
    # Reduz as margens laterais para alinhar com o texto
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=25,
        leftMargin=25,
        topMargin=30,
        bottomMargin=30
    )
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=20
    )
    
    # Estilo para o texto da disciplina
    disciplina_style = ParagraphStyle(
        'DisciplinaStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=0
    )
    
    # Título
    title = Paragraph(f"Relatório Acadêmico - {selected_year}.{selected_period}", title_style)
    elements.append(title)
    
    # Informações do aluno com fonte menor
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5
    )
    elements.append(Paragraph(f"Aluno: {user_data.get('nome_registro')}", info_style))
    elements.append(Paragraph(f"Matrícula: {user_data.get('identificacao')}", info_style))
    elements.append(Paragraph(f"Curso: {user_data.get('curso')}", info_style))
    elements.append(Spacer(1, 15))
    
    # Dados das disciplinas
    data = [['Disciplina', 'N1', 'N2', 'Média', 'Final', 'M.Final', 'Faltas', 'Situação']]
    
    for subject in grades_data:
        # Cria um Paragraph para o nome da disciplina para permitir quebra de linha
        disciplina = Paragraph(subject.get('disciplina', ''), disciplina_style)
        data.append([
            disciplina,
            subject.get('nota_etapa_1', {}).get('nota', '--'),
            subject.get('nota_etapa_2', {}).get('nota', '--'),
            subject.get('media_disciplina', '--'),
            subject.get('nota_avaliacao_final', {}).get('nota', '--'),
            subject.get('media_final_disciplina', '--'),
            subject.get('numero_faltas', '0'),
            subject.get('situacao', 'Cursando')
        ])
    
    # Aumenta as larguras proporcionalmente para usar todo o espaço disponível
    col_widths = [220, 38, 38, 48, 38, 48, 43, 65]  # Larguras ajustadas
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWHEIGHT', (0, 0), (-1, 0), 20),
        ('ROWHEIGHT', (0, 1), (-1, -1), 30),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(table)
    
    # Adiciona data de geração com fonte menor
    elements.append(Spacer(1, 15))
    date_generated = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    elements.append(Paragraph(f"Gerado em: {date_generated}", info_style))
    
    # Gera o PDF
    doc.build(elements)
    
    # Prepara a resposta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{selected_year}_{selected_period}.pdf"'
    
    return response

def export_csv(request):
    """Exporta o relatório em formato CSV"""
    if 'access_token' not in request.session:
        return redirect('portal_estudante:login')
    
    # Obtém os dados do relatório
    suap_api = SUAPAPI()
    suap_api.access_token = request.session['access_token']
    selected_year = request.GET.get('ano')
    selected_period = request.GET.get('periodo')
    
    if not selected_year or not selected_period:
        return redirect('portal_estudante:dashboard')
    
    grades_data = suap_api.get_user_grades(selected_year, selected_period)
    
    # Prepara a resposta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{selected_year}_{selected_period}.csv"'
    
    # Cria o escritor CSV
    writer = csv.writer(response)
    
    # Escreve o cabeçalho
    writer.writerow([
        'Disciplina',
        'Nota 1',
        'Nota 2',
        'Média',
        'Final',
        'Média Final',
        'Faltas',
        'Carga Horária',
        'Frequência (%)',
        'Situação'
    ])
    
    # Escreve os dados
    for subject in grades_data:
        # Obtém a frequência e arredonda para 2 casas decimais
        frequencia = float(subject.get('percentual_carga_horaria_frequentada', 0))
        frequencia_formatada = round(frequencia, 2)
        
        writer.writerow([
            subject.get('disciplina', ''),
            subject.get('nota_etapa_1', {}).get('nota', ''),
            subject.get('nota_etapa_2', {}).get('nota', ''),
            subject.get('media_disciplina', ''),
            subject.get('nota_avaliacao_final', {}).get('nota', ''),
            subject.get('media_final_disciplina', ''),
            subject.get('numero_faltas', '0'),
            subject.get('carga_horaria', '0'),
            frequencia_formatada,
            subject.get('situacao', 'Cursando')
        ])
    
    return response

def simulator(request):
    """
    View para a página do simulador de notas.
    """
    if not request.session.get('access_token'):
        return redirect('portal_estudante:login')
        
    context = {
        'user_data': request.session.get('user_data', {})
    }
    return render(request, 'portal_estudante/simulator.html', context)
