#!/usr/bin/env python3

import logging

# Plugin base per openstackclient
from openstackclient.common import command

# Libreria per chiamare le API OpenStack
import openstack

# Necessario per installare questo file come plugin
from setuptools import setup

LOG = logging.getLogger(__name__)

class SimpleVolumeCost(command.Command):
    """Plugin minimal: calcola il costo basato sui volumi Cinder."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--rate",
            type=float,
            default=0.1,
            help="Costo per GB dei volumi (Cinder). Default: 0.1 USD/GB/mese"
        )
        return parser

    def take_action(self, parsed_args):
        # Connessione al cloud (usa credenziali da env o clouds.yaml)
        conn = openstack.connect()

        # Recupera i volumi e somma i GB allocati
        volumes = conn.block_storage.volumes(details=True)
        total_gb = sum(vol.size for vol in volumes)

        # Calcola il costo in base alla tariffa specificata
        cost = total_gb * parsed_args.rate

        # Mostra i risultati
        print("\n=== OpenStack Volume Cost ===")
        print(f"Spazio totale su Cinder: {total_gb} GB")
        print(f"Tariffa: {parsed_args.rate} USD/GB/mese")
        print(f"Costo mensile stimato: {cost:.2f} USD\n")


def do_setup():
    """
    Installazione del plugin come pacchetto Python (entry point per 'openstack').
    """
    setup(
        name="volume-cost-plugin-single-file",
        version="0.1.0",
        py_modules=["openstack_volume_cost_plugin"],  # Deve corrispondere al nome di questo file (senza .py)
        install_requires=[
            "openstackclient",
            "openstacksdk"
        ],
        entry_points={
            # Creiamo un'estensione "cost" per openstackclient
            'openstack.cli.extension': [
                'cost = openstack_volume_cost_plugin',
            ],
            # Aggiungiamo il comando "volume" dentro "cost"
            'openstack.cost.v1': [
                'volume = openstack_volume_cost_plugin:SimpleVolumeCost',
            ],
        }
    )


if __name__ == "__main__":
    # Se lo lanci direttamente (es. python openstack_volume_cost_plugin.py install),
    # viene chiamata la procedura di setup
    do_setup()
