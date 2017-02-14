import numpy as np
import datetime
import time

import pytz
import tzlocal

from ..operation import Operation
from .. import optools

class WindowZip(Operation):
    """
    From input iterables of x and y, 
    produce an n-by-2 array 
    where x is bounded by the specified limits 
    """

    def __init__(self):
        input_names = ['x','y','x_min','x_max']
        output_names = ['x_window','y_window','x_y_window']
        super(WindowZip,self).__init__(input_names,output_names)        
        self.input_src['x'] = optools.wf_input
        self.input_src['y'] = optools.wf_input
        self.input_src['x_min'] = optools.text_input
        self.input_src['x_max'] = optools.text_input
        self.input_type['x'] = optools.ref_type
        self.input_type['y'] = optools.ref_type
        self.input_type['x_min'] = optools.float_type
        self.input_type['x_max'] = optools.float_type
        self.inputs['x_min'] = 0.02 
        self.inputs['x_max'] = 0.6 
        self.input_doc['x'] = 'list (or iterable) of x values'
        self.input_doc['y'] = 'list (or iterable) of y values'
        self.input_doc['x_min'] = 'inclusive minimum x value of output'
        self.input_doc['x_max'] = 'inclusive maximum x value of output'
        self.output_doc['x_window'] = 'n-by-1 array of x_min <= x <= x_max'
        self.output_doc['y_window'] = 'n-by-1 array of y for x_min <= x <= x_max'
        self.output_doc['x_y_window'] = 'n-by-2 array with x, y pairs for x_min <= x <= x_max'

    def run(self):
        xvals = self.inputs['x']
        yvals = self.inputs['y']
        x_min = self.inputs['x_min']
        x_max = self.inputs['x_max']
        #try:
        idx_good = ((xvals >= x_min) & (xvals <= x_max))
        x_y_window = np.zeros((idx_good.sum(),2))
        #except Exception as ex:
        #    import pdb; pdb.set_trace()
        x_y_window[:,0] = xvals[idx_good]
        x_y_window[:,1] = yvals[idx_good]
        self.outputs['x_window'] = x_y_window[:,0]
        self.outputs['y_window'] = x_y_window[:,1]
        self.outputs['x_y_window'] = x_y_window

class TimeTempFromHeader(Operation):
    """
    Get time and temperature from a detector output header file.
    Return string time, float time (utc in seconds), and float temperature.
    Time is assumed to be in the format Day Mon dd hh:mm:ss yyyy.
    """
    def __init__(self):
        input_names = ['header_dict','time_key','temp_key']
        output_names = ['time_str','time','temp']
        super(TimeTempFromHeader,self).__init__(input_names,output_names)        
        self.input_src['header_dict'] = optools.wf_input
        self.input_src['time_key'] = optools.text_input
        self.input_src['temp_key'] = optools.text_input
        self.input_type['header_dict'] = optools.ref_type
        self.input_type['time_key'] = optools.str_type
        self.input_type['temp_key'] = optools.str_type
        self.inputs['time_key'] = 'time'
        self.inputs['temp_key'] = 'TEMP'
        self.input_doc['header_dict'] = 'workflow uri of dict produced from detector output header file.'
        self.input_doc['time_key'] = 'key in header_dict that refers to the time' 
        self.input_doc['temp_key'] = 'key in header_dict that refers to the temperature' 
        self.output_doc['time_str'] = 'string representation of the time'
        self.output_doc['time'] = 'UTC time in seconds'
        self.output_doc['temp'] = 'Temperature'
        self.categories = ['PACKAGING']

    def run(self):
        d = self.inputs['header_dict']
        time_str = str(d[self.inputs['time_key']])
        temp = float(d[self.inputs['temp_key']])
        # process the UTC time in seconds assuming %a %b %d %H:%M:%S %Y format
        # set local time zone for utc-awareness 
        tz = tzlocal.get_localzone()
        # use strptime to create a naive datetime object
        dt = datetime.datetime.strptime(time_str.strip(),"%a %b %d %H:%M:%S %Y")
        # add in timezone information to make a utc-aware datetime object
        dt_aware = datetime.datetime(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second,dt.microsecond,tz)
        # interpret the time in UTC milliseconds
        t_utc = time.mktime(dt_aware.timetuple())
        self.outputs['time_str'] = time_str
        self.outputs['time'] = float(t_utc)
        self.outputs['temp'] = temp

class XYDataFromBatch(Operation):
    """
    Given a batch output and appropriate keys, 
    use the uris to harvest x and y data from the batch.
    """

    def __init__(self):
        input_names = ['batch_output','x_uri','y_uri','x_shift_flag']
        output_names = ['x','y','x_y','x_y_sorted']
        super(XYDataFromBatch,self).__init__(input_names,output_names)        
        self.input_doc['batch_output'] = 'list of dicts produced by a batch execution.'
        self.input_doc['x_uri'] = 'uri of data for x. Must be in batch.saved_items().'
        self.input_doc['y_uri'] = 'uri of data for y. Must be in batch.saved_items().'
        self.input_doc['x_shift_flag'] = 'if True, shift x data so that its minimum value is zero.' 
        self.input_src['batch_output'] = optools.wf_input
        self.input_src['x_uri'] = optools.wf_input
        self.input_src['y_uri'] = optools.wf_input
        self.input_src['x_shift_flag'] = optools.text_input
        self.input_type['batch_output'] = optools.ref_type
        self.input_type['x_uri'] = optools.path_type
        self.input_type['y_uri'] = optools.path_type
        self.input_type['x_shift_flag'] = optools.bool_type
        self.inputs['x_shift_flag'] = False
        self.output_doc['x'] = 'array of the x values in batch output order.'
        self.output_doc['y'] = 'array of the y values in batch output order.'
        self.output_doc['x_y'] = 'n-by-2 array of x and y values in batch output order.'
        self.output_doc['x_y_sorted'] = 'n-by-2 array of x and y values, sorted for increasing x.'

    def run(self):
        b_out = self.inputs['batch_output']
        x_uri = self.inputs['x_uri']
        y_uri = self.inputs['y_uri']
        x_all = np.array([optools.get_uri_from_dict(x_uri,d) for d in b_out if optools.dict_contains_uri(x_uri,d)],dtype=float)
        y_all = np.array([optools.get_uri_from_dict(y_uri,d) for d in b_out if optools.dict_contains_uri(y_uri,d)],dtype=float)
        if any(x_all):
            xmin = np.min(x_all)
        else:
            xmin = 0
        if self.inputs['x_shift_flag']:
            x_all = x_all - xmin
            #xmin = 0 
        self.outputs['x'] = x_all 
        self.outputs['y'] = y_all 
        self.outputs['x_y'] = np.array(zip(x_all,y_all))
        #self.outputs['x_y_sorted'] = np.sort(np.array(zip(x_all,y_all)),0)
        x_sort = np.sort(x_all)
        y_xsort = np.array([y_all[i] for i in np.argsort(x_all)])
        self.outputs['x_y_sorted'] = np.array(zip(x_sort,y_xsort))

class Window_q_I_2(Operation):
    """
    From input iterables of *q_list_in* and *I_list_in*,
    produce two 1d vectors
    where q is greater than *q_min* and less than *q_min*
    """

    def __init__(self):
        input_names = ['q_list_in','I_list_in','q_min','q_max']
        output_names = ['q_list_out','I_list_out']
        super(Window_q_I_2,self).__init__(input_names,output_names)
        # docstrings
        self.input_doc['q_list_in'] = '1d iterable listing q values'
        self.input_doc['I_list_in'] = '1d iterable listing I values'
        self.input_doc['q_min'] = 'lowest value of q of interest'
        self.input_doc['q_max'] = 'highest value of q of interest'
        self.output_doc['q_list_out'] = '1d iterable listing q values where q is between *q_min* and *q_max*'
        self.output_doc['I_list_out'] = '1d iterable listing I values where q is between *q_min* and *q_max*'
        # source & type
        self.input_src['q_list_in'] = optools.wf_input
        self.input_src['I_list_in'] = optools.wf_input
        self.input_src['q_min'] = optools.text_input
        self.input_src['q_max'] = optools.text_input
        self.input_type['q_min'] = optools.float_type
        self.input_type['q_max'] = optools.float_type
        self.inputs['q_min'] = 0.02
        self.inputs['q_max'] = 0.6
        self.categories = ['PACKAGING']

    def run(self):
        qvals = self.inputs['q_list_in']
        ivals = self.inputs['I_list_in']
        q_min = self.inputs['q_min']
        q_max = self.inputs['q_max']
        if (q_min >= q_max):
            raise ValueError("*q_max* must be greater than *q_min*.")
        good_qvals = ((qvals > q_min) & (qvals < q_max))
        self.outputs['q_list_out'] = qvals[good_qvals]
        self.outputs['I_list_out'] = ivals[good_qvals]


