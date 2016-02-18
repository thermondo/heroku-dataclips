import click
from api import Client


@click.command()
@click.argument('email')
@click.argument('password')
@click.argument('source_resource')
@click.argument('destination_resource')
def move_all(email, password, source_resource, destination_resource):
    heroku = Client(email, password)
    resources = {
        resource['resource_name']: resource['id']
        for resource in heroku.get_heroku_resources()
    }

    if source_resource not in resources:
        raise Exception('`source_resource` not a heroku resource')
    if destination_resource not in resources:
        raise Exception('`destination_resource` not a heroku resource')

    source_dataclips_slugs = [
        dataclip['slug']
        for dataclip in heroku.get_all_dataclips()
        if dataclip['heroku_resource_id'] == resources[source_resource]
    ]

    for source_dataclip_slug in source_dataclips_slugs:
        heroku.move_to_resource(source_dataclip_slug, resources[destination_resource])

if __name__ == '__main__':
    move_all()