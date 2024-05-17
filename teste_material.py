import os
from pymxs import runtime as rt
import json


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
                        material[node_type][node_name]['index'] = texture_dict[str(
                            material[node_type][node_name]['index'])] + '.png'

            elif node_type == 'normalTexture' or 'occlusionTexture' or 'emissiveTexture':
                if node_type in material:
                    if 'index' in str(material[node_type]):
                        material[node_type]['index'] = texture_dict[str(material[node_type]['index'])] + '.png'
    return dict


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
    for file in get_gltf_file_list():
        with open(file, 'r') as gltf_file:
            gltf_to_dict = json.loads(gltf_file.read())
            gltf_file = set_material_textures(get_node_type_list(gltf_to_dict), gltf_to_dict)
            main_scene_name = main_json['scenes'][0]['name']

            if gltf_file['scenes'][0]['name'] != main_scene_name:
                print(gltf_file['meshes'])


def dumps_json_dict():
    node_list = get_node_type_list(get_gltf_file())
    file_convert = json.dumps(set_material_textures(node_list, get_gltf_file()))
    return file_convert


def write_json_file():
    with open(json_file_path, 'w') as file:
        node_list = get_node_type_list(get_gltf_file())
        return json.dump(set_material_textures(node_list, get_gltf_file()), file)


def config_initial_scene():
    rt.resetMaxFile(rt.name('noPrompt'))
    rt.renderers.current = rt.Corona()

    # Limpa o listener para a nova cena
    rt.clearListener()

    # Change Apect Ratio
    rt.rendLockImageAspectRatio = True
    rt.renderWidth = 1280
    rt.rendImageAspectRatio = 1


def create_environment():
    hdri_sky = rt.CoronaSky(cloudsEnable=True, intensityMultiplier=0.1)
    IMXR_sun = rt.CoronaSun(name="IMXRSun", on=True, targeted=True, sizeMultiplier=2, intensity=0.2, shadowsFromClouds=True, textured=True)
    IMXR_sun.position = rt.Point3(500, 500, 500)
    sun_target = rt.getNodeByName('IMXRSun.target')
    sun_target.pos = rt.Point3(0, 0, 0)


def import_fbx():
    rt.importFile(fbxFilePath, rt.name('noPrompt'))


def delete_dummy_nodes():
    to_delete = []
    for node in rt.objects:
        # Cria uma lista com os nodes a serem excluídos
        if rt.classOf(node) == rt.Dummy:
            to_delete.append(node)
    # Itera na lista e exclui os nodes selecionados
    for delete_node in to_delete:
        rt.delete(delete_node)


def create_cc_node(text_map, channel_file):
    channel_dict = {
        "R": 0,
        "G": 1,
        "B": 2,
        "A": 3
    }

    cc_node = rt.ColorCorrection()
    channel_to_use = channel_dict[channel_file.upper()]

    # Aplicar textura no Color Correction
    cc_node.Map = text_map

    # Mudar o canal para o desejado
    cc_node.rewireR = channel_to_use
    cc_node.rewireG = channel_to_use
    cc_node.rewireB = channel_to_use

    return cc_node


def create_cameras():
    for obj in rt.objects:
        if rt.classOf(obj) == rt.Dummy and 'Camera' in obj.name and 'SceneComponent' in obj.name:

            camera = rt.CoronaCam()
            camera.name = obj.name
            camera.pos = obj.pos
            camera.target.pos = rt.Point3(0, 0, obj.pos.z)
            camera.focalLength = 30
            camera.enableClipping = True
            camera.clippingNear = 20


def copy_uv_channel(obj, channel_from, channel_to):
    rt.convertToPoly(obj)

    ## Retorna um inteiro com o número de faces e vértices do canal desejado
    num_map_verts_from = rt.polyop.getNumMapVerts(obj, channel_from)
    num_map_faces_from = rt.polyop.getNumMapFaces(obj, channel_from)
    num_map_faces_to = rt.polyop.getNumMapFaces(obj, channel_to)
    num_map_verts_to = rt.polyop.getNumMapVerts(obj, channel_to)

    ## Define o número de faces e vértices do novo canal a ser usado
    rt.polyop.setNumMapVerts(obj, channel_to, num_map_verts_from, keep=False)
    rt.polyop.setNumMapFaces(obj, channel_to, num_map_faces_from, keep=False)

    for vert in range(1, num_map_verts_to + 1):
        rt.polyop.setMapVert(obj, channel_to, vert, rt.polyop.getMapVert(obj, channel_from, vert))

    for face in range(1, num_map_faces_to + 1):
        rt.polyop.setMapFace(obj, channel_to, face, rt.polyop.getMapFace(obj, channel_from, face))

    print(f"UV mudada para ID 1 para o objeto {obj.name}")


def create_material():
    for mtl in json_file['materials']:
        material_node = rt.CoronaPhysicalMtl()
        material_node.name = mtl['name']
        is_vertex_color = False

        if 'pbrMetallicRoughness' in mtl:
            # Diffuse settings
            if 'baseColorTexture' in mtl['pbrMetallicRoughness']:
                diffuse_texture_path = folder_path + '/' + mtl['pbrMetallicRoughness']['baseColorTexture']['index']
                diffuse_color_texture = rt.Bitmaptexture(fileName=diffuse_texture_path)
                material_node.baseTexmap = diffuse_color_texture

                # UV ID Setting
                if 'texCoord' in mtl['pbrMetallicRoughness']['baseColorTexture']:
                    if mtl['pbrMetallicRoughness']['baseColorTexture']['texCoord'] == 1:
                        is_vertex_color = True

            elif 'baseColorFactor' in mtl['pbrMetallicRoughness']:
                diffuse_color_factor = mtl['pbrMetallicRoughness']['baseColorFactor']
                material_node.colorDiffuse = rt.Color(diffuse_color_factor[0], diffuse_color_factor[1], diffuse_color_factor[2])

            # Metallic Settings
            if 'metallicRoughnessTexture' in mtl['pbrMetallicRoughness']:
                metallic_roughness_texture_path = folder_path + '/' + mtl['pbrMetallicRoughness']['metallicRoughnessTexture']['index']
                metallic_roughness_texture = rt.Bitmaptexture(fileName=metallic_roughness_texture_path)

                # Roughness Map
                material_node.baseRoughnessTexmap = create_cc_node(metallic_roughness_texture, 'G')

                # Metalness Map
                material_node.metalnessTexmap = create_cc_node(metallic_roughness_texture, 'R')

                # UV ID Setting
                if 'texCoord' in mtl['pbrMetallicRoughness']['metallicRoughnessTexture']:
                    if mtl['pbrMetallicRoughness']['metallicRoughnessTexture']['texCoord'] == 1:
                        is_vertex_color = True

            if 'metallicFactor' in mtl['pbrMetallicRoughness']:
                material_node.metalnessMode = mtl['pbrMetallicRoughness']['metallicFactor']

            # Roughness Settings
            if 'roughnessFactor' in mtl['pbrMetallicRoughness']:
                material_node.baseRoughnessMapAmount = mtl['pbrMetallicRoughness']['roughnessFactor']
                material_node.baseRoughness = mtl['pbrMetallicRoughness']['roughnessFactor']

        # Normal Settings
        if 'normalTexture' in mtl:
            normal_map_texture_path = folder_path + '/' + mtl['normalTexture']['index']
            normal_map_texture = rt.Bitmaptexture(fileName=normal_map_texture_path)
            normal_node = rt.CoronaNormal(normalMap=normal_map_texture)
            normal_node.multiplier = 1
            material_node.baseBumpTexmap = normal_node

            # UV ID Setting
            if 'texCoord' in mtl['normalTexture']:
                if mtl['normalTexture']['texCoord'] == 1:
                    is_vertex_color = True

        # Emissive Settings
        if 'emissiveTexture' in mtl:
            emissive_texture_path = folder_path + '/' + mtl['emissiveTexture']['index']
            emissive_texture = rt.Bitmaptexture(fileName=emissive_texture_path)
            material_node.selfIllumTexmap = emissive_texture

        if 'emissiveFactor' in mtl:
            material_node.selfIllumLevel = mtl['emissiveFactor'][0]

        # Double Sided Mtl
        if 'doubleSided' in mtl:
            is_double_sided = mtl['doubleSided']

        for obj in rt.objects:
            if obj.material:
                if 'Glass' in obj.material.name:
                    material_to_apply = rt.CoronaPhysicalMtl(preset=14)
                    obj.material = material_to_apply
                elif obj.material.name == mtl['name']:
                    obj.material = material_node
                    if is_vertex_color:
                        copy_uv_channel(obj, 2, 1)
                        break


        print(mtl['name'])
        print(mtl)
        print('---------------------')


if __name__ == '__main__':
    #config_initial_scene()
    #import_fbx()
    #json_file = json.loads(dumps_json_dict())
    #create_cameras()
    ##create_environment()
    #delete_dummy_nodes()
    #create_material()
    compare_json()
