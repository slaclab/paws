from pypif import pif
from pypif.obj import *
from citrination_client import CitrinationClient

def upload_to_citrine(Qlist, IntAve, Qlist_texture, texture, metal_names, newRow1, newRow2, newRow3, newRow4):
    chemical_system = ChemicalSystem()
    chemical_system.composition = [Composition(element=metal_names[0],ideal_atomic_percent=newRow1[0]),
                                   Composition(element=metal_names[1],ideal_atomic_percent=newRow1[1]),
                                   Composition(element=metal_names[2],ideal_atomic_percent=newRow1[2])]

    chemical_system.preparation = [ProcessStep(name = 'sputtering')]

    chemical_system.source = Source(producer='Hattrick-Simplers Group (University of South Carolina)')
    IntAve = IntAve.astype(float)
    IntAve = list(IntAve[7:950])
    Qlist = list(Qlist[7:950])

    Qlist_texture = Qlist_texture[66:645]
    texture = texture[66:645]

    plt.plot(Qlist, IntAve)

    # chemical_system.properties = Property(name='XRD Intensity', scalars=[1, 2, 3, 4],
    #                                       conditions=[Value(name='Q', scalars=[1, 2, 3, 4]),
    #                                                   Value(name='Temperature', scalars='25', units='$^\\circ$C')],
    #                                       method=Method(instruments=(Instrument(name='MARCCD'))))
    #
    chemical_system.properties = [Property(name = 'XRD Intensity', scalars = IntAve,
                                          conditions=[Value(name = 'Q', scalars = Qlist),
                                                      Value(name = 'Temperature', scalars = '25', units= '$^\\circ$C')],
                                          method = Method(instruments=(Instrument(name = 'MARCCD')))),
                                  Property(name='Texture Intensity', scalars=texture,
                                          conditions=[Value(name='Q', scalars=Qlist_texture),
                                                      Value(name='Temperature', scalars='25', units='$^\\circ$C')],
                                          method=Method(instruments=(Instrument(name='MARCCD'))))]

    chemical_system.uid = 'test_wafer'

    # print pif.dumps(chemical_system, indent=4)

    pif.dump(chemical_system, open('temp.json','w'))
    client = CitrinationClient(api_key = 'CXvOe54ijESoSqEtZtnG7Att', site = 'https://slac.citrination.com')
    response = client.create_data_set()

    client.upload_file('temp.json',data_set_id = response.json()['id'])  # id is the folder id

    # client.upload_file('temp.json',data_set_id = 3)  # id is the folder id, each folder for 1 sample

    ID = response.json()['id']
    print ID
    return [ID]

# to delete a record
# C:\Python27\Scripts>citrination create_dataset_version -k CXvOe54ijESoSqEtZtnG7Att -p slac -d ID

