from PySide import QtCore

class ImageList(QtCore.QAbstractListModel):
    """
    Class for managing the list of open images for slacx.
    Should be able to add images to the list
    and remove selected images from the list.
    """

    def __init__(self,file_list):
        self.img_dict = {}
        if file_list:
            for f in file_list:
                self.add_to_dict(f)
    
    # subclass must implement rowCount()
    def rowCount(self):
        return len(self.img_dict)
 
    # subclass must implement data()
    def data(self):
        return self.img_dict.keys()
    
    # add a file to the dict by filename
    def add_to_dict(self,new_img_file):
        img_tag = new_img_file.split('/')[-1]
        print('adding image file: {}, with tag {}'.format(new_img_file,img_tag))
        
    # remove a file from the dict by img_tag
    def rm_from_dict(self,img_tag):
        if img_tag in self.img_dict:
            del self.img_dict[img_tag]



