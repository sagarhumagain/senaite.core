# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.sample.samples_filter_bar\
    import SamplesBikaListingFilterBar


class AggregatedanalysesBikaListingFilterBar(SamplesBikaListingFilterBar):
    """
    This class defines a filter bar to make advanced queries in
    BikaListingView. This filter shouldn't override the 'filter by state'
    functionality
    """
    def filter_bar_builder(self):
        """
        The template is going to call this method to create the filter bar in
        bika_listing_filter_bar.pt
        If the method returns None, the filter bar will not be shown.
        :return: a list of dictionaries as the filtering fields or None.
        """
        fields_dict = SamplesBikaListingFilterBar.filter_bar_builder(self)
        fields_dict.append({
            'name': 'date_submited',
            'label': _('Date result submitted'),
            'type': 'date_range',
        })
        return fields_dict

    def get_filter_bar_queryaddition(self):
        """
        This function gets the values from the filter bar inputs in order to
        create a query accordingly.
        Only returns the once that can be added to contentFilter dictionary.
        :return: a dictionary to be added to contentFilter.
        """
        filter_dict = self.get_filter_bar_dict()
        query_dict =\
            SamplesBikaListingFilterBar.get_filter_bar_queryaddition(self)
        # Sample condition filter
        if filter_dict.get('sample_condition', ''):
            query_dict['getSampleConditionUID'] =\
                filter_dict.get('sample_condition', '')
        # Print state filter
        if filter_dict.get('print_state', ''):
            query_dict['getAnalysisRequestPrintStatus'] =\
                filter_dict.get('print_state', '')
        query_dict = self.createQueryForDateRange(
            filter_dict, query_dict, 'date_submited', 'getDateSubmitted')
        return query_dict

    def filter_bar_check_item(self, item):
        return True
