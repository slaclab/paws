import os
import string 
from collections import OrderedDict

class DictTree(object):
    """
    A tree as an ordered dictionary (root), 
    extended by embedding other objects 
    that are amenable to tree storage.
    Fetches items by a uri string that is a sequence 
    of dict keys, connected by '.'s.

    Child items (end nodes of the tree)
    can be anything.
    Parent items, in order to index their children,
    must be either lists, dicts, or objects implementing
    keys(), __getitem__(key) and __setitem__(key,value).
    """

    def __init__(self,data={}):
        super(DictTree,self).__init__()
        self._root = OrderedDict()
        if isinstance(data,dict):
            self._root = OrderedDict(data)
        self.bad_chars = string.punctuation 
        self.bad_chars = self.bad_chars.replace('_','')
        self.bad_chars = self.bad_chars.replace('-','')
        self.bad_chars = self.bad_chars.replace('.','')
        self.space_chars = [' ','\t','\n',os.linesep]
        self._all_uris = []

    def __getitem__(self,uri):
        return self.get_from_uri(uri)

    def __setitem__(self,uri,val):
        self.set_uri(uri,val)

    def root_keys(self):
        return self._root.keys()

    #def __len__(self):
    #    return self.n_items()
    #
    #def n_items(self,root_uri=''):
    #    """
    #    Get the total number of data items in the tree.
    #    Only nodes containing data (i.e. end nodes) are counted.
    #    Nodes referencing containers, for example, are not counted. 
    #    """
    #    if root_uri:
    #        itm = self.get_from_uri(root_uri)
    #        prefix = root_uri + '.'
    #    else:
    #        itm = self._root
    #        prefix = ''
    #    if isinstance(itm,list):
    #        return sum([self.n_items(prefix+str(i)) for i in range(len(itm))])
    #    elif isinstance(itm,dict):
    #        return sum([self.n_items(prefix+k) for k in itm.keys()])
    #    else:
    #        # BUG: lacks a solution for simultaneously serving 
    #        # non-dict non-list and non-parent items.
    #        # terminal node: return 1
    #        return 1 

    def delete_uri(self,uri=''):
        """
        Delete the given uri, i.e., 
        remove the corresponding key from the embedded dict.
        This should not be relied on to be fast.
        It has to go through all of the uris to remove children.
        """
        try:
            itm = self._root
            if '.' in uri:
                itm = self.get_from_uri(uri[:uri.rfind('.')])
            path = uri.split('.')
            k = path[-1]
            if k:
                # Note- parent items must implement __getitem__
                del itm[k]
                #itm.pop(k)
                for i,testuri in zip(range(len(self._all_uris))[::-1],self._all_uris[::-1]):
                    if uri in testuri:
                        self._all_uris.pop(i)
        except Exception as ex:
            msg = str('\n[{}] Encountered an error while trying to delete uri {}: \n'
            .format(__name__,uri))
            ex.message = msg + ex.message
            raise ex

    def set_uri(self,uri='',val=None):
        """
        Set the data at the given uri to provided value val.
        """
        try:
            itm = self._root
            if '.' in uri:
                parent_uri = uri[:uri.rfind('.')]
                #if parent_uri in self._all_uris:
                itm = self.get_from_uri(parent_uri)
                #else:
                #    itm = self.build_to_uri(parent_uri)
            k = uri.split('.')[-1]
            # TODO: Is there a more graceful way to handle lists?
            if k:
                if isinstance(itm,list):
                    itm[int(k)] = val
                else:
                    # Note- parent items must implement __setitem__
                    itm[k] = val
                if not uri in self._all_uris:
                    self._all_uris.append(uri)
        except Exception as ex:
            #import pdb; pdb.set_trace()
            msg = str('\n[{}] Encountered an error while trying to set uri {} to val {}: \n'
            .format(__name__,uri,val)) + ex.message
            raise KeyError(msg)

    def get_from_uri(self,uri=''):
        """
        Return the data stored at uri.
        Each data item in the lineage of the uri
        must implement __getitem__() with support for
        string-like keys, unless it is a list,
        in which case the key is cast as int(key)
        before using it as an index in the list.
        """
        try:
            path = uri.split('.')
            itm = self._root 
            #for k in path[:-1]:
            while any(path):
                k = path.pop(0)
                # TODO: Is there a more graceful way to handle lists?
                if isinstance(itm,list):
                    itm = itm[int(k)]
                else:
                    # Note- parent items must implement __getitem__ and keys()
                    if k in itm.keys():
                        itm = itm[k]
                    else:
                        # this could be a dict with a key containing a '.'
                        found = False
                        while not found:
                            k = k+'.'+path.pop(0)                        
                            if k in itm.keys():
                                itm = itm[k]
                                found = True 
                            elif k+'.' in itm.keys():
                                itm = itm[k+'.']
                                found = True           
            return itm
            #k = uri.split('.')[-1]
            #if k == '':
            #    # uri ended with a '.' 
            #    return itm 
            #elif k is not None:
            #    if isinstance(itm,list):
            #        return itm[int(k)]
            #    else:
            #        # Note- parent items must implement __getitem__
            #        return itm[k]
        except Exception as ex:
            #import pdb; pdb.set_trace()
            msg = str('[{}] Encountered an error while fetching uri {}: \n'
            .format(__name__,uri) + ex.message)
            raise KeyError(msg) 

    #def build_to_uri(self,uri=''):
    #    """ 
    #    If the tree does not contain the input uri,
    #    Fill the tree out with dicts
    #    until an empty dict exists at the given uri. 
    #    """
    #    try:
    #        itm = self._root 
    #        if '.' in uri:
    #            parent_uri = uri[:uri.rfind('.')]
    #            if parent_uri in self._all_uris:
    #                itm = self.get_from_uri(parent_uri)
    #            else:
    #                itm = self.build_to_uri(parent_uri)
    #        k = uri.split('.')[-1]
    #        if k == '':
    #            return itm 
    #        elif k is not None:
    #            # Note- parent items must implement __setitem__
    #            if not uri in self._all_uris:
    #                self._all_uris.append(uri)
    #            itm[k] = OrderedDict()
    #            return itm[k]
    #    except Exception as ex:
    #        msg = str('[{}] Encountered an error while trying to build uri {}: \n'
    #        .format(__name__,uri) + ex.message)
    #        raise KeyError(msg) 
        
    #def list_child_tags(self,parent_uri=''):
    #    if parent_uri:
    #        p_itm = self.get_from_uri(parent_uri)
    #    else:
    #        p_itm = self._root
    #    try:
    #        # TODO: Is there a more graceful way to handle lists?
    #        if isinstance(p_itm,list):
    #            return [str(i) for i in range(len(p_itm))]
    #        elif isinstance(p_itm,dict):
    #            return p_itm.keys()
    #        # BUG: lacks a solution for simultaneously serving 
    #        # non-dict non-list and non-parent items.
    #    except Exception as ex:
    #        msg = str('[{}] Encountered an error while trying to get child tags from parent uri {}: \n'
    #        .format(__name__,parent_uri) + ex.message)
    #        raise KeyError(msg) 

    #def list_uris(self,root_uri=''):
    #    if root_uri:
    #        itm = self.get_from_uri(root_uri)
    #        l = [root_uri]
    #        prefix = root_uri+'.'
    #    else:
    #        itm = self._root
    #        l = []
    #        prefix = ''
    #    # TODO: Is there a more graceful way to handle lists?
    #    if isinstance(itm,list):
    #        for i in range(len(itm)):
    #            l = l + self.list_uris(prefix+str(i))
    #    elif isinstance(itm,dict):
    #        for k in itm.keys():
    #            l = l + self.list_uris(prefix+k)
    #        # BUG: lacks a solution for simultaneously serving 
    #        # non-dict non-list and non-parent items.
    #    return l
            
    def is_uri_valid(self,uri):
        """
        Check for validity of a uri. 
        Uris may contain upper case letters, lower case letters, 
        numbers, dashes (-), and underscores (_). 
        Periods (.) are used as delimiters between tags in the uri.
        Any whitespace or any character in the string.punctuation library
        (other than -, _, or .) results in an invalid uri.
        """
        #if parent is None:
        #    parent = self.root_index()
        if (any(map(lambda s: s in uri,self.space_chars))
            or any(map(lambda s: s in uri,self.bad_chars))):
            return False 
        return True 

    def is_tag_valid(self,tag):
        """
        Check for validity of a tag.
        The conditions for a valid tag are the same as for a valid uri,
        except that a tag should not contain period (.) characters.
        """
        if '.' in tag:
            return False 
        else:
            return self.is_uri_valid(tag)

    def is_uri_unique(self,uri):
        """
        Check for uniqueness of a uri. 
        """
        return uri not in self._all_uris
        #if parent is None:
        #    parent = self.root_index()
        #if uri in self._all_uris:
        #    return False 
        #else:
        #    return True 

    def uri_error(self,uri):
        """Provide a human-readable error message for bad uris."""
        if not uri:
            err_msg = 'uri is blank.'
        elif any(map(lambda s: s in uri,self.space_chars)):
            err_msg = 'uri contains whitespace.'
        elif any(map(lambda s: s in uri,self.bad_chars)):
            err_msg = 'uri contains special characters.'
        else:
            err_msg = 'Unforeseen uri error.'
        return str('uri error for {}: \n{}\n'.format(uri,err_msg))

    def tag_error(self,tag):
        """Provide a human-readable error message for bad tags."""
        if '.' in tag:
            return 'tag error for {}: \ntag contains a period (.)\n'.format(tag)
        else:
            return self.uri_error(tag)

    def contains_uri(self,uri):
        """Returns whether or not input uri points to an item in this tree."""
        return uri in self._all_uris
        #if not uri:
        #    return False
        #path = uri.split('.')
        #p_idx = QtCore.QModelIndex()
        #for itemuri in path:
        #    try:
        #        row = self.list_child_tags(p_idx).index(itemuri)
        #    except ValueError as ex:
        #        return False
        #    idx = self.index(row,0,p_idx)
        #    p_idx = idx
        #return True

    def make_unique_uri(self,prefix):
        """
        Generate the next unique uri from prefix by appending '_x' to it, 
        where x is a minimal nonnegative integer.
        """
        suffix = 0
        gooduri = False
        urilist = self._all_uris
        while not gooduri:
            testuri = prefix+'_{}'.format(suffix)
            if not testuri in urilist: 
                gooduri = True
            else:
                suffix += 1
        return testuri 

    def print_tree(self,root_uri='',rowprefix=''):
        """
        Print the content of the tree rooted at root_uri,
        with each row of the string preceded by rowprefix.
        """
        if root_uri:
            itm = self.get_from_uri(root_uri)
        else:
            itm = self._root
        if isinstance(itm,dict):
            tree_string = '\n'
            for k,x in itm.items():
                x_tree = self.print_tree(root_uri+'.'+k,rowprefix+'\t')
                tree_string = tree_string+rowprefix+'{}: {}\n'.format(k,x_tree)
        elif isinstance(itm,list):
            tree_string = '\n'
            for i,x in zip(range(len(itm)),itm):
                x_tree = self.print_tree(root_uri+'.'+str(i),rowprefix+'\t')
                tree_string = tree_string+rowprefix+'{}: {}\n'.format(i,x_tree)
        else:
            return '{}'.format(itm)
        return tree_string

    def print_tree(self,root_uri='',rowprefix=''):
        """
        Print the content of the tree rooted at root_uri,
        with each row of the string preceded by rowprefix.
        """
        if root_uri:
            itm = self.get_from_uri(root_uri)
        else:
            itm = self._root
        if isinstance(itm,dict):
            tree_string = '\n'
            for k,x in itm.items():
                x_tree = self.print_tree(root_uri+'.'+k,rowprefix+'\t')
                tree_string = tree_string+rowprefix+'{}: {}\n'.format(k,x_tree)
        elif isinstance(itm,list):
            tree_string = '\n'
            for i,x in zip(range(len(itm)),itm):
                x_tree = self.print_tree(root_uri+'.'+str(i),rowprefix+'\t')
                tree_string = tree_string+rowprefix+'{}: {}\n'.format(i,x_tree)
        else:
            return '{}'.format(itm)
        return tree_string

#        if parent.isValid():
#            itm = self.get_item(parent)
#            tree_string = tree_string+rowprefix+str(itm.data)+'\n'
#            for j in range(itm.n_children()):
#                tree_string = tree_string + self.print_tree(rowprefix+'\t',self.index(j,0,parent))
#                l.append(root_uri+'.'+str(i))
#                l = l + self.list_uris(root_uri+'.'+str(i))
#
            
