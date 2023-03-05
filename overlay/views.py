import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from ghostz_cdl.decorators import add_cors_react_dev, validate_user, validate_pusher_user
from overlay.models import Overlay, Team, Character, User, BDOClass, Background
from django.conf import settings
from lib import pusher


# Create your views here.
@add_cors_react_dev
@require_GET
@validate_user
def get_overlay(request, user):

    overlay_objects = Overlay.objects.all().order_by('id')

    data = [{
        'id': overlay.id,
        'date': overlay.date,
        'hour': overlay.hour,
        'modality': overlay.modality,
        'active': overlay.active,
        'team': [{
            'id': team.id,
            'name': team.name,
            'twitch': team.twitch,
            'mmr': team.mmr,
            'mmr_as': team.mmr_as,
            'characteres': [{
                'id': character.id,
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


@add_cors_react_dev
@require_GET
@validate_pusher_user
def get_active_overlay(request, user):
    overlay_object = Overlay.objects.filter(active=True).first()
    if overlay_object is None:
        overlay_object = Overlay.objects.first()

    if overlay_object is None:
        return JsonResponse({'msg': 'Overlay not found.'}, status=404)

    background = Background.objects.filter(modality__icontains=overlay_object.modality).first()

    def BDOClassImages(bdo_class):
        bdo_class_object = BDOClass.objects.filter(json_name=bdo_class).first()
        if bdo_class_object is None:
            return {
                'video_awakening': '',
                'video_sucession': '',
                'images': []
            }
        data = {
            'video_awakening': settings.BASE_URL + bdo_class_object.video_awakening.url,
            'video_sucession': settings.BASE_URL + bdo_class_object.video_sucession.url,
            'images': [{
                'url': settings.BASE_URL + bdo_image.image.url,
                'awakening': bdo_image.awakening
            } for bdo_image in bdo_class_object.images.all()]
        }
        return data

    def userCustomVideo(family):
        user = User.objects.filter(family=family).first()
        if user is None or not user.video:
            return {
                'video': ''
            }
        return {
            'video': settings.BASE_URL + user.video.url
        }

    data = {
        'id': overlay_object.id,
        'date': overlay_object.date,
        'hour': overlay_object.hour,
        'modality': overlay_object.modality,
        'league': overlay_object.league,
        'background': settings.BASE_URL + background.image.url if background else '',
        'active': overlay_object.active,
        'team': [{
            'id': team.id,
            'name': team.name,
            'twitch': team.twitch,
            'mmr': team.mmr,
            'mmr_as': team.mmr_as,
            'characteres': [{
                'id': character.id,
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
                'walkover': character.walkover,
                'media': BDOClassImages(character.bdo_class),
                'custom': userCustomVideo(character.family)
            } for character in team.character_set.all()]
        } for team in overlay_object.team_set.all()]
    }

    return JsonResponse({'data': data})


@csrf_exempt
@add_cors_react_dev
@validate_user
@require_POST
def update_overlay_active(request, id, user):
    overlay_active = Overlay.objects.filter(active=True).all()
    if overlay_active.__len__() > 0:
        for overlay in overlay_active:
            overlay.active = False
            overlay.save()

    overlay = Overlay.objects.filter(id=id).first()

    if overlay is None:
        return JsonResponse({'status': 'Overlay não encontrado'}, status=404)
    overlay.active = True
    overlay.save()

    background = Background.objects.filter(modality__icontains=overlay.modality).first()

    def BDOClassImages(bdo_class):
        bdo_class_object = BDOClass.objects.filter(json_name=bdo_class).first()
        if bdo_class_object is None:
            return {
                'video_awakening': '',
                'video_sucession': '',
                'images': []
            }
        data = {
            'video_awakening': settings.BASE_URL + bdo_class_object.video_awakening.url,
            'video_sucession': settings.BASE_URL + bdo_class_object.video_sucession.url,
            'images': [{
                'url': settings.BASE_URL + bdo_image.image.url,
                'awakening': bdo_image.awakening
            } for bdo_image in bdo_class_object.images.all()]
        }
        return data

    def userCustomVideo(family):
        user = User.objects.filter(family=family).first()
        if user is None or not user.video:
            return {
                'video': ''
            }
        return {
            'video': settings.BASE_URL + user.video.url
        }

    data = {
        'id': overlay.id,
        'date': overlay.date,
        'hour': overlay.hour,
        'modality': overlay.modality,
        'league': overlay.league,
        'background': settings.BASE_URL + background.image.url if background else '',
        'active': overlay.active,
        'team': [{
            'id': team.id,
            'name': team.name,
            'twitch': team.twitch,
            'mmr': team.mmr,
            'mmr_as': team.mmr_as,
            'characteres': [{
                'id': character.id,
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
                'walkover': character.walkover,
                'media': BDOClassImages(character.bdo_class),
                'custom': userCustomVideo(character.family)
            } for character in team.character_set.all()]
        } for team in overlay.team_set.all()]
    }

    pusher.send_active_overlay(data)

    return JsonResponse({'status': 'Overlay atualizado com sucesso!'})


@csrf_exempt
@add_cors_react_dev
@validate_user
@require_POST
def import_json(request, user):
    req = json.loads(request.body) if request.body else {}

    if req.get('reset') is True:
        Overlay.objects.all().delete()

    if req.get('data') is None:
        return JsonResponse({'status': 'Nao existe dada para ser importado!'}, status=400)

    data = json.loads(req.get('data')) if req.get('data') else []

    for overlay_data in data:
        overlay = Overlay(
            date=overlay_data['Data'],
            hour=overlay_data['Horario'],
            modality=overlay_data['Modalidade'],
            league=overlay_data['LIGA']
        )
        overlay.save()

        for i in range(2):
            team_index = i + 1

            team = Team(
                overlay=overlay,
                name=overlay_data['Time{}'.format(team_index)],
                twitch=overlay_data['Twitch{}'.format(team_index)],
                mmr=overlay_data['MMR{}'.format(team_index)] if overlay_data.get(
                    'MMR{}'.format(team_index)) else '',
                mmr_as=overlay_data['MMR{}_AS'.format(team_index)] if overlay_data.get(
                    'MMR{}_AS'.format(team_index)) else ''
            )
            team.save()
            for c in range(3):

                character_index = (i * 3) + (c + 1)

                character = Character(
                    team=team,
                    family=overlay_data['Fam{}'.format(character_index)],
                    name=overlay_data['Char{}'.format(character_index)],
                    bdo_class=overlay_data['Classe{}'.format(character_index)],
                    combat_style=overlay_data['Arma{}'.format(
                        character_index)],
                    matches=overlay_data['PA{}'.format(character_index)],
                    defeats=overlay_data['DE{}'.format(character_index)],
                    victories=overlay_data['VI{}'.format(character_index)],
                    champion=overlay_data['CA{}'.format(character_index)],
                    dr=overlay_data['DR{}'.format(character_index)],
                    by=overlay_data['BY{}'.format(character_index)],
                    walkover=overlay_data['WO{}'.format(character_index)]
                )
                character.save()

                user = User.objects.filter(family=character.family).first()
                if user is None:
                    user = User(
                        family=character.family
                    )
                    user.save()

    return JsonResponse({'status': 'JSON importado com sucesso!'})


@csrf_exempt
@add_cors_react_dev
@validate_user
@require_POST
def reload_overlay(request, user):

    overlay = Overlay.objects.filter(active=True).first()

    if overlay is None:
        return JsonResponse({'status': 'Não existe overlay ativo!'}, status=400)

    background = Background.objects.filter(modality__icontains=overlay.modality).first()

    def BDOClassImages(bdo_class):
        bdo_class_object = BDOClass.objects.filter(json_name=bdo_class).first()
        if bdo_class_object is None:
            return {
                'video_awakening': '',
                'video_sucession': '',
                'images': []
            }
        data = {
            'video_awakening': settings.BASE_URL + bdo_class_object.video_awakening.url,
            'video_sucession': settings.BASE_URL + bdo_class_object.video_sucession.url,
            'images': [{
                'url': settings.BASE_URL + bdo_image.image.url,
                'awakening': bdo_image.awakening
            } for bdo_image in bdo_class_object.images.all()]
        }
        return data

    def userCustomVideo(family):
        user = User.objects.filter(family=family).first()
        if user is None or not user.video:
            return {
                'video': ''
            }
        return {
            'video': settings.BASE_URL + user.video.url
        }

    data = {
        'id': overlay.id,
        'date': overlay.date,
        'hour': overlay.hour,
        'modality': overlay.modality,
        'league': overlay.league,
        'background': settings.BASE_URL + background.image.url if background else '',
        'active': overlay.active,
        'team': [{
            'id': team.id,
            'name': team.name,
            'twitch': team.twitch,
            'mmr': team.mmr,
            'mmr_as': team.mmr_as,
            'characteres': [{
                'id': character.id,
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
                'walkover': character.walkover,
                'media': BDOClassImages(character.bdo_class),
                'custom': userCustomVideo(character.family)
            } for character in team.character_set.all()]
        } for team in overlay.team_set.all()]
    }

    pusher.send_active_overlay(data)

    return JsonResponse({'status': 'Evento disparado com sucesso!'})
