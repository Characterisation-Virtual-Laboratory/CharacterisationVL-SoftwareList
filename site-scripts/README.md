CharacterisationVL-SoftwareList

Tools to consolidate a listing of CVL software available at the various sites.


# list.py (Python >=3.6)
This small script parses Mate's menu configuration files to get a list of installed software.
It also looks into the Exec script to determine how the sofware is launched (singulraity or module).

To run:

pip3 install -r requirements.txt

Parameters:
* xdg-applications-dirs: list of folders containing *.desktop files
* xdg-desktop-dir: 1 folder containing *.directory files
* xdg-menu-dir: 1 folder containing *.menu files
* xdg-menu-files: list of menu files to be considered
* cvl-site: name of cvl site
* output-file

## At wiener
```
python3 list.py --xdg-applications-dirs "/scratch/cvl-admin/xdg_data_dirs/applications" \
		--xdg-desktop-dir "/scratch/cvl-admin/xdg_data_dirs/desktop-directories" \
		--xdg-menu-dir "/scratch/cvl-admin/xdg_config_dirs/menus" \
		--xdg-menu-files "cvl.menu" \
		--cvl-site "CVl@Wiener" --output-file "CVl@Wiener-21Sep2021.csv"
```
## At Awoonga
```
python3 list.py --xdg-applications-dirs "/sw7/CVL/xdg_data_dirs/applications" \
		--xdg-desktop-dir "/sw7/CVL/xdg_data_dirs/desktop-directories" \
		--xdg-menu-dir "/sw7/CVL/xdg_config_dirs/menus" \
		--xdg-menu-files "cvl.menu" \
		--cvl-site "CVl@Qld" --output-file "CVl@Qld-21Sep2021.csv"
```

## At massive
The best way to obtain a list of all software modules is to run the bash script
`listModules-massive.sh`. This will build a full list. The example below will
build a list of software modules available in the Desktop menu, which is a small
subset of all software.

```
python3 list.py --cvl-site "CVl@Massive"  --output-file "CVl@Massive-21Sep2021.csv" \
				--xdg-applications-dirs "/usr/local/share/applications" "/usr/local/desktop/services/massive-p4/xdg_config/applications-merged/application" \
                --xdg-desktop-dir "/usr/local/share/desktop-directories" \
                --xdg-menu-dir "/usr/local/desktop/services/massive-p4/xdg_config/menus" \
                --xdg-menu-files "ansto.menu" "cryoem.menu" "flowcytometry.menu" "general-imaging.menu" \
                "lightmicroscopy.menu" "neutronbeamimaging.menu" "bioinformatics.menu" \
                "full.menu" "generalscientific.menu" "neuroimaging.menu" "structural-biology.menu"
```

# Output
CSV header
```
site, name, version, menu_path, tags, exec_type, module_name, singularityimagepath

```

fields:

* site: site name
* name: name of the software
* versoin: version of the software
* menu_path: path leads to the app. For instance: Applications/Characterisation Virtual Laboratory/Neuroimaging Tools/VNM Neuroimaging/Image Registration/fsl
* tags: any tags related to this app | separated. Example: Dsistudio|Diffusion Imaging|VNM Neuroimaging|Applications|Neuroimaging|Characterisation Virtual Laboratory|Applications
* exec_type: whether the app is loaded from singularity or module
* module_name: module name if exec_type=module
* singularityimagepath - path to simg file if exec_type=singulraity
