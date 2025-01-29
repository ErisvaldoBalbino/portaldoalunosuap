from django import template

register = template.Library()

@register.filter
def filter_by_name(diaries, discipline_name):
    """Filtra a lista de diários pelo nome da disciplina"""
    if not diaries:
        return None
    
    for diary in diaries:
        if diary.get('disciplina', {}).get('nome') == discipline_name:
            return diary.get('disciplina')
    return None 