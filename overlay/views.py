import json

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ghostz_cdl.decorators import (add_cors_react_dev, validate_pusher_user,
                                   validate_user)
from lib import pusher
from overlay.models import Background, BDOClass, Character, Overlay, Team, User


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
            } for character in team.character_set.all().order_by('id')]
        } for team in overlay.team_set.all().order_by('id')]
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

    return JsonResponse({'data': mount_overlay_active(overlay_object.id)})


def mount_overlay_active(id):

    query_active_overlay = """
        select
            oo.id as id,
            oo.modality as modality ,
            oo.league as league ,
            ob2.image as background_image
        from
            overlay_overlay oo
        left join overlay_background ob2
            on
            ob2.modality = oo.modality
        where
            1 = 1
            and oo.id = %(id)s
    """

    with connection.cursor() as cursor:
        cursor.execute(query_active_overlay, {
            'id': id
        })
        overlay = cursor.fetchone()

    filters_teams = {
        'overlay_id': overlay[0]
    }

    query_overlay_teams = """
        select
            ot.id as id,
            ot."name" as team_name,
            ot.twitch as team_twitch,
            ot.mmr as team_mmr,
            ot.mmr_as as team_mmr_as
        from
            overlay_team ot
        where
            1 = 1
            and ot.overlay_id = %(overlay_id)s
        ORDER BY ot.id ASC
    """

    with connection.cursor() as cursor:
        cursor.execute(query_overlay_teams, filters_teams)
        teams = cursor.fetchall()

    team_list = []

    query_overlay_players = """
        select
            oc.id as id,
            oc."family" as player_family,
            oc."name" as player_name,
            oc.bdo_class as player_class,
            oc.combat_style as player_style,
            oc.matches as player_matches,
            oc.defeats as player_defeats,
            oc.victories as player_victories,
            oc.champion as player_champion,
            oc.dr as player_dr,
            oc.by as player_by,
            oc.walkover as player_walkover,
            coalesce (ou2.video,
            ou.video,
            ob.video_awakening) as video_awakening,
            coalesce (ou2.video,
            ou.video,
            ob.video_sucession) as video_sucession
        from
            overlay_character oc
        inner join overlay_bdoclass ob
        on
            ob.json_name = oc.bdo_class
        left join overlay_user ou
        on
            ou."family" = oc."family"
            and ou.video <> ''
        left join overlay_uservideo ou2
        on
            ou2.user_id = ou.id
            and ou2.bdo_class_id = ob.id
        where
            1 = 1
            and oc.team_id = %(team_id)s
        ORDER BY oc.id ASC
    """
    for team in teams:

        filters_player = {
            'team_id': team[0]
        }

        with connection.cursor() as cursor:
            cursor.execute(query_overlay_players, filters_player)
            players = cursor.fetchall()

        players_list = []

        for player in players:
            player_data = {
                'id': player[0],
                'family': player[1],
                'name': player[2],
                'bdo_class': player[3],
                'combat_style': player[4],
                'matches': player[5],
                'defeats': player[6],
                'victories': player[7],
                'champion': player[8],
                'dr': player[9],
                'by': player[10],
                'walkover': player[11],
                'media': {
                    'images': [],
                    'video_awakening': settings.BASE_URL + settings.MEDIA_URL + player[12],
                    'video_sucession': settings.BASE_URL + settings.MEDIA_URL + player[13]
                }
            }

            modality = overlay[1]
            if modality == 'DUPLAS' or modality == 'TRIOS':
                class_videos_list = []
                filters_class_videos = {
                    'player_class': player[3],
                    'awakening': True if player[4] == 'Despertar' else False
                }

                query_class_videos = """
                    select
                        image
                    from
                        overlay_imagebdoclass oi
                    inner join overlay_bdoclass ob
                    on
                        ob.json_name = %(player_class)s
                    where
                        1 = 1
                        and oi.bdo_class_id = ob.id
                        and oi.awakening = %(awakening)s
                """
                with connection.cursor() as cursor:
                    cursor.execute(query_class_videos, filters_class_videos)
                    class_videos = cursor.fetchall()
                for class_video in class_videos:
                    class_videos_list.append({
                        'url': settings.BASE_URL + settings.MEDIA_URL + class_video[0]
                    })
                player_data['media']['images'] = class_videos_list

            players_list.append(player_data)

        team_list.append({
            'id': team[0],
            'name': team[1],
            'twitch': team[2],
            'mmr': team[3],
            'mmr_as': team[4],
            'characteres': players_list
        })

    overlay_data = {
        'id': overlay[0],
        'modality': overlay[1],
        'league': overlay[2],
        'background': settings.BASE_URL + settings.MEDIA_URL + overlay[3] if overlay[3] else '',
        'team': team_list
    }

    return overlay_data


@csrf_exempt
@add_cors_react_dev
@validate_user
@require_POST
def update_overlay_active(request, id, user):

    pusher.send_active_overlay(mount_overlay_active(id))

    overlay = Overlay.objects.filter(id=id).first()
    if overlay is None:
        return JsonResponse({'status': 'Overlay não encontrado'}, status=404)
    overlay.active = True

    overlay.save()

    overlay_active = Overlay.objects.filter(active=True).exclude(id=id).all()
    if overlay_active.__len__() > 0:
        for overlay in overlay_active:
            overlay.active = False
            overlay.save()

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
            league=overlay_data['LIGA'] if overlay_data.get('LIGA') else 'LIVERTO'
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

                if overlay_data['Fam{}'.format(character_index)] == '':
                    continue

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
            } for character in team.character_set.all().order_by('id')]
        } for team in overlay.team_set.all().order_by('id')]
    }

    pusher.send_active_overlay(data)

    return JsonResponse({'status': 'Overlay atualizado com sucesso!'})


@add_cors_react_dev
@require_GET
@validate_user
def get_class_view(request, user):
    bdo_class = BDOClass.objects.all().order_by('name')

    data = [{
        'id': data.id,
        'name': data.json_name
    } for data in bdo_class]

    return JsonResponse({'data': data})


@csrf_exempt
@add_cors_react_dev
@validate_user
@require_POST
def update_team(request, user):
    req = json.loads(request.body) if request.body else {}

    if req is None:
        return JsonResponse({'status': 'Nao existe dados para ser atualizados!'}, status=400)

    if req.get('id') is None:
        return JsonResponse({'status': 'Id do time nao informado!'}, status=400)

    team = Team.objects.filter(id=req.get('id')).first()

    if req.get('name'):
        team.name = req.get('name')
    if req.get('twitch'):
        team.twitch = req.get('twitch')

    team.save()

    for character_data in req.get('characteres'):
        character = Character.objects.filter(id=character_data.get('id')).first()
        character.family = character_data.get('family')
        character.name = character_data.get('name')
        character.bdo_class = character_data.get('bdo_class')
        character.combat_style = character_data.get('combat_style')
        character.save()

    return JsonResponse({'status': 'Time atualizado com sucesso!'})
