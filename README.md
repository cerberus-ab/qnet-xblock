# Qnet-xblock Tutorial
Qnet-plus XBlock for Open edX.

### Version
0.4

### Installation
Before start make sure you have:
* git
* python2.7
* fabric
* virtual environment (for dev)

Clone repository using git:
```
$ git clone https://github.com/cerberus-ab/qnet-xblock.git
$ cd qnet-xblock
```

Deploy xblock to Devstack using fabric:
```
$ fab --set conf=<target> deploy
```
Known targets: `sotsbi`

Deploy task uses those commands:
```
$ sudo -u edxapp /edx/bin/pip.edxapp install /tmp/qnet --no-cache-dir
$ /edx/bin/supervisorctl restart edxapp:
```
And then xblock is available in: `/edx/app/edxapp/venvs/edxapp/lib/python2.7/site-packages/qnet`.

Enable xblock in edX Platform ([details](http://edx.readthedocs.io/projects/xblock-tutorial/en/latest/edx_platform/index.html)):
1. Make sure using advanced components is enabled in `edx-platform/lms/envs/common.py`
2. Make sure devstack studio has been started
3. Log in to Studio
4. Course -> Settings -> Advanced Settings -> Advanced Module List -> Add "qnet" -> Save changes

### Development
Activate virtual environment:
```
$ virtualenv venv
$ source venv/bin/activate
```

Install xblock-sdk:
```
$ git clone https://github.com/edx/xblock-sdk.git
$ cd xblock-sdk
$ [sudo] pip install -r requirements/base.txt
$ cd ..
```

Instal xblock:
```
$ [sudo] pip install -e qnet
```

Start local server:
```
$ cd xblock-sdk
$ python manage.py runserver
$ cd ..
```

Local server will start on http://localhost:8000. 

[Customize your XBlock](http://edx.readthedocs.io/projects/xblock-tutorial/en/latest/customize/index.html)  
[Debugg your XBlock and Edxapp](https://openedx.atlassian.net/wiki/display/OpenOPS/Debugging+Edxapp)

### TODO
* Add validation to the studio view form
* Add release task (or flag) to fabfile for auto update deploy (or research --update flag usage)
* Add studio view to workbench for local testing