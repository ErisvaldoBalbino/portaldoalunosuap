from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_http_methods
import secrets
import logging
from api import SUAPAPI

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

def student_dashboard(request):
    """Exibe o dashboard do estudante"""
    if 'access_token' not in request.session:
        return redirect('portal_estudante:login')
    
    suap_api = SUAPAPI()
    suap_api.access_token = request.session['access_token']
    
    # Busca dados do usuário e notas
    user_data = request.session.get('user_data', {})
    periods_data = suap_api.get_academic_periods() or []  # Se retornar None, usa lista vazia
    
    # Pega o período selecionado ou o mais recente
    selected_year = request.GET.get('ano')
    selected_period = request.GET.get('periodo')
    
    # Se não tiver período selecionado e houver períodos disponíveis, usa o mais recente
    if (not selected_year or not selected_period) and periods_data:
        selected_year = str(periods_data[0].get('ano_letivo'))
        selected_period = str(periods_data[0].get('periodo_letivo'))
    
    # Busca notas apenas se tiver um período selecionado
    grades_data = []
    if selected_year and selected_period:
        grades_data = suap_api.get_user_grades(selected_year, selected_period) or []
    
    context = {
        'user_data': user_data,
        'grades': grades_data,
        'periods': periods_data,
        'summary': {
            'total_subjects': len(grades_data) if isinstance(grades_data, list) else 0,
            'approved_subjects': 0,
            'at_risk_subjects': 0
        }
    }
    
    # Calculate statistics if grades are available
    if isinstance(grades_data, list):
        for subject in grades_data:
            if subject.get('situacao') == 'Aprovado':
                context['summary']['approved_subjects'] += 1
            else:
                context['summary']['at_risk_subjects'] += 1
    
    return render(request, 'portal_estudante/dashboard.html', context)

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

def generate_report(request):
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
