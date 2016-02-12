import json
from pathlib import Path

import click
from api import Client


@click.command()
@click.argument('email')
@click.argument('password')
@click.argument('path')
def backup(email, password, path):
    heroku = Client(email, password)
    path = Path(path)
    if not path.exists():
        path.mkdir()

    for clip in heroku.get_all_dataclips():
        slug = clip['slug']
        print(clip['name'])

        destination_dir = path / slug
        destination_dir.mkdir()

        with (destination_dir / 'clip.json').open('w') as output_file:
            json.dump(clip, output_file)

        for version in heroku.get_dataclip_versions(slug):
            print(version['version_number'])

            version_dir = destination_dir / str(version['version_number'])
            version_dir.mkdir()

            with (version_dir / 'clip.json').open('w') as output_file:
                json.dump(version, output_file)

            with (version_dir / 'clip.sql').open('w') as output_file:
                output_file.write(version['sql'])


if __name__ == '__main__':
    backup()
