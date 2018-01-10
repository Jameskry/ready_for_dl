%matplotlib inline
import SimpleITK
import ntpath 
import numpy as np
import pandas 
import os
import glob
import scipy.ndimage
import cv2

import config
from helpers import get_cube_from_img, save_cube_img
from image_helpers import save_patient_images, normalize, load_patient_images, resample_images

def init():
    check_or_create_dirs.check_or_create_dirs()


# get positive annotations as pandas dataframe
def get_annot_dataframe():
    csv_file = config.LUNA16_META_DIR + "/" + "annotations.csv"
    annots_df = pandas.read_csv(csv_file)
    return annots_df

# get positive and negative annotations as pandas dataframe
def get_candidates_dataframe():
    csv_file = config.LUNA16_META_DIR + "/" + "candidates.csv"
    annots_df = pandas.read_csv(csv_file)
    return annots_df


# save positive labels per patient.
# used while extracted positive cubes/3d patches from images
def save_positive_labels(patient_annots, origin_cordinates): 
  annot_index = 0 
  pos_annos = []
  for index, row in patient_annots.iterrows():
      
      center_float = np.array([row["coordX"], row["coordY"], row["coordZ"]])
      center_float_rescaled = (center_float - origin_cordinates) / TARGET_VOXEL_MM

      pos_annos.append([annot_index, 
                        round(center_float_rescaled[0], 4), 
                        round(center_float_rescaled[1], 4),
                        round(center_float_rescaled[2], 4), 
                        round(row["diameter_mm"], 4), 1])
      annot_index = annot_index + 1
      
  df_annos = pandas.DataFrame(pos_annos, columns=["annot_index", "x", "y", "z", "diameter", "malignancy"])        
  df_annos.to_csv(config.LUNA16_TRAIN_LABELS_DIR +"/" + patient_id + "_annos_pos.csv", index=False)

# save positive labels per patient.
# used while extracted positive cubes/3d patches from images
def save_negative_labels(candidate_annots, origin_cordinates): 
  neg_index = 0 
  negative_annos = []
  for index, row in candidate_annots.iterrows():
      
      center_float = np.array([row["coordX"], row["coordY"], row["coordZ"]])
      center_float_rescaled = (center_float - origin_cordinates) / TARGET_VOXEL_MM

      negative_annos.append([neg_index, 
                        round(center_float_rescaled[0], 4), 
                        round(center_float_rescaled[1], 4),
                        round(center_float_rescaled[2], 4), 
                        0, 0])
      neg_index = neg_index + 1
      
  df_neg_annos = pandas.DataFrame(negative_annos, columns=["annot_index", "x", "y", "z", "diameter", "malignancy"])        
  df_neg_annos.to_csv(config.LUNA16_TRAIN_LABELS_DIR +"/" + patient_id + "_annos_neg.csv", index=False)


# The dataset from (luna16.grand-challenge.org/data/) contains multiple subsets [0-9]
# Pass subset index to this method. Feel free to run this in parallel for better efficiency
#
def read_subset(index):
  subset_dir = config.LUNA16_RAW_IMG_DIR + "/" +  "subset" + str(index) + "/"
  annot_df = get_annot_dataframe()
  candidate_df = get_candidates_dataframe()

  # choose mhd images then retrieve positive annotations (for patient if any) from annotaions.csv
  for image_path in glob.glob(subset_dir + "*.mhd"):
      
    # sources files have  patient.mhd format  
    patient_id = ntpath.basename(image_path).replace(".mhd", "")
    patient_annots = annot_df[annot_df["seriesuid"] == (str(patient_id))] 
    candidate_annots =  candidate_df[candidate_df["seriesuid"] == (str(patient_id)) && candidate_df["label"] == 0 ] 

    if patient_annots.empty OR candidate_annots.empty:
        #print('No annotations for:', patient_id)
        continue

    img_array, spacing, origin = read_mhd(image_path = image_path)

    # change the order of dims in spacing. This is something to with pixel spacing
    # in mhd files. Its swaps x,y,z with z, x, y
    swap_dim_spacing =np.array([spacing[2], spacing[0], spacing[1]]) 
    img_array = resample_images(images = img_array, spacing = swap_dim_spacing) 
    
    # save images if not done already
    save_patient_images(target_path= config.LUNA16_TRAIN_IMAGES_POS + '/' + patient_id + '/', 
                        patient_id=patient_id, images = img_array)
    
    # 
    if !patient_annots.empty:
      save_positive_labels(patient_annots = patient_annots, origin_cordinates = origin)
    
    if !candidate_annots.empty:
      save_negative_labels(candidate_annots = candidate_annots, origin_cordinates = origin)
        
           



for raw_path in glob.glob(config.LUNA16_RAW_DIR + '/'+ '*105756658031515062000744821260*.mhd'):
    patient_id = ntpath.basename(raw_path).replace(".mhd", "")
    extract_dir = config.LUNA16_IMAGE_DIR + "/" +  patient_id + "/"
    if not os.path.exists(extract_dir):
        os.mkdir(extract_dir)
        
    patient_id = ntpath.basename(raw_path).replace(".mhd", "")
    itk_img = SimpleITK.ReadImage(raw_path)
    img_array = SimpleITK.GetArrayFromImage(itk_img)
    origin = numpy.array(itk_img.GetOrigin())      # x,y,z  Origin in world coordinates (mm)
    print("Origin (x,y,z): ", origin)
    spacing = numpy.array(itk_img.GetSpacing())    # spacing of voxels in world coor. (mm)
    print("Spacing (x,y,z): ", spacing)
    rescale = spacing / TARGET_VOXEL_MM
    print("Rescale: ", rescale)
    img_array = resample_image(img_array, [spacing[2], spacing[0], spacing[1]])

    
for i in range(img_array.shape[0]):
    img = img_array[i]
    img = normalize(img)
    cv2.imwrite(extract_dir + "img_" + str(i).rjust(4, '0') + "_i.png", img * 255)
    


csv_file = config.LUNA16_META_DIR + "/" + "candidates.csv"
candidates_df = pandas.read_csv(csv_file)

for patient_image_dirs in  glob.glob(config.LUNA16_IMAGE_DIR + "/*") :
    patient_id = ntpath.basename(patient_image_dirs)
    # print(patient_id)
    patient_annots = annots[annots["seriesuid"] == (str(patient_id))] 
    images = load_images(patient_id)
    l_skip_count = 0
    l_susp_count = 0 
    l_annotation_count = 0

    for index, row in patient_annots.iterrows():
      l_annotation_count = l_annotation_count + 1
      x = int(row["coordX"] )
      y = int(row["coordY"] )
      z = int(row["coordZ"] )
      
      center_float = numpy.array([row["coordX"], row["coordY"], row["coordZ"]])
      # center_int = numpy.rint((center_float-origin) / spacing)
      center_float_rescaled = (center_float - origin) / TARGET_VOXEL_MM
       
      anno_index = index
      cube_img = helpers.get_cube_from_img(images, center_float_rescaled[0], center_float_rescaled[1], center_float_rescaled[2], 48)

      if cube_img.sum() < 5:
        # print(" ***** Skipping ", x, y, z)
        l_skip_count += 1
        continue

      if cube_img.mean() < 10:
        l_susp_count += 1
        # print(" ***** Suspicious ",x, y, z)
      helpers.save_cube_img(config.LUNA16_IMAGE_PATCH_DIR + "/" + patient_id + "_" + str(anno_index) + "_0_"  + ".png", cube_img, 6, 8)

    print('skipped cubes:', l_skip_count)
    print('suspicious cubes:', l_susp_count)
    print('l_annotation_count', l_annotation_count)
    


for raw_path in glob.glob(config.LUNA16_RAW_DIR + '/'+ '*105756658031515062000744821260*.mhd'):
    patient_id = ntpath.basename(raw_path).replace(".mhd", "")
    extract_dir = config.LUNA16_IMAGE_DIR + "/" +  patient_id + "/"
    if not os.path.exists(extract_dir):
        os.mkdir(extract_dir)
        
    patient_id = ntpath.basename(raw_path).replace(".mhd", "")
    itk_img = SimpleITK.ReadImage(raw_path)
    img_array = SimpleITK.GetArrayFromImage(itk_img)
    origin = numpy.array(itk_img.GetOrigin())      # x,y,z  Origin in world coordinates (mm)
    print("Origin (x,y,z): ", origin)
    spacing = numpy.array(itk_img.GetSpacing())    # spacing of voxels in world coor. (mm)
    print("Spacing (x,y,z): ", spacing)
    rescale = spacing / TARGET_VOXEL_MM
    print("Rescale: ", rescale)
    img_array = resample_image(img_array, [spacing[2], spacing[0], spacing[1]])

    
for i in range(img_array.shape[0]):
    img = img_array[i]
    img = normalize(img)
    cv2.imwrite(extract_dir + "img_" + str(i).rjust(4, '0') + "_i.png", img * 255)
    


csv_file = config.LUNA16_META_DIR + "/" + "candidates.csv"
candidates_df = pandas.read_csv(csv_file)

for patient_image_dirs in  glob.glob(config.LUNA16_IMAGE_DIR + "/*") :
    patient_id = ntpath.basename(patient_image_dirs)
    # print(patient_id)
    patient_annots = annots[annots["seriesuid"] == (str(patient_id))] 
    images = load_images(patient_id)
    l_skip_count = 0
    l_susp_count = 0 
    l_annotation_count = 0

    for index, row in patient_annots.iterrows():
      l_annotation_count = l_annotation_count + 1
      x = int(row["coordX"] )
      y = int(row["coordY"] )
      z = int(row["coordZ"] )
      
      center_float = numpy.array([row["coordX"], row["coordY"], row["coordZ"]])
      # center_int = numpy.rint((center_float-origin) / spacing)
      center_float_rescaled = (center_float - origin) / TARGET_VOXEL_MM
       
      anno_index = index
      cube_img = helpers.get_cube_from_img(images, center_float_rescaled[0], center_float_rescaled[1], center_float_rescaled[2], 48)

      if cube_img.sum() < 5:
        # print(" ***** Skipping ", x, y, z)
        l_skip_count += 1
        continue

      if cube_img.mean() < 10:
        l_susp_count += 1
        # print(" ***** Suspicious ",x, y, z)
      helpers.save_cube_img(config.LUNA16_IMAGE_PATCH_DIR + "/" + patient_id + "_" + str(anno_index) + "_0_"  + ".png", cube_img, 6, 8)

    print('skipped cubes:', l_skip_count)
    print('suspicious cubes:', l_susp_count)
    print('l_annotation_count', l_annotation_count)
    

 
 