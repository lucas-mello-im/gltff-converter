import json, os


fbxFilePath = r"C:\Users\lucas.ferreira\Downloads\GLTF\S_BD2_CH2_L01_01_B.fbx"
folder_path = r"C:\Users\lucas.ferreira\Downloads\Lucas"
json_file_path = r"D:/temp/teste.json"


def get_gltf_file():
    gltf_list = get_gltf_file_list()
    with open(gltf_list[0], 'r') as gltf_file:
        dict1 = json.loads(gltf_file.read())
    return dict1


def get_gltf_file_list():
    gltf_list = []
    folder_list = os.listdir(folder_path)
    for file in folder_list:
        if file.split('.')[1] == 'gltf':
            gltf_list.append(folder_path + '/' + file)
    return gltf_list


def get_texture_dict(dict):
    image_dict = {}
    for index, image in enumerate(dict['textures']):
        image_dict.update({str(index): image['name']})
    return image_dict


def set_material_textures(node_type_list, dict):
    texture_dict = get_texture_dict(dict)
    to_delete_list = ['accessors', 'buffers', 'bufferViews', 'nodes', 'samplers']
    texture_dict_ = create_material_dict(dict)
    for object_to_delete in to_delete_list:
        dict.pop(object_to_delete)

    # Muda o index pelo nome dos materiais
    for asset in dict['meshes']:
        for node in asset['primitives']:
            for material in texture_dict_['materials']:
                if material['materialIndex'] == node['material']:
                    node['material'] = material['name']

    # Muda o index pelo nome das texturas
    for node_type in node_type_list:
        for material in dict['materials']:
            node_list = []

            if node_type == 'pbrMetallicRoughness':
                if node_type in material:
                    for node in list(material[node_type].keys()):
                        node_list.append(node)
                for node_name in node_list:
                    if 'index' in str(material[node_type][node_name]):
                        material[node_type][node_name]['index'] = texture_dict[str(
                            material[node_type][node_name]['index'])] + '.png'

            elif node_type == 'normalTexture' or 'occlusionTexture' or 'emissiveTexture':
                if node_type in material:
                    if 'index' in str(material[node_type]):
                        material[node_type]['index'] = texture_dict[str(material[node_type]['index'])] + '.png'
    return dict


def create_material_dict(dict):
    material_dict = {'materials': []}
    for index, node in enumerate(dict['materials']):
        node['materialIndex'] = index
        material_dict['materials'].append(node)
    return material_dict


def get_node_type_list(dict):
    node_list = []
    if dict['materials']:
        for node in dict['materials']:
            for node_name in list(node.keys()):
                node_list.append(node_name)
        remove_duplicate = list(set(node_list))
        return remove_duplicate


def compare_json():
    main_json = set_material_textures(get_node_type_list(get_gltf_file()), get_gltf_file())
    main_scene_name = main_json['scenes'][0]['name']
    main_scene_assets = {}
    main_material_name_list = []

    teste_num_mat = str(len(main_json['materials']))

    for asset in main_json['meshes']:
        main_scene_assets[asset['name']] = asset['primitives'][0]['material']

    for material_name in main_json['materials']:
        main_material_name_list.append(material_name['name'])

    for file in get_gltf_file_list():
        with open(file, 'r') as gltf_file:
            gltf_to_dict = json.loads(gltf_file.read())
            gltf_file = set_material_textures(get_node_type_list(gltf_to_dict), gltf_to_dict)

            # Adiciona a variação de material ao Mesh
            if gltf_file['scenes'][0]['name'] != main_scene_name:
                for node in gltf_file['meshes']:
                    if node['name'] in main_scene_assets.keys():
                        if node['primitives'][0]['material'] != main_scene_assets[node['name']]:
                            for asset_node in main_json['meshes']:
                                if node['name'] == asset_node['name']:
                                    asset_node['primitives'][0]['materia2'] = node['primitives'][0]['material']

            # Adiciona os novos materiais ao json principal
            for material in gltf_file['materials']:
                if material['name'] not in main_material_name_list:
                    main_json['materials'].append(material)


            #print(f"Objeto: {node['name']}\nMaterial 1: {node['primitives'][0]['material']}\nMaterial 2: {main_scene_assets[node['name']]}\n-------------------------")
    #print(f'Numero de materiais antes: {teste_num_mat}\nNumero de materiais depois: {str(len(main_json['materials']))}')
    #print(main_json)


compare_json()
