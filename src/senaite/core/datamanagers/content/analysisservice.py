# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import Unauthorized
from bika.lims import api
from bika.lims.interfaces import IAnalysisService
from Products.Archetypes.utils import mapply
from senaite.core import logger
from senaite.core.datamanagers.base import DataManager
from zope.component import adapter


@adapter(IAnalysisService)
class AnalysisServiceDataManager(DataManager):
    """Data Manager for Analysis Services
    """

    @property
    def fields(self):
        return api.get_fields(self.context)

    def is_field_readable(self, field):
        """Checks if the field is readable
        """
        return field.checkPermission("get", self.context)

    def is_field_writeable(self, field, context=None):
        """Checks if the field is writeable
        """
        if context is None:
            context = self.context
        return field.checkPermission("set", context)

    def get_field_by_name(self, name):
        """Get the field by name
        """
        field = self.fields.get(name)

        # try to fetch the field w/o the `get` prefix
        # this might be the case is some listings
        if field is None:
            # ensure we do not have the field setter as column
            name = name.split("get", 1)[-1]
            field = self.fields.get(name)

        return field

    def get(self, name):
        """Get sample field
        """
        # get the schema field
        field = self.get_field_by_name(name)

        # check if the field exists
        if field is None:
            raise AttributeError("Field '{}' not found".format(name))

        # Check the permission of the field
        if not self.is_field_readable(field):
            raise Unauthorized("Field '{}' not readable!".format(name))

        # return the value with the field accessor
        if hasattr(field, "getAccessor"):
            accessor = field.getAccessor(self.context)
            return accessor()
        else:
            # Set the value on the field directly
            return field.get(self.context)

    def set(self, name, value):
        """Set sample field or analysis result
        """
        # set of updated objects
        updated_objects = set()

        # get the schema field
        field = self.get_field_by_name(name)

        if field is None:
            raise AttributeError("Field '{}' not found".format(name))

        # Check the permission of the field
        if not self.is_field_writeable(field):
            logger.error("Field '{}' not writeable!".format(name))
            return []
        # get the field mutator (works only for AT content types)
        if hasattr(field, "getMutator"):
            mutator = field.getMutator(self.context)
            mapply(mutator, value)
        else:
            # Set the value on the field directly
            field.set(self.context, value)

        updated_objects.add(self.context)

        # return a unified list of the updated objects
        return list(updated_objects)
