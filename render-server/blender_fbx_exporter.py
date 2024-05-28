import sys
import bpy


def save_fbx_file(gltf_path):
    export_path_list = gltf_path.split('\\')[:len(gltf_path.split('\\')) - 1]
    fbx_file_name = gltf_path.split('\\')[len(gltf_path.split('\\')) - 1]
    file_path = '/'.join(export_path_list) + '/' + fbx_file_name.split('.')[0] + '.fbx'

    print(file_path)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=file_path, embed_textures=True)


def export_fbx():
    gltf_path = sys.argv[5]

    # Limpa a cena inicial
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Importa o arquivo GLTF
    bpy.ops.import_scene.gltf(filepath=gltf_path)
    save_fbx_file(gltf_path)
    bpy.ops.wm.quit_blender()


export_fbx()
