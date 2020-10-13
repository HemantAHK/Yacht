import docker
import json

### IMAGES ###
def get_images():
    dclient = docker.from_env()
    containers = dclient.containers.list(all=True)
    images = dclient.images.list()
    image_list = []
    for image in images:
        attrs = image.attrs
        for container in containers:
            try:
                if container.image.id in image.id:
                    attrs.update({'inUse': True})
            except Exception as exc:
                if exc.status_code == 404:
                    pass
        if attrs.get('inUse') == None:
            attrs.update({'inUse': False})

        image_list.append(attrs)
    return image_list

def write_image(image_tag):
    delim = ":"
    dclient = docker.from_env()
    repo, tag = None, image_tag
    if delim in image_tag:
                repo, tag = tag.split(delim, 1)
    else:
        repo = image_tag
        tag = "latest"
    image = dclient.images.pull(repo, tag)
    return get_images()

def get_image(image_id):
    dclient = docker.from_env()
    containers = dclient.containers.list(all=True)
    image = dclient.images.get(image_id)
    attrs=image.attrs
    for container in containers:
        try:
            if container.image.id in image.id:
                attrs.update({'inUse': True})
        except Exception as exc:
            if exc.status_code == 404:
                pass
    if attrs.get('inUse') == None:
        attrs.update({'inUse': False})
    return attrs

def update_image(image_id):
    dclient = docker.from_env()
    if type(image_id) == str:
        image = dclient.images.get(image_id)
        new_image = dclient.images.get_registry_data(image.tags[0])
        new_image.pull()
        return get_image(image_id)
    if type(image_id) == list:
        updated_list = []
        for _id in image_id:
            image = dclient.images.get(image_id)
            new_image = dclient.images.get_registry_data(image.tags[0])
            new_image.pull()
            updated_list.append(new_image)
        return updated_list()

def delete_image(image_id):
    dclient = docker.from_env()
    image = dclient.images.get(image_id)
    dclient.images.remove(image_id, force=True)
    return image.attrs

### Volumes ###
def get_volumes():
    dclient = docker.from_env()
    containers = dclient.containers.list(all=True)
    volumes = dclient.volumes.list()
    volume_list = []
    for volume in volumes:
        attrs = volume.attrs
        for container in containers:
            try:
                if any(d['Source'] == volume.attrs['Mountpoint'] for d in container.attrs['Mounts']):
                    attrs.update({'inUse': True})
            except Exception as exc:
                if exc.status_code == 404:
                    pass
        if attrs.get('inUse') == None:
            attrs.update({'inUse': False})
        volume_list.append(attrs)
    return volume_list

def write_volume(volume_name):
    dclient = docker.from_env()
    volume = dclient.volumes.create(name=volume_name)
    return get_volumes()

def get_volume(volume_id):
    dclient = docker.from_env()
    containers = dclient.containers.list(all=True)
    volume = dclient.volumes.get(volume_id)
    attrs=volume.attrs
    for container in containers:
        try:
            if any(d['Source'] == volume.attrs['Mountpoint'] for d in container.attrs['Mounts']):
                attrs.update({'inUse': True})
        except Exception as exc:
            if exc.status_code == 404:
                pass
    if attrs.get('inUse') == None:
        attrs.update({'inUse': False})
    return attrs

# def update_volume(volume_id):
#     dclient = docker.from_env()
#     if type(volume_id) == str:
#         volume = dclient.volumes.get(volume_id)
#         new_volume = dclient.volumes.get_registry_data(volume.tags[0])
#         new_volume.pull()
#         return get_volume(volume_id)
#     if type(volume_id) == list:
#         updated_list = []
#         for _id in volume_id:
#             volume = dclient.volumes.get(volume_id)
#             new_volume = dclient.volumes.get_registry_data(volume.tags[0])
#             new_volume.pull()
#             updated_list.append(new_volume)
#         return updated_list()

def delete_volume(volume_id):
    dclient = docker.from_env()
    volume = dclient.volumes.get(volume_id)
    volume.remove(force=True)
    return volume.attrs

def prune_resources(resource):
    dclient = docker.from_env()
    action = getattr(dclient, resource)
    if resource == 'images':
        deleted_resource = action.prune(filters={'dangling': False})
    else:
        deleted_resource = action.prune()
    return deleted_resource