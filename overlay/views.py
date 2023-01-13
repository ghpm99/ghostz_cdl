import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from ghostz_cdl.decorators import add_cors_react_dev
from overlay.models import Overlay, Team, Character

# Create your views here.
@add_cors_react_dev
@require_GET
def get_overlay(request):

    overlay_objects = Overlay.objects.all()

    data = [{
        'date': overlay.date,
        'hour': overlay.hour,
        'modality': overlay.modality,
        'active': overlay.active,
        'team' : [{
            'name': team.name,
            'twitch': team.twitch,
            'mmr': team.mmr,
            'mmr_as': team.mmr_as,
            'characteres': [{
                'family': character.family,
                'name': character.name,
                'bdo_class': character.bdo_class,
                'combat_style': character.combat_style,
                'matches': character.matches,
                'defeats': character.defeats,
                'victories': character.victories,
                'champion': character.champion,
                'dr': character.dr,
                'by': character.by,
                'walkover': character.walkover
            } for character in team.character_set.all()]
        } for team in overlay.team_set.all()]
    } for overlay in overlay_objects]

    return JsonResponse({'data': data})


@csrf_exempt
@add_cors_react_dev
@require_POST
def import_json(request):
    data = json.loads(request.body)
    for overlay_data in data:
        overlay = Overlay(
            date = overlay_data['Data'],
            hour = overlay_data['Horario'],
            modality = overlay_data['Modalidade']
        )
        overlay.save()

        for i in range(2):
            team_index = i + 1 #logica errada
            team = Team(
                overlay= overlay,
                name= overlay_data['Time{}'.format(team_index)],
                twitch = overlay_data['Twitch{}'.format(team_index)],
                mmr= overlay_data['MMR{}'.format(team_index)] if overlay_data.get('MMR{}'.format(team_index)) else '',
                mmr_as= overlay_data['MMR{}_AS'.format(team_index)] if overlay_data.get('MMR{}_AS'.format(team_index)) else ''
            )
            team.save()
            for c in range(3):

                character_index = c + i + 1 #logica errada

                character = Character(
                    team = team,
                    family = overlay_data['Fam{}'.format(character_index)],
                    name = overlay_data['Char{}'.format(character_index)],
                    bdo_class = overlay_data['Classe{}'.format(character_index)],
                    combat_style = overlay_data['Arma{}'.format(character_index)],
                    matches = overlay_data['PA{}'.format(character_index)],
                    defeats = overlay_data['DE{}'.format(character_index)],
                    victories = overlay_data['VI{}'.format(character_index)],
                    champion = overlay_data['CA{}'.format(character_index)],
                    dr = overlay_data['DR{}'.format(character_index)],
                    by = overlay_data['BY{}'.format(character_index)],
                    walkover = overlay_data['WO{}'.format(character_index)]
                )
                character.save()

    return JsonResponse({'status': 'JSON importado com sucesso!'})
