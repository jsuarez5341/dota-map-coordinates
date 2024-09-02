import json
import matplotlib.path as mplPath
import numpy as np

save_data = {
    'towers': [],
    'creeps': [],
    'neutrals': [],
    'waypoints': [],
}

def transform(x, y):
    return x/130 + 130/2, 130/2 - y/130

with open('data/mapdata.json', 'r') as f:
    neutrals = []
    data = json.loads(f.read())['data']
    for subdict in data['trigger_multiple']:
        name = subdict['name']
        if 'good' in name:
            team = 0
        elif 'evil' in name:
            team = 1
        else:
            raise ValueError('Unknown team name', name)

        top_left_x = subdict['1']['x']
        top_left_y = subdict['1']['y']
        bottom_right_x = subdict['4']['x']
        bottom_right_y = subdict['4']['y']
        top_left_x, top_left_y = transform(top_left_x, top_left_y)  
        bottom_right_x, bottom_right_y = transform(bottom_right_x, bottom_right_y)

        x = top_left_x + (bottom_right_x - top_left_x)/2
        y = top_left_y + (bottom_right_y - top_left_y)/2

        save_data['neutrals'].append({
            'team': team,
            'x': x,
            'y': y,
        })
        
    for subdict in data['npc_dota_tower']:
        name = subdict['name']
        if 'goodguys' in name:
            team = 0
        elif 'badguys' in name:
            team = 1
        else:
            raise ValueError('Unknown team name', name)

        if '1' in name:
            tier = 1
        elif '2' in name:
            tier = 2
        elif '3' in name:
            tier = 3
        elif '4' in name:
            tier = 4
        else:
            raise ValueError('Unknown tier name', name)

        x, y = transform(subdict['x'], subdict['y'])
        health = subdict['health']
        damage = (subdict['damageMax'] + subdict['damageMin']) / 2
        save_data['towers'].append({
            'team': team,
            'tier': tier,
            'x': x,
            'y': y,
            'health': health,
            'damage': damage,
        })

    for subdict in data['npc_dota_fort']:
        name = subdict['name']
        if 'goodguys' in name:
            team = 0
        elif 'badguys' in name:
            team = 1
        else:
            raise ValueError('Unknown team name', name)

        x, y = transform(subdict['x'], subdict['y'])
        health = subdict['health']
        save_data['towers'].append({
            'team': team,
            'tier': 5,
            'x': x,
            'y': y,
            'health': health,
            'damage': 0,
        })

waypoints = {}
with open('data/path_corner.json', 'r') as f:
    data = json.loads(f.read())['features']
    for npc_path in data:
        path_key = npc_path['id']
        path_coords = []
        for x, y in npc_path['geometry']['coordinates']:
            x, y = transform(x, y)
            path_coords.append({'x': x, 'y': y})

        waypoints[path_key] = {'waypoints': path_coords}

with open('data/spawnerdata.json', 'r') as f:
    data = json.loads(f.read())['features']
    for npc_path in data:
        spawner_key = npc_path['properties']['name']
        spawner_x, spawner_y = npc_path['geometry']['coordinates']
        x, y = transform(spawner_x, spawner_y)
        waypoints[spawner_key]['spawn_x'] = x
        waypoints[spawner_key]['spawn_y'] = y

# Order waypoints by lane
save_data['waypoints'] = [
    waypoints['npc_dota_spawner_good_top'],
    waypoints['npc_dota_spawner_good_mid'],
    waypoints['npc_dota_spawner_good_bot'],
    waypoints['npc_dota_spawner_bad_top'],
    waypoints['npc_dota_spawner_bad_mid'],
    waypoints['npc_dota_spawner_bad_bot'],
]

save_path = 'processed.yaml'
import yaml
with open(save_path, 'w') as f:
    yaml.dump(save_data, f)

exit()

neutral_data = {}
with open('data/dota_pvp_prefab.vmap.txt', 'r') as f:
    dump_on_next_brace = False
    for line in f.readlines():
        if 'VolumeName' in line:
            VolumeName = line.strip('\n').split(" ")[-1].replace('"', '')
        if 'PullType' in line:
            PullType = line.strip('\n').split(" ")[-1].replace('"', '')
        if 'NeutralType' in line:
            NeutralType = line.strip('\n').split(" ")[-1].replace('"', '')
        if 'npc_dota_neutral_spawner' in line:
            dump_on_next_brace = True
        if '}' in line and dump_on_next_brace:
            dump_on_next_brace = False
##            print VolumeName, PullType, NeutralType
            neutral_data[VolumeName] = {
                'PullType': PullType,
                'NeutralType': NeutralType
            }

print(neutral_data)

for pt in data['npc_dota_neutral_spawner']:
    point = [pt['x'], pt['y']]
    for trigger in data['trigger_multiple']:
        points = []
        for i in range(1, 5):
            points.append([trigger[str(i)]['x'], trigger[str(i)]['y']])
        bbPath = mplPath.Path(np.array(points))
        if bbPath.contains_point(point):
            pt['name'] = trigger['name']
            pt['PullType'] = neutral_data[trigger['name']]['PullType']
            pt['NeutralType'] = neutral_data[trigger['name']]['NeutralType']
            break
