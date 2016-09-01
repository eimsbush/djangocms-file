# -*- coding: utf-8 -*-
"""
Enables the user to add a "File" plugin that displays a file wrapped by
an <anchor> tag.
"""
from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _

from cms.models import CMSPlugin

from djangocms_attributes_field.fields import AttributesField

from filer.fields.file import FilerFileField
from filer.fields.folder import FilerFolderField


LINK_TARGET = (
    ('_self', _('Open in same window.')),
    ('_blank', _('Open in new window.')),
    ('_parent', _('Delegate to parent.')),
    ('_top', _('Delegate to top.')),
)


# Add additional choices through the ``settings.py``.
def get_templates():
    choices = getattr(
        settings,
        'DJANGOCMS_FILE_TEMPLATES',
        [],
    )
    return choices


@python_2_unicode_compatible
class File(CMSPlugin):
    """
    Renders a file wrapped by an anchor
    """
    search_fields = ('name',)

    file_src = FilerFileField(
        verbose_name=_('File'),
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    file_name = models.CharField(
        verbose_name=_('Name'),
        blank=True,
        max_length=255,
        help_text=_('Overrides the default file name with the given value.'),
    )
    link_target = models.CharField(
        verbose_name=_('Link target'),
        choices=LINK_TARGET,
        blank=True,
        max_length=255,
        default='',
    )
    link_title = models.CharField(
        verbose_name=_('Link title'),
        blank=True,
        max_length=255,
    )
    show_file_size = models.BooleanField(
        verbose_name=_('Show file size'),
        blank=True,
        default=False,
        help_text=_('Appends the file size at the end of the name.'),
    )
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
        excluded_keys=['title'],
    )

    # Add an app namespace to related_name to avoid field name clashes
    # with any other plugins that have a field with the same name as the
    # lowercase of the class name of this model.
    # https://github.com/divio/django-cms/issues/5030
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin,
        related_name='%(app_label)s_%(class)s',
        parent_link=True,
    )

    def __str__(self):
        if self.file_src and self.file_src.label:
            return self.file_src.label
        return ugettext('<file is missing>')


@python_2_unicode_compatible
class Folder(CMSPlugin):
    """
    Renders a folder plugin to the selected tempalte
    """
    TEMPLATE_CHOICES = [
        ('default', _('Default')),
    ]

    # The label will be displayed as help text in the structure board view.
    template = models.CharField(
        verbose_name=_('Template'),
        choices=TEMPLATE_CHOICES + get_templates(),
        default=TEMPLATE_CHOICES[0][0],
        max_length=255,
    )
    folder_src = FilerFolderField(
        verbose_name=_('Folder'),
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    link_target = models.CharField(
        verbose_name=_('Link target'),
        choices=LINK_TARGET,
        blank=True,
        max_length=255,
        default='',
    )
    show_file_size = models.BooleanField(
        verbose_name=_('Show file size'),
        blank=True,
        default=False,
        help_text=_('Appends the file size at the end of the name.'),
    )
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
        excluded_keys=['title'],
    )

    # Add an app namespace to related_name to avoid field name clashes
    # with any other plugins that have a field with the same name as the
    # lowercase of the class name of this model.
    # https://github.com/divio/django-cms/issues/5030
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin,
        related_name='%(app_label)s_%(class)s',
        parent_link=True,
    )

    def __str__(self):
        if self.folder_src and self.folder_src.label:
            return self.folder_src.label
        return ugettext('<folder is missing>')
