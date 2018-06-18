import os

def stack_contains(itm,stk):
    for lst in stk:
        if itm in lst:
            return True
    return False

def stack_size(stk):
    sz = 0
    for lst in stk:
        sz += len(lst)
    return sz

def print_stack(stk):
    stktxt = ''
    opt_newline = os.linesep
    n_layers = len(stk)
    for i,lst in enumerate(stk):
        if i == n_layers-1:
            opt_newline = ''
        stktxt += ('{}'+opt_newline).format(lst)
    return stktxt



