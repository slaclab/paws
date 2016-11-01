import numpy as np

from slacxop import Operation


class ItemFromSequence(Operation):
    """Extract an item from a sequence.

    Intended for use with strings, lists, and tuples, but may work with other data types.

    Uses the python convention that indexing begins with zero, not one."""

    def __init__(self):
        input_names = ['sequence', 'index']
        output_names = ['item']
        super(ItemFromSequence, self).__init__(input_names, output_names)
        self.input_doc['sequence'] = 'list, tuple, string, or other indexable sequence'
        self.input_doc['index'] = 'index of the item you wish to extract'
        self.output_doc['item'] = 'item extracted from *sequence* at position *index*'
        self.categories = ['MISC']

    def run(self):
        self.outputs['item'] = self.inputs['sequence'][self.inputs['index']]


class ItemRangeFromSequence(Operation):
    """Extract consecutive items from a sequence.

    Intended for use with strings, lists, and tuples, but may work with other data types.

    Uses python indexing conventions.
    """

    def __init__(self):
        input_names = ['sequence', 'start_index', 'end_index']
        output_names = ['slice']
        super(ItemRangeFromSequence, self).__init__(input_names, output_names)
        self.input_doc['sequence'] = 'list, tuple, string, or other indexable sequence'
        self.input_doc['start_index'] = 'starting index of the slice you wish to extract'
        self.input_doc['end_index'] = 'ending index of the slice you wish to extract'
        self.output_doc['slice'] = 'items extracted from *sequence*'
        self.categories = ['MISC']

    def run(self):
        start_index, end_index = type_check_item_range_from_sequence(self.inputs['start_index'], self.inputs['end_index'])
        print self.inputs['sequence'], start_index, end_index
        self.outputs['slice'] = self.inputs['sequence'][start_index : end_index]


def type_check_item_range_from_sequence(start_index, end_index):
    if start_index != None:
        start_index = int(start_index)
    if end_index != None:
        end_index = int(end_index)
    return start_index, end_index


class ItemFromMap(Operation):
    """Extract an item from a sequence.

    Intended for use with lists and tuples, but may work with other data types."""

    def __init__(self):
        input_names = ['map', 'key']
        output_names = ['value']
        super(ItemFromMap, self).__init__(input_names, output_names)
        self.input_doc['map'] = 'dictionary or other map'
        self.input_doc['key'] = 'key to the item you wish to extract'
        self.output_doc['value'] = 'value of the item with key *key* in object *map*'
        self.categories = ['MISC']

    def run(self):
        self.outputs['value'] = self.inputs['map'][ self.inputs['key'] ]

class DummySequences(Operation):
    def __init__(self):
        input_names = []
        output_names = ['list', 'tuple', 'string']
        super(DummySequences, self).__init__(input_names, output_names)
        self.output_doc['list'] = ''
        self.output_doc['tuple'] = ''
        self.output_doc['string'] = ''
        self.categories = ['TEST']

    def run(self):
        self.outputs['list'] = ['ab','ra','ca','dab','ra']
        self.outputs['tuple'] = ('ab','ra','ca','dab','ra')
        self.outputs['string'] = 'abracadabra'

