import os, subprocess


def export_fbx_file_blender(main_dir):
    blender_path = r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe"
    blender_export_script = os.path.abspath('blender_fbx_exporter.py')
    gltf_path = get_path(main_dir)
    subprocess.run([blender_path, '-b', '-P', blender_export_script, '--', gltf_path])


def create_root_folder(folder_to_create):
    if folder_to_create == 'ToDo':
        os.mkdir(r'\\IMDNas\IMDNAS\IMDNAS\IMDArchive\GLTF_CONVERTER\ToDo')
    elif folder_to_create == 'Doing':
        os.mkdir(r'\\IMDNas\IMDNAS\IMDNAS\IMDArchive\GLTF_CONVERTER\Doing')
    elif folder_to_create == 'Done':
        os.mkdir(r'\\IMDNas\IMDNAS\IMDNAS\IMDArchive\GLTF_CONVERTER\Done')


def validate_root_folder():
    folder_dict = {
        "ToDo": os.path.isdir(r'\\IMDNas\IMDNAS\IMDNAS\IMDArchive\GLTF_CONVERTER\ToDo'),
        "Doing": os.path.isdir(r'\\IMDNas\IMDNAS\IMDNAS\IMDArchive\GLTF_CONVERTER\Doing'),
        "Done": os.path.isdir(r'\\IMDNas\IMDNAS\IMDNAS\IMDArchive\GLTF_CONVERTER\Done')
    }

    for folder in folder_dict:
        if folder_dict[folder]:
            print(f'{folder} folder already exists.')
        else:
            print(f'Creating {folder} folder.')
            create_root_folder(folder)


def get_path(main_dir):
    main_dir_to_do_list = os.listdir(main_dir)
    if len(main_dir_to_do_list) >= 1:
        gltf_path = main_dir + '/' + main_dir_to_do_list[0] + '/' + main_dir_to_do_list[0] + '.gltf'
        return gltf_path
    else:
        print('Nenhuma tarefa aguardando')


def call_3d_max():
    max_path = r"C:\Program Files\Autodesk\3ds Max 2025\3dsmax.exe"
    ms_path = os.path.abspath('teste.ms')
    background_image = os.path.abspath('../resource/imxr.png')
    subprocess.run([max_path, '-a', background_image, '-ms', ms_path])

validate_root_folder()
#while True:
#    main_dir = r"C:\Users\lucas.ferreira\Downloads\Lucas\teste"
#    if len(os.listdir(main_dir)) >= 1:
#        export_fbx_file_blender(main_dir)
#

