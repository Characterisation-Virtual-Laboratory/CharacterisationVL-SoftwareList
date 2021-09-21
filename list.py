#!/usr/bin/env python3

import sys
import argparse
import os
import configparser
import re
from lxml import etree
import collections

def is_valid_version_str(versionStr):
    if re.match(r"^(?:(\d+)\.)?(?:(\d+)\.)?(\*|\d+)$", versionStr):
        return True
    else:
        return False


def find_categories(tree, directories_path, is_merge_file):
    """
    takes a tree, return a dict
    {'category-1': {tags: ['tag1', 'tag2'], 'directories': ['']}}
    """
    root_element = tree.getroot()
    all_categories = root_element.findall('.//Category')
    return_cats = {}
    for category in all_categories:
        category_val = category.text
        return_cats[category_val] = {'tags': [], 'directories': []}
        # now go all the way back to find all tags
        _cat_parent = category.getparent()
        while _cat_parent is not None:
            # if menu level, look for its children with Name as tag
            if _cat_parent.tag == 'Menu':
                _name_items = _cat_parent.findall('Name')
                _directory_items = _cat_parent.findall('Directory')
                for _name_item in _name_items:
                    return_cats[category_val]['tags'].append(_name_item.text.strip())
                    if len(_directory_items) == 0 and not is_merge_file:
                        return_cats[category_val]['directories'].insert(0, _name_item.text.strip())
                for _directory_item in _directory_items:
                    # read the directory
                    _directory_file_path = os.path.join(directories_path, _directory_item.text)
                    if os.path.exists(_directory_file_path):
                        _dir_config = configparser.ConfigParser(interpolation=None)
                        _dir_config.read(_directory_file_path)
                        _dir_name = _dir_config.get("Desktop Entry", "Name").strip()
                        if _dir_name:
                            return_cats[category_val]['directories'].insert(0, _dir_name)
            _cat_parent = _cat_parent.getparent()
    return return_cats


def read_merge_file(merge_file, directories_path):
    """
    takes a file, return a dict
    {'category-1': {tags: ['tag1', 'tag2'], 'directories': ['']}}
    """
    tree = etree.parse(merge_file)
    return find_categories(tree, directories_path, True)

    
def do_list(args):
    xdg_applications_dirs=args.xdg_applications_dirs
    xdg_menu_dir=args.xdg_menu_dir
    xdg_cvl_files=args.xdg_menu_files
    xdg_desktop_dir=args.xdg_desktop_dir
    neurodesk_containers_dir=args.neurodesk_containers_dir
    cvl_site=args.cvl_site
    output_file=args.output_file
    for xdg_applications_dir in xdg_applications_dirs:
        if not os.path.exists(xdg_applications_dir):
            print (f"Application DIR {xdg_applications_dir} does not exist. Ignore")
    for xdg_cvl_file in xdg_cvl_files:
        if not os.path.exists(os.path.join(xdg_menu_dir, xdg_cvl_file)):
            print (f"File {xdg_cvl_file} does not exist in {xdg_menu_dir}")
    if not os.path.exists(xdg_desktop_dir):
        print (f"xdg_desltop_dir not exist")
        exit(1)	
    print (">>>>>>>>>>Valid inputs<<<<<<<<<<<<<")
    ################### read xml file #################
    categories = {}
    for xdg_cvl_file in xdg_cvl_files:
        tree = etree.parse(os.path.join(xdg_menu_dir, xdg_cvl_file))
        _afile_categories = find_categories(tree, xdg_desktop_dir, False)
        categories.update(_afile_categories)
        # deal with merge files now
        merge_files = tree.getroot().findall('.//MergeFile')
        for merge_file in merge_files:
            merge_file_path = merge_file.text
            if not "/" in merge_file_path:
                merge_file_path = os.path.join(xdg_menu_dir, merge_file_path)
            _a_mergefile_categories = read_merge_file(merge_file_path, xdg_desktop_dir)
            _additional_tags = []
            _additional_paths = []
            # walk to parent
            _merge_file_parent = merge_file.getparent()
            while _merge_file_parent is not None:
                if _merge_file_parent.tag == 'Menu':
                    _name_items = _merge_file_parent.findall('Name')
                    _directory_items = _merge_file_parent.findall('Directory')
                    for _name_item in _name_items:
                        _additional_tags.append(_name_item.text.strip())
                        if len(_directory_items) == 0:
                            _additional_paths.insert(0, _name_item.text.strip())
                for _directory_item in _directory_items:
                    # read the directory
                    _directory_file_path = os.path.join(xdg_desktop_dir, _directory_item.text)
                    _dir_config = configparser.ConfigParser(interpolation=None)
                    _dir_config.read(_directory_file_path)
                    _dir_name = _dir_config.get("Desktop Entry", "Name").strip()
                    if _dir_name:
                        _additional_paths.insert(0, _dir_name)
                _merge_file_parent = _merge_file_parent.getparent()
            ### go over _a_mergefile_categories
            for _cat in _a_mergefile_categories:
                _a_mergefile_categories[_cat]['tags'] = _a_mergefile_categories[_cat]['tags'] + _additional_tags
                _a_mergefile_categories[_cat]['directories'] = _additional_paths +  _a_mergefile_categories[_cat]['directories']
            categories.update(_a_mergefile_categories)
             
    ###################
    with open(output_file, 'w') as out:
        out.write('site, name, version, menu_path, tags, exec_type, module_name, singularityimagepath\n')
        # First look at all the applications in applications dir and its subdirs
        for xdg_applications_dir in xdg_applications_dirs:
            for root, dirs, files in os.walk(xdg_applications_dir, topdown = True, followlinks=True):
                for file in files:
                    if not file.endswith(".desktop"):
                        continue
                    _output_line = ''
                    app_config_file = os.path.join(root, file)
                    print (f"\n>>>>>Looking into {app_config_file}")
                    _config = configparser.ConfigParser(interpolation=None)
                    _config.read(app_config_file)
                    _app_name = _config.get("Desktop Entry", "Name").strip()
                    _app_version = ""
                    _name_parts = _app_name.split(" ")
                    if len(_name_parts) > 1 and is_valid_version_str(_name_parts[-1].strip()):
                        _app_name = " ".join(_name_parts[:-1])
                        _app_version = _name_parts[-1]
                    # this app does not belong to any categories
                    if not _config.has_option("Desktop Entry", "Categories"):
                        print ("\tNo category, ignore")
                        continue
                    else:
                        _app_category = _config.get("Desktop Entry", "Categories").strip()
                        _app_category_info = categories.get(_app_category) # tags + directories
                    _app_menu_paths = ""
                    _app_tags = ""
                    if _app_category_info:
                        _app_menu_paths = "/".join(_app_category_info.get('directories'))
                        _app_tags = "|".join(_app_category_info.get('tags'))
                    _app_exec_cmd = _config.get("Desktop Entry", "Exec")
                    print (f"\texec cmd: {_app_exec_cmd}")
                    _app_exec_mode = "module"
                    _app_module = ""
                    _app_singularity_image = ""
                    # look info exec
                    #### MASSIVE - they are using /usr/local/desktop/desktop_start_arg to load modules
                    if "desktop_start_arg" in _app_exec_cmd:
                        _app_exec_mode = "module"
                        _exec_cmd_parts = _app_exec_cmd.split(" ")
                        if len(_exec_cmd_parts) > 3:
                            _app_module = _exec_cmd_parts[1]
                            # override whatever version extracted from name
                            _app_version = _exec_cmd_parts[2]
                        else:
                            continue
                    print (f"\tapp name={_app_name} version={_app_version} app module={_app_module}")
                    ############## continue     
                    _exec_script_search = re.search(r"(\/.*)*\.sh", _app_exec_cmd)
                    if _exec_script_search:
                        _exec_script = _exec_script_search.group()
                        if ' ' in _exec_script:
                            _exec_script = _exec_script.split(' ')[-1]
                        #print (f"\texec bash cmd: {_exec_script}")
                        ### if exec script exists 
                        if os.path.exists(_exec_script):
                            # read the file
                            with open (_exec_script, "r") as _exec_f:
                                for _line in _exec_f:
                                    _line = _line.strip()
                                    if _line.startswith("#"):
                                        continue
                                    _module_load_regex = re.search("module load \w+", _line)
                                    if _module_load_regex:
                                        _module_load_str = _module_load_regex.group()
                                        _module_to_be_loaded = _module_load_str.replace("module load", "").strip() 
                                        if _module_to_be_loaded == 'singularity':
                                            _app_exec_mode = 'singularity'
                                        else:
                                            _app_exec_mode = 'module'
                                            _app_module = _module_to_be_loaded  
                                    if _app_exec_mode == "singularity":
                                        _simgFileSearch = re.search(r"(\/[^\s]*)*\.simg", _line)
                                        if _simgFileSearch:
                                            _app_singularity_image = _simgFileSearch.group()
                                        ### this is specific to neurodesk-nobody should do this really
                                        if "neurodesk" in _exec_script and os.path.exists(neurodesk_containers_dir):
                                            _neuroDeskSearch = re.search(r"fetch_and_run.sh .*", _line)
                                            if _neuroDeskSearch:
                                                _neuroDeskStr = _neuroDeskSearch.group()
                                                _neuroDeskStrParts = _neuroDeskStr.split(" ")[1:]
                                                _container_folder_path = os.path.join(neurodesk_containers_dir, "_".join(_neuroDeskStrParts) )
                                                if os.path.exists(_container_folder_path):
                                                    # list this dir to find smig file
                                                    for _f in os.listdir( _container_folder_path ):
                                                        if os.path.isfile(os.path.join(_container_folder_path, _f)) and ".simg" in _f:
                                                            _app_singularity_image = os.path.join(_container_folder_path, _f)

                                                
                    # name, version, menu_path, tags, exec_type, module_name, singularityimagepath
                    if _app_menu_paths.strip() != '':
                        _output_line=f"{cvl_site},{_app_name.replace(',', '-')},{_app_version}, {_app_menu_paths}, {_app_tags}, {_app_exec_mode}, {_app_module}, {_app_singularity_image}\n"    
                        # write to csv
                        out.write(_output_line)
                 


def main(arguments=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        prog='list',
        description='list CVL tools')
    parser.set_defaults(func=do_list)
    parser.add_argument('--xdg-applications-dirs', nargs='+', help='XDG applications dirs. Wiener=/scratch/cvl-admin/xdg_data_dirs/applications',  type=str)
    parser.add_argument('--xdg-desktop-dir', help='XDG desktop dir. Wiener=/scratch/cvl-admin/xdg_data_dirs/applications', type=str)
    parser.add_argument('--xdg-menu-dir', help='XDG menu dir. Wiener=/scratch/cvl-admin/xdg_data_dirs/desktop-directories',  type=str)	
    parser.add_argument('--xdg-menu-files', nargs='+', help='XDG menu files to look at, only the top menu files, merged files not needed', type=str)	
    parser.add_argument('--neurodesk-containers-dir', help='Neurodesk containers - maybe UQ specific - optional', type=str, default='/scratch/cvl-admin/neurodesk/local/containers')
    parser.add_argument('--cvl-site', help='CVL site', type=str)
    parser.add_argument('--output-file', help='output file', type=str)
    args = parser.parse_args(arguments)
    return args.func(args)

if __name__ == "__main__":
    main()
