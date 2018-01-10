#
# set these for your system. 
BASE_DIR = '/home/apple/lung'
LUNA16_DATA_DIR = BASE_DIR + '/datasets/luna16'

# Directory for annotations.csv, candidates.csv 
LUNA16_META_DIR = LUNA16_DATA_DIR 

# Directory for raw images
LUNA16_RAW_IMG_DIR = LUNA16_DATA_DIR 
#

LUNA16_TRAIN_DIR = BASE_DIR + '/datasets/train' 
LUNA16_TRAIN_PATCHES_DIR = LUNA16_TRAIN_DIR + '/patches'
LUNA16_TRAIN_IMAGES_DIR = LUNA16_TRAIN_DIR + '/images'
LUNA16_TRAIN_LABELS_DIR  = LUNA16_TRAIN_DIR + '/labels'

LUNA16_TRAIN_CUBES_POS = LUNA16_TRAIN_DIR + '/patches/positive'
LUNA16_TRAIN_IMAGES_POS = LUNA16_TRAIN_DIR + '/images/positive'

LUNA16_TRAIN_CUBES_NEG = LUNA16_TRAIN_DIR + '/patches/negative'
LUNA16_TRAIN_IMAGES_NEG = LUNA16_TRAIN_DIR + '/images/negative'

CUBE_SIZE = 64

TARGET_VOXEL_MM = [1,1,1]


def check_or_create_dirs():
    if not os.path.exists(config.LUNA16_TRAIN_DIR):
        os.mkdir(config.LUNA16_TRAIN_DIR) 
    
    if not os.path.exists(config.LUNA16_TRAIN_PATCHES_DIR):
        os.mkdir(config.LUNA16_TRAIN_PATCHES_DIR)    
    
    if not os.path.exists(config.LUNA16_TRAIN_IMAGES_DIR):
        os.mkdir(config.LUNA16_TRAIN_IMAGES_DIR)   
        
    if not os.path.exists(config.LUNA16_TRAIN_CUBES_POS):
        os.mkdir(config.LUNA16_TRAIN_POSITIVE_DIR)     
    
    if not os.path.exists(config.LUNA16_TRAIN_IMAGES_POS):
        os.mkdir(config.LUNA16_TRAIN_IMAGES_POS) 

    if not os.path.exists(config.LUNA16_TRAIN_CUBES_NEG):
        os.mkdir(config.LUNA16_TRAIN_CUBES_NEG)     
    
    if not os.path.exists(config.LUNA16_TRAIN_IMAGES_NEG):
        os.mkdir(config.LUNA16_TRAIN_IMAGES_NEG) 
    
    if not os.path.exists(config.LUNA16_TRAIN_LABELS_DIR):
        os.mkdir(config.LUNA16_TRAIN_LABELS_DIR) 