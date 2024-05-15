import json


file_path = r"C:\Users\lucas.ferreira\Downloads\GLTF\S_BD2_CH2_L01_01_B.gltf"
json_file_path = r"D:/temp/teste.json"


def get_gltf_file(file_path):
    with open(file_path, 'r') as gltf_file:
        dict = json.loads(gltf_file.read())
        return dict


def get_texture_dict():
    dict = get_gltf_file(file_path)
    image_dict = {}
    for index, image in enumerate(dict['textures']):
        image_dict.update({str(index): image['name']})
    return image_dict


def set_material_textures(node_type_list):
    dict = get_gltf_file(file_path)
    texture_dict = get_texture_dict()
    to_delete_list = ['accessors', 'buffers', 'bufferViews', 'nodes', 'samplers', 'scenes']

    for object_to_delete in to_delete_list:
        dict.pop(object_to_delete)
    for node_type in node_type_list:
        for material in dict['materials']:
            node_list = []
            
            if node_type == 'pbrMetallicRoughness':
                if node_type in material:
                    for node in list(material[node_type].keys()):
                        node_list.append(node)
                for node_name in node_list:
                    if 'index' in str(material[node_type][node_name]):
                        material[node_type][node_name]['index'] = texture_dict[str(material[node_type][node_name]['index'])] + '.png'
            
            elif node_type == 'normalTexture' or 'occlusionTexture' or 'emissiveTexture':
                if node_type in material:
                    if 'index' in str(material[node_type]):
                        material[node_type]['index'] = texture_dict[str(material[node_type]['index'])] + '.png'
    return dict


def get_node_type_list():
    dict = get_gltf_file(file_path)
    node_list = []
    for node in dict['materials']:
        for node_name in list(node.keys()):
            node_list.append(node_name)
    remove_duplicate = list(set(node_list))
    return remove_duplicate


def dumps_json_dict():
    node_list = get_node_type_list()
    file_convert = json.dumps(set_material_textures(node_list))
    return file_convert


def write_json_file():
    with open(json_file_path, 'w') as file:
        node_list = get_node_type_list()
        data = json.dumps(set_material_textures(node_list))
        return data
