from setuptools import setup

setup(
    name="openstack_volume_cost_plugin",
    version="1.0",
    py_modules=["openstack_volume_cost_plugin"],
    install_requires=[
        "openstackclient",
        "openstacksdk"
    ],
    entry_points={
        "openstack.cli.extension": [
            "cost = openstack_volume_cost_plugin"
        ],
        "openstack.cost.v1": [
            "volume = openstack_volume_cost_plugin:SimpleVolumeCost"
        ],
    },
)
