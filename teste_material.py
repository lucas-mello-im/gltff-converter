import os
from pymxs import runtime as rt
import json, subprocess, time

opts = rt.maxOps.mxsCmdLineArgs
folder_path = r"\\IMDNas\IMDNAS\IMDNAS\IMDArchive\GLTF_CONVERTER\ToDo\S_BD2_CH2_L01_01_A"#opts['file_path']
json_file_path = r"D:/temp/teste.json"


def get_gltf_file():
    gltf_list = get_gltf_file_list()
    if len(gltf_list) >= 1:
        with open(gltf_list[0], 'r') as gltf_file:
            dict1 = json.loads(gltf_file.read())
        return dict1
    else:
        print('Não há arquivos na cena')


def get_gltf_file_list():
    gltf_list = []
    folder_list = os.listdir(folder_path)
    for file in folder_list:
        if len(file.split('.')) > 1:
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
    to_delete_list = ['accessors', 'buffers', 'bufferViews', 'samplers']
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
                    if node['name'] in main_scene_assets.keys() and node['primitives'][0]['material'] != main_scene_assets[node['name']]:
                        for asset_node in main_json['meshes']:
                            if node['name'] == asset_node['name']:
                                material_parent = asset_node['primitives'][0]['material']
                                asset_node['primitives'][0]['material'] = [material_parent]
                                asset_node['primitives'][0]['material'].append(node['primitives'][0]['material'])

            # Adiciona os novos materiais ao json principal
            for material in gltf_file['materials']:
                if material['name'] not in main_material_name_list:
                    main_json['materials'].append(material)

    return main_json


def change_node_names(main_json):
    for node in main_json['nodes']:
        if 'mesh' in node:
            main_json['meshes'][node['mesh']]['name'] = node['name']


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
    rt.renderWidth = 1000
    rt.rendImageAspectRatio = 1

    # Cria o render element para AO
    create_render_elements()


def create_render_elements():
    corona_ao = rt.CoronaAO()
    corona_ao.colorSpread = -0.5
    corona_ao.quality = 32
    corona_ao.maxDistance = [100,100,100]
    
    re = rt.maxOps.GetCurRenderElementMgr()
    re.addrenderelement(rt.CTexmap(elementname='IMXR_AO'))
    render_element = re.getRenderElement(0)
    render_element.texmap = corona_ao


def create_environment():
    hdri_sky = rt.CoronaSky(cloudsEnable=True, intensityMultiplier=1)
    rt.environmentMap = hdri_sky
    
    # Config BG Override
    cc_node = rt.CoronaColorCorrect(exposure=-3.177, gamma=0.81)
    cc_node.inputTexmap = hdri_sky
    rt.renderers.current.bg_texmapUseDirect = True
    rt.renderers.current.bg_texmapUseReflect = True
    rt.renderers.current.bg_texmapUseRefract = True
    rt.renderers.current.bg_overrideRefract = True
    rt.renderers.current.bg_overrideDirect = True
    rt.renderers.current.bg_overrideReflect = True
    rt.renderers.current.bg_texmapDirect = cc_node
    rt.renderers.current.bg_texmapReflect = cc_node
    rt.renderers.current.bg_texmapRefract = cc_node

    IMXR_sun = rt.CoronaSun(name="IMXRSun", on=True, sizeMultiplier=5, intensity=0.1, shadowsFromClouds=True, textured=True)
    IMXR_sun.targeted = True
    IMXR_sun.pos = rt.Point3(-410.894, 881.947, 745.899)
    IMXR_sun.target.pos = rt.Point3(-138.526, 142.186, 0)
  

def import_fbx(file_path):
    if os.path.isfile(file_path):
        rt.importFile(file_path, rt.name('noPrompt'))
    else:
        print("Nao deu")


def delete_dummy_nodes():
    to_delete = []
    for node in rt.objects:
        # Cria uma lista com os nodes a serem excluídos
        if rt.classOf(node) == rt.Dummy or rt.classOf(node) == rt.Freecamera:
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


def create_lights():
    for obj in rt.objects:
        if rt.classOf(obj) == rt.freeSpot:
            # Get old light parameters
            new_light_position = obj.position
            new_light_intensity = obj.multiplier
            new_light_color = obj.rgb

            # Create New Light
            new_light = rt.CoronaLight(on=True, shape=0, color=new_light_color, intensity=new_light_intensity * 100, width=0.5)
            new_light.position = new_light_position

            # Delete Old Light
            rt.delete(obj)

        elif rt.classOf(obj) == rt.Directionallight:
            rt.delete(obj)


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


def add_multi_mtl_mod(object_node):
    mtl_id_mod = rt.materialModifier(materialID=1, name='IMxr MtlID Modifier')
    rt.addModifier(object_node, mtl_id_mod)


def get_material_name_list(obj_node):
    material_name_list = []
    for node in json_file['meshes']:
        if node['name'] == obj_node.name:
            if isinstance(node['primitives'][0]['material'], str):
                material_name_list.append(node['primitives'][0]['material'])
            else:
                for material in node['primitives'][0]['material']:
                    material_name_list.append(material)
    print(material_name_list)
    return material_name_list


def create_material(obj_node):
    material_node = None
    material_name_list = get_material_name_list(obj_node)
    is_vertex_color = False
    material_id_list = []

    for mtl in json_file['materials']:

        if mtl['name'] in material_name_list:
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
                round_edges_node = rt.CoronaRoundEdges(mapAdditionalBump=normal_node, radius=0.02)
                material_node.baseBumpTexmap = round_edges_node

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

            if is_vertex_color:
                copy_uv_channel(obj_node, 2, 1)
            material_id_list.append(material_node)

    if material_id_list:
        if len(material_name_list) > 1:
            add_multi_mtl_mod(obj_node)
            obj_node.material = rt.multiSubMaterial(materialList=material_id_list)

            print('Material aplicado para: ' + material_node.name)
        else:
            obj_node.material = material_id_list[0]
            print('Material aplicado para: ' + material_node.name)


def apply_all_materials():
    for obj_node in rt.objects:
        if obj_node.material:
            if 'Glass' in obj_node.material.name:
                material_to_apply = rt.CoronaPhysicalMtl(preset=14)
                obj_node.material = material_to_apply
            else:
                create_material(obj_node)


def loop_camera_renderer():
    for cam in rt.objects:
        if rt.classOf(cam) == rt.CoronaCam:
            print(cam)


def render_structure():
    for obj in rt.objects:
        if 'SM_BD1_DFT' not in obj.name:
            if rt.classOf(obj) == rt.Editable_mesh or rt.classOf(obj) == rt.Editable_Poly:
                rt.hide(obj)
    for obj in rt.objects:
        rt.unhide(obj)


def get_file(main_dir):
    gltf_path = main_dir + '/' + main_dir.split('\\')[-1] + '.gltf'
    if os.path.isfile(gltf_path):
        print('Starting process for: ' + gltf_path)
        return gltf_path
    else:
        print('Without GLTF file in folder: ' + gltf_path)
        return None


def export_fbx_file_blender(main_dir):
    blender_path = r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe"
    # Caminho paliativo por conta do subprocess, fazer com os.path.abspath
    blender_export_script = r"\\IMDNas\IMDNAS\IMDNAS\IMDArchive\GLTF_CONVERTER\gltff-converter\render-server\blender_fbx_exporter.py" #os.path.abspath('/render-server/blender_fbx_exporter.py')
    gltf_path = get_file(main_dir)
    if gltf_path:
        print('Opening Blender to convert: ' + gltf_path)
        subprocess.run([blender_path, '-b', '-P', blender_export_script, '--', gltf_path])
    else:
        print('Nothing to process')


if __name__ == '__main__':
    rt.clearListener()
    json_file = set_material_textures(get_node_type_list(get_gltf_file()), get_gltf_file())    
    if len(get_gltf_file_list()) > 1:
        json_file = compare_json()
    change_node_names(json_file)
    export_fbx_file_blender(folder_path)
    config_initial_scene()
    import_fbx(rf"\\IMDNas\IMDNAS\IMDNAS\IMDArchive\GLTF_CONVERTER\ToDo/{json_file['scenes'][0]['name']}/{json_file['scenes'][0]['name']}.fbx")
    create_cameras()
    create_lights()
    create_environment()
    delete_dummy_nodes()
    apply_all_materials()
    rt.archiveMaxFile(rf"\\IMDNas\IMDNAS\IMDNAS\IMDArchive\GLTF_CONVERTER\Done/{json_file['scenes'][0]['name']}", quiet=True)
    #render_structure()
