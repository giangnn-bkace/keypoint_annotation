##############################
#  ONLY 1 CHIM IN A IMAGE    # 
##############################

import os
import argparse
import json
import xml.etree.ElementTree as ET
import datetime
import numpy as np
from PIL import Image

KEY_POINT = ["nose", "left_eye", "right_eye", "left_ear", "right_ear", "left_shoulder", 
			"right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist",
			"left_hip", "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle"]

SKELETON = [[16, 14], [14, 12], [17, 15], [15, 13], [12, 13], [6, 12], [7, 13], [6, 7], [6, 8], 
			[7, 9], [8, 10], [9, 11], [2, 3], [1, 2], [1, 3], [2, 4], [3, 5], [4, 6], [5, 7]]				

now = datetime.datetime.now()
parse = argparse.ArgumentParser()
parse.add_argument("--data_path", required=True, help="path to data folder")
args = parse.parse_args()

def createImageObject(file_name, width, height, id, license=1, coco_url="", date_captured="", flickr_url=""):
	image_obj = {}
	image_obj['license'] = license
	image_obj['file_name'] = file_name
	image_obj['coco_url'] = coco_url
	image_obj['height'] = height
	image_obj['width'] = width
	image_obj['date_captured'] = date_captured
	image_obj['flickr_url'] = flickr_url
	image_obj['id'] = id
	return image_obj

def createAnnotationObject(image_id, id, segmentation, bbox, num_keypoints, keypoints, area=0, iscrowd=0, category_id=1):
	annotation_obj = {}
	annotation_obj['segmentation'] = segmentation
	annotation_obj['num_keypoints'] = num_keypoints
	annotation_obj['area'] = area
	annotation_obj['iscrowd'] = iscrowd
	annotation_obj['keypoints'] = keypoints
	annotation_obj['image_id'] = image_id
	annotation_obj['bbox'] = bbox
	annotation_obj['category_id'] = category_id
	annotation_obj['id'] = id
	return annotation_obj

def createSegmentationObject(points):
	seg = []
	minx = points[0][0]
	maxx = points[0][0]
	miny = points[0][1]
	maxy = points[0][1]
	for point in points:
		seg.append(round(point[0], 2))
		seg.append(round(point[1], 2))
		if minx > point[0]:
			minx = point[0]
		if maxx < point[0]:
			maxx = point[0]
		if miny > point[1]:
			miny = point[1]
		if maxy < point[1]:
			maxy = point[1]
	x = round(minx, 2)
	y = round(miny, 2)
	width = round(maxx, 2) - round(minx, 2)
	height = round(maxy, 2) - round(miny, 2)
	bbox = [x, y, width, height]
	return seg, bbox

	
	
anno = {}

# create info
anno['info'] = {}
anno['info']['description'] = "test convert"
anno['info']['url'] = ""
anno['info']['version'] = "0.1"
anno['info']['year'] = "2017"
anno['info']['contributor'] = "COCO"
anno['info']['date_created'] = now.strftime("%Y/%m/%d %H:%M:%S")

# create licenses
anno['licenses'] = []
license_0 = {}
license_0['url'] = "none"
license_0['id'] = 1
license_0['name'] = "noname"
license_1 = {}
license_1['url'] = "none"
license_1['id'] = 2
license_1['name'] = "noname"
anno['licenses'].append(license_0)
anno['licenses'].append(license_1)

# create categories
anno['categories'] = []
category_0 = {}
category_0['supercategory'] = "person"
category_0['id'] = 1
category_0['name'] = "person"
category_0['keypoints'] = KEY_POINT
category_0['skeleton'] = SKELETON
anno['categories'].append(category_0)

anno['images'] = []
anno['annotations'] = []

for i, file in enumerate(os.listdir(os.path.join(args.data_path, 'segmentation'))):
	name = os.path.splitext(file)[0]
	print(name)
	
	# create image objects
	img_path = os.path.join(args.data_path, 'images', name+'.jpg')
	img = Image.open(img_path)
	(img_width, img_height) = img.size
	img_id = int(str.split(name, "_")[1])
	anno['images'].append(createImageObject(file_name=name+'.jpg', width=img_width, height=img_height, id=img_id))
	
	# create keypoints objects
	an_id = i
	xml_tree = ET.parse(os.path.join(args.data_path, "info", name+"_0.xml"))
	xml_root = xml_tree.getroot()
	an_nkp = 0
	an_kp = [0]*(len(KEY_POINT)*3)
	for keypoint in xml_root.iter("keypoint"):
		an_nkp = an_nkp + 1
		pos = KEY_POINT.index(keypoint.get('name'))
		an_kp[pos*3] = int(float(keypoint.get('x')))
		an_kp[pos*3+1] = int(float(keypoint.get('y')))
		an_kp[pos*3+2] = 2
			
	json_file = json.load(open(os.path.join(args.data_path, "segmentation", name+".json")))
	an_seg = []
	an_seg_0, an_bb = createSegmentationObject(json_file['shapes'][0]['points'])
	an_seg.append(an_seg_0)
	anno['annotations'].append(createAnnotationObject(image_id=img_id, id=an_id, segmentation=an_seg, bbox=an_bb, num_keypoints=an_nkp, keypoints=an_kp))
	print(img_id)
	
with open(os.path.join(args.data_path, "annotation.json"), 'w') as anno_file:
	json.dump(anno, anno_file)