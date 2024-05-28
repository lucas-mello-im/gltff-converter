import os, subprocess, zipfile
import time

root_folder = r"\\IMDNas\IMDNAS\IMDNAS\IMDArchive\GLTF_CONVERTER"


def export_fbx_file_blender(main_dir):
    blender_path = r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe"
    blender_export_script = os.path.abspath('blender_fbx_exporter.py')
    gltf_path = get_file(main_dir)
    if gltf_path:
        print('Opening Blender to convert: ' + gltf_path)
        subprocess.run([blender_path, '-b', '-P', blender_export_script, '--', gltf_path])
    else:
        print('Nothing to process')
        time.sleep(10)


def create_root_folder(folder_to_create):
    if folder_to_create == 'ToDo':
        os.mkdir(root_folder + '/ToDo')
    elif folder_to_create == 'Doing':
        os.mkdir(root_folder + '/Doing')
    elif folder_to_create == 'Done':
        os.mkdir(root_folder + '/Done')


def validate_root_folder():
    folder_dict = {
        "ToDo": os.path.isdir(root_folder + '/ToDo'),
        "Doing": os.path.isdir(root_folder + '/Doing'),
        "Done": os.path.isdir(root_folder + '/Done')
    }

    for folder in folder_dict:
        if folder_dict[folder]:
            print(f'{folder} folder already exists.')
        else:
            print(f'Creating {folder} folder.')
            create_root_folder(folder)


def get_file(main_dir):
    main_dir_to_do_list = os.listdir(main_dir + '/ToDo')
    if len(main_dir_to_do_list) >= 1:
        file_name = main_dir_to_do_list[0].split('.')[0]
        zip_path = main_dir + '/ToDo/' + main_dir_to_do_list[0]
        unpack_path = main_dir + '/Doing/' + main_dir_to_do_list[0].split('.')[0]
        gltf_path = main_dir + '/Doing/' + main_dir_to_do_list[0].split('.')[0] + '/' + main_dir_to_do_list[0].split('.')[0] + '.gltf'

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            print(f'Extraindo arquivos de: {zip_path}')
            zip_ref.extractall(unpack_path)

        if os.path.isfile(gltf_path):
            print('Starting process for: ' + gltf_path)
            return gltf_path
        else:
            print('Without GLTF file in folder: ' + unpack_path)
            return None
    else:
        print('Nenhuma tarefa aguardando.')


def call_3d_max(main_dir):
    max_path = r"C:\Program Files\Autodesk\3ds Max 2025\3dsmaxbatch.exe"
    ms_path = os.path.abspath('run_converter.ms')
    background_image = os.path.abspath('../resource/imxr.png')
    subprocess.run([max_path, ms_path, '-mxsValue', f'file_path:{main_dir}', '-v', '4'])


#while True:
main_dir = r"C:\Users\lucas.ferreira\Downloads\Lucas"
call_3d_max(main_dir)
#    if len(os.listdir(main_dir)) >= 1:
        #validate_root_folder()
#       export_fbx_file_blender(main_dir)
#

