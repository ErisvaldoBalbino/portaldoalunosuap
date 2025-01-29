import requests
from django.conf import settings
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode
import logging

logger = logging.getLogger('portal_estudante')

class SUAPAPI:
    AUTHORIZATION_URL = settings.SUAP['AUTH_URL']
    ACCESS_TOKEN_URL = settings.SUAP['TOKEN_URL']
    API_URL = settings.SUAP['API_URL']
    USER_DATA_URL = f"{API_URL}rh/eu/"
    EXTRA_USER_DATA_URL = f"{API_URL}v2/minhas-informacoes/meus-dados/"
    PERIODS_URL_2 = f"{API_URL}v2/minhas-informacoes/meus-periodos-letivos/"
    PERIODS_URL_1 = f"{API_URL}edu/periodos/"
    DEFAULT_SCOPE = ['identificacao', 'email', 'documentos_pessoais']

    def __init__(self):
        self.client_id = settings.SUAP['CLIENT_ID']
        self.client_secret = settings.SUAP['CLIENT_SECRET']
        self.access_token = None

    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """Pega a URL de autorização para o fluxo OAuth2"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.DEFAULT_SCOPE)
        }
        if state:
            params['state'] = state
        
        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"

    def get_token_from_code(self, code: str, redirect_uri: str) -> Optional[str]:
        """Troca o código de autorização por um token de acesso"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.post(self.ACCESS_TOKEN_URL, data=data)
            response.raise_for_status()
            self.access_token = response.json().get('access_token')
            return self.access_token
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar token: {e}")
            return None

    def get_user_data(self, access_token: str = None) -> Optional[Dict[str, Any]]:
        """Pega os dados do usuário autenticado da API SUAP"""
        token = access_token or self.access_token
        if not token:
            return None
        
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            # Busca dados básicos do usuário
            response = requests.get(self.USER_DATA_URL, headers=headers)
            response.raise_for_status()
            user_data = response.json()
            
            # Busca dados extras do usuário
            extra_response = requests.get(self.EXTRA_USER_DATA_URL, headers=headers)
            extra_response.raise_for_status()
            extra_data = extra_response.json()

            if 'vinculo' in extra_data and 'curso' in extra_data['vinculo']:
                user_data['curso'] = extra_data['vinculo']['curso']
            
            return user_data
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados do usuário: {e}")
            return None

    def get_user_grades(self, ano_letivo: str = None, periodo_letivo: str = None) -> Optional[Dict[str, Any]]:
        """Busca notas do usuário autenticado"""
        if not self.access_token:
            return None
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        if ano_letivo and periodo_letivo:
            url = f"{self.API_URL}v2/minhas-informacoes/boletim/{ano_letivo}/{periodo_letivo}/"
        else:
            # Tenta buscar notas do período atual
            periods = self.get_academic_periods()
            if periods and len(periods) > 0:
                # Usa o período mais recente
                current_period = periods[0]
                ano = current_period.get('ano_letivo', current_period.get('ano'))
                periodo = current_period.get('periodo_letivo', current_period.get('periodo'))
                url = f"{self.API_URL}v2/minhas-informacoes/boletim/{ano}/{periodo}/"
            else:
                #logger.error("Não foi possível encontrar períodos acadêmicos")
                return None
        
        try:
            #logger.debug(f"Buscando notas do URL: {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            #logger.error(f"Erro ao buscar notas: {e}")
            #if hasattr(e.response, 'text'):
                #logger.error(f"Conteúdo da resposta: {e.response.text}")
            return None

    def get_academic_periods(self) -> Optional[List[Dict[str, Any]]]:
        """Pega a lista de períodos acadêmicos tentando ambos os endpoints disponíveis"""
        if not self.access_token:
            return None
        
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.get(self.PERIODS_URL_2, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data:  # Se obtiver dados válidos, retorna-os
                return data
        except requests.exceptions.RequestException:
            pass
        
        try:
            response = requests.get(self.PERIODS_URL_1, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None

    def get_student_data(self, registration: str) -> Optional[Dict[str, Any]]:
        """Pega os dados do estudante"""
        if not self.access_token:
            return None
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.API_URL}edu/alunos/{registration}/"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            #logger.error(f"Erro ao buscar dados do estudante: {e}")
            return None

    def get_student_grades(self, registration: str) -> Optional[Dict[str, Any]]:
        """Pega as notas do estudante"""
        if not self.access_token:
            return None
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.API_URL}edu/alunos/{registration}/boletim/"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            #logger.error(f"Erro ao buscar notas do estudante: {e}")
            return None

    def get_diaries(self, semestre: str) -> Optional[List[Dict[str, Any]]]:
        """Busca os diários e disciplinas do semestre"""
        if not self.access_token:
            return None
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.API_URL}v2/minhas-informacoes/meus-diarios/{semestre}/"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None 