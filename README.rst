Upload software modules list to a Google Sheet
==============================================

To provide a consolidated list of software modules available at various CVL
sites. (e.g CVL@MASSIVE, CVL@Wiener, CVL@Awoonga, CVL@UWA), this software has
been developed to upload a generated CSV file to a common Google Sheet, from
where the final module list can be consolidated for publication.

..

    To ensure this software module list is updated over time, a cron job should
    be setup at each site. This cron job will run a script that builds the list
    of modules into a .csv formatted file. It will then call this software to
    upload the .csv file to the common Google Sheet. Each site will upload the
    .csv to its own uniquely named worksheet, from which the software list can
    be consolidated for all sites.

It is acknowledged that software at each CVL site has been installed
differently. This approach allows the script that generates the .csv file, to be
customised per site.

Installation
------------

ModulesToGoogle requires Python 3 to be installed on your system.

The following steps are an example:

.. code-block:: bash

    - create a virtual environment
        python3 -m venv /opt/modules-to-google

    - activate the virtual environment
        source /opt/modules-to-google/bin/activate

    - Install the software
        pip install git+https://github.com/Characterisation-Virtual-Laboratory/CharacterisationVL-SoftwareList.git#egg=ModulesToGoogle


Installation for Development
----------------------------

The following steps are an example:

.. code-block:: bash

    - create a virtual environment
        python3 -m venv /opt/modules-to-google-dev

    - activate the virtual environment
        source /opt/modules-to-google-dev

    - Create a source folder and clone the repository
        mkdir /opt/modules-to-google-dev/src
        cd /opt/modules-to-google-dev/src
        git clone https://github.com/Characterisation-Virtual-Laboratory/CharacterisationVL-SoftwareList.git

    - Install from source
        cd CharacterisationVL-SoftwareList/
        pip install --upgrade --force-reinstall -e . #egg=ModulesToGoogle

Once code modifications have been made, ensure the virtual environment is
activated, then run the same pip command as above from the same folder.

Configuration
-------------

The sample config.yml file can be found in the 'etc' folder, below is a copy of it
with explanation of the settings.

.. code-block:: bash

    ---
    service-account-secrets-file: "secrets.json"
    modules_file: "massive_modules.csv"
    spreadsheet_id: "11f27MLbWKb94sUFbOEuaWw8AD45er5o-EasYBK9XBulBpg"
    worksheet: "Monash"

    log-level: logging.DEBUG
    log-files:
        modules-to-google: /opt/modules-to-google/var/log/modules-to-google.log


- service-account-secrets-file:  Path to local file containing the JSON web token. e.g. secrets.json
- modules_file:  Path to local file containing the list of software modules. e.g. massive_modules.csv
- spreadsheet_id:  Google ID of the sheet to be updated.
- worksheet: name of the worksheet, within the spreadsheet to put the .csv data.
- log-level: Possible values are: logging.DEBUG, logging.INFO, logging.ERROR, logging.WARNING
- log-files: modules-to-google: Path to the log file. e.g. var/log/modules-to-google.log

Running
-------

.. code-block:: bash

    $ modules-to-google
    usage: modules-to-google [-h] [--config CONFIG]

    modules-to-google: upload a list of HPC software modules to a specified Google Worksheet.

    optional arguments:
      -h, --help       show this help message and exit
      --config CONFIG  path to config.yml

Cron Job setup
--------------

The file `build-modules-list.sh` is an example of how to setup the whole process.
This script executes listModules-massive.sh to obtain a .csv file for uploading and then executes 'modules-to-google'
to upload to the Google Sheet.

.. code-block:: bash

  #!/bin/bash

  #Output the list of modules
  ./opt/modules-to-google/listModules-massive.sh /opt/modules-to-google/massive_modules.csv

  source /opt/modules-to-google/bin/activate
  modules-to-google --config /opt/modules-to-google/etc/config.yml


The folder 'site-scripts' contains details on how to generate the modules list '.csv'
file at each site. Customise the above script to suite your site.


An example crontab setup ensuring the job runs daily at 1:00 am. Customise to
your requirements.

.. code-block:: bash

    #Ansible: modules-to-google crontab
    0 1 * * * /opt/modules-to-google/build-modules-list.sh
