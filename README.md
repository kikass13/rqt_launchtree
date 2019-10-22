# rqt_launchtree ![img](https://travis-ci.org/pschillinger/rqt_launchtree.svg?branch=kinetic)
An RQT plugin for hierarchical launchfile configuration introspection.

![img](http://philserver.bplaced.net/img/rqt_launchtree_screenshot.png)



# How to install [sts]

```
catkin build rqt_launchtree
```

or

```
python setup_usr.py develop
```



# How to use [sts]

Source your proper environment, when used in combination with the deployment you have to first source the env-loader with

```
source /tmp/sts_env_loader.sh
```

When built via catkin you can use the "normal" way of running rqt plugins (by running rqt and selecting the tool) or by running it directly with

```
rosrun rqt_launchtree rqt_launchtree launchfile:=/home/fgn/ahl_adas_9c34de1a/launch/main.launch stack:=/home/fgn/ahl_adas_9c34de1a/
```

