import os
import itwincapturemodeler
def transform_it(value):
    transformer = itwincapturemodeler.SRSTransformation(itwincapturemodeler.SRS("EPSG:4978"), itwincapturemodeler.SRS("WGS84"))
    coord = transformer.transform(value)
    return coord.x, coord.y, coord.z

projectName = 'labtest1'

ccmasterkernel = itwincapturemodeler

project = ccmasterkernel.Project()

project.setName(projectName)

project.setProjectFilePath(os.path.join('C:/test', projectName))

err = project.writeToFile()
if not err.isNone():
    print(err.message)

block = ccmasterkernel.Block(project)

project.addBlock(block)

block.setName('block #1')

photogroups = block.getPhotogroups()

path = r'C:\MapMaker-SapmleDatasets\PhotogrammetryDatasets\Outdoors\Images_geotagged\EO-AnafiThermal\79Images'

files = os.listdir(path)

for file in files:
    file = os.path.join(
        r'C:\MapMaker-SapmleDatasets\PhotogrammetryDatasets\Outdoors\Images_geotagged\EO-AnafiThermal\79Images', file)

for file in files:
    file = os.path.join(path, file)
    # add photo, create a new photogroup if needed
    lastPhoto = photogroups.addPhotoInAutoMode(file)
    if lastPhoto is None:
        continue

    # upgrade block positioningLevel if a photo with position is found (GPS tag)
    # update exif data exists flag if photo with position is found
    if not lastPhoto.pose.center is None:
        block.setPositioningLevel(ccmasterkernel.PositioningLevel.PositioningLevel_georeferenced)

photogroups = project.getBlock(0).getPhotogroups()

for i_pg in range(0, photogroups.getNumPhotogroups()):
    print('photogroup #%s:' % (i_pg + 1))
    if not photogroups.getPhotogroup(i_pg).hasValidFocalLengthData():
        print('Warning: invalid photogroup')
    for photo_i in photogroups.getPhotogroup(i_pg).getPhotoArray():
        print('image: %s' % photo_i.imageFilePath)
    print('')

blockAT = ccmasterkernel.Block(project)
project.addBlock(blockAT)
blockAT.setBlockTemplate(ccmasterkernel.BlockTemplate.Template_adjusted, block)
at_settings = blockAT.getAT().getSettings()
at_settings.keyPointsDensity = ccmasterkernel.KeyPointsDensity.KeyPointsDensity_normal
at_settings.splatsPreprocessing = ccmasterkernel.SplatsPreprocessing.SplatsPreprocessing_none
at_settings.adjustmentConstraints = ccmasterkernel.AdjustmentAndPositioning.Positioning_PositionMetadata

atSubmitError = blockAT.getAT().submitProcessing()

print(atSubmitError.message)
