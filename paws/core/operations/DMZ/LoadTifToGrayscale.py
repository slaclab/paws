class LoadTifToGrayscale(Operation):
    """
    Takes a filesystem path that points to a .tif,
    outputs image data and metadata from the file. 
    """

    def __init__(self):
        input_names = ['path']
        output_names = ['image','metadata']
        super(LoadTifToGrayscale,self).__init__(input_names,output_names) 
        # default behavior: load from filesystem
        self.input_doc['path'] = 'string representing the path to a .tif image'
        self.input_src['path'] = optools.fs_input
        self.input_type['path'] = optools.path_type
        self.output_doc['image'] = '2D array representing pixel values taken from the input file'
        self.output_doc['metadata'] = 'Dictionary containing all image metadata loaded from the input file'
        
    def run(self):
        img_url = self.inputs['path']
        #if self.istiff():
        try:
            # Open the tif, convert it to grayscale with .convert("L")
            pil_img = Image.open(img_url).convert("L")
            # Get the data out of this image.
            # Image.getdata() returns a sequence (have to reshape):
            self.outputs['image'] = np.array(pil_img.getdata()).reshape(pil_img.size).T
            self.outputs['metadata'] = pil_img.info
        except IOError as ex:
            print "[{}] PIL IOError for file {}. \nError message:".format(
            __name__,img_url,ex.message)
            self.set_outputs_to_none()
        except ValueError as ex:
            print "[{}] ValueError for file {}. \nError message:".format(
            __name__,img_url,ex.message)
            self.set_outputs_to_none()
        #else:
        #    print "[{}] File {} does not seem to be a .tif file".format(
        #    __name__,img_url)
        #    self.set_outputs_to_none()
    
    #tifftest = re.compile("^.tif*$")
    #def istiff(self):
    #    img_ext = os.path.splitext(self.inputs['path'])[1]
    #    if self.tifftest.match(img_ext):
    #        return True
    #    return False



