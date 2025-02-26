import openstack
import json


def connect_to_openstack():
    """
    Connette al cloud OpenStack utilizzando le credenziali di ambiente
    o un file di configurazione (clouds.yaml) già configurato.
    """
    conn = openstack.connection.Connection()
    return conn


# ----------------------------------------------------------------------------
# Sezione: Monitoraggio e gestione istanze
# ----------------------------------------------------------------------------

def list_instances(conn):
    """
    Elenca tutte le istanze attive nel cloud OpenStack e le salva in un file JSON.
    """
    instances = []
    print("Listing instances:")
    for server in conn.compute.servers():
        instance_data = {
            "ID": server.id,
            "Name": server.name,
            "Status": server.status
        }
        instances.append(instance_data)
        print(f"ID: {server.id}, Name: {server.name}, Status: {server.status}")

    with open("instances.json", "w") as file:
        json.dump(instances, file, indent=4)
    print("Instances saved to instances.json")


def get_instance_details(conn, instance_id):
    """
    Ottiene i dettagli di una specifica istanza e li salva in un file JSON.
    """
    server = conn.compute.get_server(instance_id)
    if server:
        details = {
            "ID": server.id,
            "Name": server.name,
            "Status": server.status,
            "CPU": server.vcpus,
            "RAM": server.ram,
            "Storage": server.disk,
            "Created At": server.created_at,
            "Updated At": server.updated_at,
            "Networks": server.addresses
        }
        print(json.dumps(details, indent=4))
        with open(f"instance_{instance_id}.json", "w") as file:
            json.dump(details, file, indent=4)
        print(f"Details saved to instance_{instance_id}.json")
    else:
        print("Instance not found.")


def check_instance_usage(conn, instance_id):
    """
    Verifica l'utilizzo delle risorse di una specifica istanza (flavor)
    e le salva in un file JSON.
    """
    server = conn.compute.get_server(instance_id)
    if server:
        usage = {
            "vCPUs": server.flavor.vcpus,
            "RAM": server.flavor.ram,
            "Disk": server.flavor.disk
        }
        print(json.dumps(usage, indent=4))
        with open(f"usage_{instance_id}.json", "w") as file:
            json.dump(usage, file, indent=4)
        print(f"Usage details saved to usage_{instance_id}.json")
    else:
        print("Instance not found.")


def start_instance(conn, instance_id):
    """
    Avvia un'istanza spenta.
    """
    server = conn.compute.get_server(instance_id)
    if server:
        conn.compute.start_server(server)
        print(f"Istanza {instance_id} avviata.")
    else:
        print(f"Istanza {instance_id} non trovata.")


def stop_instance(conn, instance_id):
    """
    Ferma un'istanza in esecuzione.
    """
    server = conn.compute.get_server(instance_id)
    if server:
        conn.compute.stop_server(server)
        print(f"Istanza {instance_id} fermata.")
    else:
        print(f"Istanza {instance_id} non trovata.")


def restart_instance(conn, instance_id):
    """
    Riavvia un'istanza in esecuzione (soft reboot).
    """
    server = conn.compute.get_server(instance_id)
    if server:
        conn.compute.reboot_server(server, 'SOFT')
        print(f"Istanza {instance_id} riavviata.")
    else:
        print(f"Istanza {instance_id} non trovata.")


def delete_instance(conn, instance_id):
    """
    Elimina un'istanza esistente.
    """
    server = conn.compute.get_server(instance_id)
    if server:
        conn.compute.delete_server(server)
        print(f"Istanza {instance_id} eliminata con successo.")
    else:
        print(f"Istanza {instance_id} non trovata.")


# ----------------------------------------------------------------------------
# Sezione: Flavors
# ----------------------------------------------------------------------------

def list_flavors(conn):
    """
    Elenca tutti i flavor disponibili (vCPUs, RAM, Disco) nel cloud OpenStack.
    """
    flavors = []
    for flavor in conn.compute.flavors():
        flavor_info = {
            "Name": flavor.name,
            "ID": flavor.id,
            "vCPUs": flavor.vcpus,
            "RAM": flavor.ram,
            "Disk": flavor.disk
        }
        flavors.append(flavor_info)
        print(flavor_info)

    with open("flavors.json", "w") as file:
        json.dump(flavors, file, indent=4)
    print("Flavors saved to flavors.json")


# ----------------------------------------------------------------------------
# Sezione: Volumi e loro gestione
# ----------------------------------------------------------------------------

def list_volumes(conn):
    """
    Elenca tutti i volumi presenti e li salva su file JSON.
    """
    volumes_list = []
    for volume in conn.block_storage.volumes():
        vol_info = {
            "ID": volume.id,
            "Name": volume.name,
            "Status": volume.status,
            "Size (GB)": volume.size
        }
        volumes_list.append(vol_info)
        print(vol_info)

    with open("volumes.json", "w") as file:
        json.dump(volumes_list, file, indent=4)
    print("Volumes saved to volumes.json")


def attach_volume(conn, instance_id, volume_id):
    """
    Collega un volume a una specifica istanza.
    """
    server = conn.compute.get_server(instance_id)
    volume = conn.block_storage.get_volume(volume_id)
    if server and volume:
        conn.compute.create_volume_attachment(
            server,
            volumeId=volume.id
        )
        print(f"Volume {volume_id} collegato all'istanza {instance_id}.")
    else:
        print("Server o volume non trovato.")


def detach_volume(conn, instance_id, volume_id):
    """
    Scollega un volume da una specifica istanza.
    """
    server = conn.compute.get_server(instance_id)
    if server:
        attachments = conn.compute.volume_attachments(server)
        for attachment in attachments:
            if attachment.volume_id == volume_id:
                conn.compute.delete_volume_attachment(attachment, server)
                print(f"Volume {volume_id} scollegato dall'istanza {instance_id}.")
                return
        print(f"Volume {volume_id} non risulta collegato all'istanza {instance_id}.")
    else:
        print("Server non trovato.")


# ----------------------------------------------------------------------------
# Sezione: Snapshot
# ----------------------------------------------------------------------------

def create_snapshot(conn, instance_id, snapshot_name):
    """
    Crea uno snapshot (immagine) dell'istanza specificata.
    """
    server = conn.compute.get_server(instance_id)
    if server:
        image = conn.compute.create_server_image(server, name=snapshot_name)
        if image:
            print(f"Snapshot '{snapshot_name}' creato con ID: {image.id}")
            # Attende che l'immagine sia pronta (opzionale, dipende dalla versione):
            image = conn.image.wait_for_image(image)
            print(f"Snapshot '{snapshot_name}' è ora in stato: {image.status}")
        else:
            print("Impossibile creare lo snapshot.")
    else:
        print("Server non trovato.")


# ----------------------------------------------------------------------------
# Sezione: Monitoraggio di base (demo)
# ----------------------------------------------------------------------------

def monitor_resources():
    """
    Monitora le risorse delle istanze OpenStack e salva i dati (demo).
    """
    conn = connect_to_openstack()
    list_instances(conn)
    instance_id = input("Enter instance ID to get details: ")
    get_instance_details(conn, instance_id)


# ----------------------------------------------------------------------------
# Sezione: Funzioni aggiuntive di monitoraggio/gestione
# ----------------------------------------------------------------------------

def list_networks(conn):
    """
    Elenca tutte le reti disponibili nel progetto corrente su OpenStack.
    """
    networks_list = []
    for net in conn.network.networks():
        net_info = {
            "ID": net.id,
            "Name": net.name,
            "Status": net.status,
            "Subnets": net.subnets,
            "Is External": net.is_external
        }
        networks_list.append(net_info)
        print(net_info)

    with open("networks.json", "w") as file:
        json.dump(networks_list, file, indent=4)
    print("Networks saved to networks.json")


def list_subnets(conn):
    """
    Elenca tutte le subnet disponibili e le salva su file JSON.
    """
    subnets_list = []
    for subnet in conn.network.subnets():
        subnet_info = {
            "ID": subnet.id,
            "Name": subnet.name,
            "Network ID": subnet.network_id,
            "CIDR": subnet.cidr,
            "Gateway IP": subnet.gateway_ip
        }
        subnets_list.append(subnet_info)
        print(subnet_info)

    with open("subnets.json", "w") as file:
        json.dump(subnets_list, file, indent=4)
    print("Subnets saved to subnets.json")


def list_security_groups(conn):
    """
    Elenca tutti i security group definiti nel progetto corrente.
    """
    sg_list = []
    for sg in conn.network.security_groups():
        sg_info = {
            "ID": sg.id,
            "Name": sg.name,
            "Description": sg.description,
            "Rules": []
        }
        for rule in sg.security_group_rules:
            rule_info = {
                "Protocol": rule.protocol,
                "Port Range": (
                f"{rule.port_range_min}-{rule.port_range_max}"
                if rule.port_range_min is not None
                else "Any"
            ),
                "Direction": rule.direction,
                "Remote IP Prefix": rule.remote_ip_prefix
            }
            sg_info["Rules"].append(rule_info)
        sg_list.append(sg_info)
        print(json.dumps(sg_info, indent=4))

    with open("security_groups.json", "w") as file:
        json.dump(sg_list, file, indent=4)
    print("Security Groups saved to security_groups.json")


def list_images(conn):
    """
    Elenca tutte le immagini disponibili nel progetto corrente (o globali, se visibili).
    """
    images_list = []
    for image in conn.image.images():
        img_info = {
            "ID": image.id,
            "Name": image.name,
            "Status": image.status,
            "Visibility": image.visibility,
            "Disk Format": image.disk_format,
            "Size (Bytes)": image.size
        }
        images_list.append(img_info)
        print(img_info)

    with open("images.json", "w") as file:
        json.dump(images_list, file, indent=4)
    print("Images saved to images.json")


def list_projects(conn):
    """
    Elenca i progetti (tenant) se l'utente possiede i permessi necessari
    (ruolo admin o project-level con accesso specifico).
    """
    projects_list = []
    for project in conn.identity.projects():
        project_info = {
            "ID": project.id,
            "Name": project.name,
            "Domain ID": project.domain_id,
            "Enabled": project.is_enabled
        }
        projects_list.append(project_info)
        print(project_info)

    with open("projects.json", "w") as file:
        json.dump(projects_list, file, indent=4)
    print("Projects saved to projects.json")


def show_quota_usage(conn, project_id=None):
    """
    Mostra l'utilizzo delle quote (es: istanze, vCPUs, RAM) per il progetto corrente
    o per un progetto specificato, se l'utente dispone dei permessi.
    """
    # Se il project_id non viene passato, utilizza quello della connessione
    if not project_id:
        project_id = conn.current_project_id  # Potrebbe variare in base alla configurazione
    # Recupera le quote compute (dipende dalla versione di openstacksdk / OpenStack)
    # In alcuni casi: conn.compute.get_quota_set(project_id)
    # In altri: conn.get_compute_quotas(project_id)
    # Verifica quale funzione è supportata dalla tua libreria.
    # Esempio generico:
    quotas = conn.get_compute_quotas(project_id)

    quota_info = {
        "Project ID": project_id,
        "Instances Quota": quotas.instances,
        "Instances Used": quotas.instances_used,
        "vCPUs Quota": quotas.cores,
        "vCPUs Used": quotas.cores_used,
        "RAM (MB) Quota": quotas.ram,
        "RAM (MB) Used": quotas.ram_used
    }

    print(json.dumps(quota_info, indent=4))
    with open(f"quota_usage_{project_id}.json", "w") as file:
        json.dump(quota_info, file, indent=4)
    print(f"Quota usage saved to quota_usage_{project_id}.json")


# ----------------------------------------------------------------------------
# Esempio di "main"
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    """
    Di seguito un esempio semplice (demo) di utilizzo dello script. 
    Puoi modificare, commentare o decommentare in base alle tue necessità.
    """
    
    # Esempio 1: Avvia la routine di monitoraggio base
    monitor_resources()
    
    # Esempio 2: Oppure, crea manualmente la connessione
    # conn = connect_to_openstack()
    #
    # # Esegui alcune funzioni di monitoraggio
    # list_instances(conn)
    # list_volumes(conn)
    # list_flavors(conn)
    # list_networks(conn)
    # list_subnets(conn)
    # list_security_groups(conn)
    # list_images(conn)
    #
    # # Mostra dettagli di una determinata istanza (chiedi ID manualmente, ad esempio)
    # instance_id = input("Enter instance ID for usage check: ")
    # check_instance_usage(conn, instance_id)
    #
    # # Se hai i permessi e vuoi vedere i progetti
    # list_projects(conn)
    #
    # # Se hai i permessi e vuoi mostrare le quote
    # show_quota_usage(conn)

    pass
