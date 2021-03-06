# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import tarfile

import django.db.models.deletion
import filer.fields.file
from django.conf import settings
from django.db import migrations


def migrate_to_filer(apps, schema_editor):
    # Because filer is polymorphic, Djangos migration can't handle
    from filer.models import File
    FileInstance = apps.get_model('djangocms_file', 'File')
    plugins = FileInstance.objects.all()
    remove_files = []

    for plugin in plugins:  # pragma: no cover
        if plugin.file:
            filename = plugin.file.name.split('/')[-1]
            old_path = os.path.join(settings.MEDIA_ROOT, str(plugin.file))
            print("Will use {} as filename.".format(filename))
            try:
                filesrc = File.objects.get_or_create(
                    file=plugin.file.file,
                    defaults={
                        'name': filename,
                        'original_filename': filename,
                    }
                )[0]
            except IOError as e:
                print(e)
            else:
                plugins.filter(pk=plugin.pk).update(file_src=filesrc)
                remove_files.append(old_path)
    remove_files = set(list(remove_files))
    if len(remove_files):
        with tarfile.open(os.path.abspath(os.path.join(settings.MEDIA_ROOT, '../cms_page_media_file_backup.tar.gz')),
                          'w:gz') as tar:
            for old_path in remove_files:
                tar.add(old_path, recursive=False)
                try:
                    os.remove(old_path)
                except:
                    pass
                else:
                    print("Remove migrated {}".format(old_path))


class Migration(migrations.Migration):
    dependencies = [
        ('filer', '0006_auto_20160623_1627'),
        ('djangocms_file', '0005_auto_20160119_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='file_src',
            field=filer.fields.file.FilerFileField(related_name='+', on_delete=django.db.models.deletion.SET_NULL,
                                                   verbose_name='File', blank=True, to='filer.File', null=True),
        ),
        migrations.RunPython(migrate_to_filer),
        migrations.RemoveField(
            model_name='file',
            name='file',
        ),
    ]
