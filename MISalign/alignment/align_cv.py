"""
OpenCV2-based Computer Vision Alignment & Relation Module
"""

import cv2 as cv
import numpy as np

from MISalign.model.relation import Relation
from MISalign.model.mis_file import MisFile

class ImageManager():
    def __init__(self,image_names_paths:dict):
        self.image_dict={name:{"path":filepath} for name,filepath in image_names_paths.items()}
    
    def get_names(self)->list[str]:
        return list(self.image_dict.keys())
    def get_path(self,name:str)->str:
        return self.image_dict[name]["path"]
    def lookup_name(self,short_name:str)->str:
        name_matches=[name for name in self.image_dict.keys() if short_name in name]
        if len(name_matches)==1:
            return name_matches
        elif len(name_matches)==0:
            raise ValueError(f"short_name '{short_name}' matched no image names.")
        elif len(name_matches)>1:
            raise ValueError(f"short_name '{short_name}' matched {len(name_matches)} image names: {name_matches}")

class ORBManager():
    def __init__(self,
            ImageM:ImageManager,
            precompute_default=True,
            store_compute=True,
            default_ORB_parameters={"nfeatures":500,"edgeThreshold":5}):
        self.ImageM=ImageM
        self.default_ORB_parameters=default_ORB_parameters
        self.store_compute=store_compute
        if store_compute:
            self.computed=dict()
            if precompute_default:
                for image_name in ImageM.get_names():
                    self.computed[image_name]=dict()
                    self.computed[image_name][self.get_parameter_hashable(default_ORB_parameters)]=self.compute_orb(image_name,default_ORB_parameters)

    def compute_orb(self,image_name,ORB_parameters):
        img = cv.imread(self.ImageM.get_path(image_name), cv.IMREAD_GRAYSCALE)
        orb = cv.ORB_create(**ORB_parameters)
        kp, des = orb.detectAndCompute(img,None)
        return {"kp":kp,"des":des}
    def get_parameter_hashable(self,ORB_parameters:dict)->tuple:
        return tuple((k,ORB_parameters[k]) for k in sorted(ORB_parameters))
    def get_orb(self,image_name,ORB_parameters=None):
        if ORB_parameters is None:
            ORB_parameters=self.default_ORB_parameters
        ORB_parameter_hashable=self.get_parameter_hashable(ORB_parameters)
        if self.store_compute:
            if image_name in self.computed.keys():
                if ORB_parameter_hashable in self.computed[image_name].keys():
                    return self.computed[image_name][ORB_parameter_hashable]
            else:
                self.computed[image_name]=dict()
        computed_orb=self.compute_orb(image_name,ORB_parameters)
        if self.store_compute:
            self.computed[image_name][ORB_parameter_hashable]=computed_orb
        return computed_orb

def generate_match_combinations(strategy,**kwargs)-> list[list]: 
    if strategy=="order":
        return generate_match_combinations_in_order(kwargs["order"])
    elif strategy=="short_pairs":
        return generate_match_combinations_from_short_pairs(kwargs["short_pairs"],kwargs["short_lookup"])
    elif strategy=="all":
        return generate_match_combinations_all_combinations(kwargs["all"])
    elif strategy=="search":
        return generate_match_combinations_all_combinations(kwargs["search"],kwargs["all"])
    else:
        raise ValueError(f"'{strategy}' is not a valid strategy.")
def generate_match_combinations_in_order(order:list):
    return [[a,b] for a,b in zip(order[:-1],order[1:])]
def generate_match_combinations_from_short_pairs(short_pairs:list[list],short_lookup:ImageManager.lookup_name):
    pass #TODO
def generate_match_combinations_all_combinations(items:list):
    pass #TODO
def generate_match_combinations_search(search:str,items:list):
    pass #TODO

def generate_match_bf(
        image1:str,
        image2:str,
        match_reduction_ratio:float,
        OrbM:ORBManager,
        ORB_parameters:dict=None)->list[cv.DMatch]:
    brute_force_matcher = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
    orb1=OrbM.get_orb(image1,ORB_parameters)
    orb2=OrbM.get_orb(image2,ORB_parameters)
    matches = brute_force_matcher.match(orb1["des"],orb2["des"])
    sorted_matches = sorted(matches, key = lambda x:x.distance)
    reduced_matches = matches[:int(len(sorted_matches)*(match_reduction_ratio))]
    return reduced_matches,orb1,orb2

def estimate_translation(
        matches,
        orb1,
        orb2,
        limit_affine_rotation=0.01, #maximum affine rotation without correction i.e. -0.01rad to +0.01rad rotations are acceptable.
        limit_affine_scale=0.01, #maximum affine scale without correction i.e. 0.99 scale to 1.01 scale are acceptable.
        limit_minimum_points=5, #minimum number of matched points for succesful translation estimate.
        limit_inlier_consistency=0.6, #minimum fraction of matched points that must be consistent.
        limit_inlier_radius=10 # minimum L2 distance between points to be considered consistent.
    )->list[list,bool]:
    
    pts_1=np.array([orb1["kp"][match.queryIdx].pt for match in matches])
    pts_2=np.array([orb2["kp"][match.trainIdx].pt for match in matches])
    eAP2D_matrix,eAP2D_in_out=cv.estimateAffinePartial2D(pts_1,pts_2)

    eAP2D_translationx=eAP2D_matrix[0,2]
    eAP2D_translationy=eAP2D_matrix[1,2]
    eAP2D_scalex=(eAP2D_matrix[0,0]**2+eAP2D_matrix[0,1]**2)**0.5
    eAP2D_scaley=(eAP2D_matrix[1,1]**2+eAP2D_matrix[1,0]**2)**0.5
    eAP2D_rotation=np.arctan(eAP2D_matrix[0,1]/eAP2D_matrix[1,1])
    eAP2D_inliers=[(tuple(pt1),tuple(pt2)) for pt1,pt2,in_out in zip(pts_1,pts_2,eAP2D_in_out) if in_out]
    eAP2D_inliers_count=len(eAP2D_inliers)
    if abs(eAP2D_rotation)<limit_affine_rotation and abs(eAP2D_scalex-1)<limit_affine_scale:
        # rotation is close to 0 and scale is close to 1 > Likely good translation fit.
        if eAP2D_inliers_count>=limit_minimum_points:
            # reasonable number of points have been found
            overall=True
            individual=[True]*eAP2D_inliers_count
        else:
            # too few points have been found
            overall=False
            individual=[True]*eAP2D_inliers_count
    else:
        # rotation or scale are outside limits.
        inlier_translations=[(pt1[0]-pt2[0],pt1[1]-pt2[1]) for pt1,pt2 in eAP2D_inliers] # convert points pairs to translations
        inter_inlier_distances=[[((inlier_trans[0]-other_trans[0])**2+(inlier_trans[1]-other_trans[1])**2)**0.5 for other_trans in inlier_translations]
            for inlier_trans in inlier_translations] # find distance between all inlier-inlier distances
        inlier_radius_limit=[[distance<limit_inlier_radius for distance in iid] for iid in inter_inlier_distances] # check i-i distances less than radius limit
        inlier_consistency_limit=[sum(irl)>=limit_inlier_consistency*eAP2D_inliers_count for irl in inlier_radius_limit] # check radius limit counts for consistency
        individual=inlier_consistency_limit
        overall=sum(individual)>=limit_minimum_points # check reasonable number of points have been found
        # print(inlier_translations)
        # print(inter_inlier_distances)
        # print(inlier_radius_limit)
        # print(inlier_consistency_limit)
        # print(individual)
        # print(overall) #TODO add more warning/error reporting or optional passthrough
    valid={"overall":overall,"individual":individual}
    return eAP2D_inliers, valid

class AlignCVManager():
    def __init__(self,ImageM:ImageManager,OrbM:ORBManager):
        self.ImageM=ImageM
        self.OrbM=OrbM
        self.alignments=[]
    def run_alignment(self,match_combinations,match_reduction_ratio=1/2,ORB_parameters=None):
        alignment_data={"alignment_parameters":
                        {"match_combinations":match_combinations,
                         "match_reduction_ratio":match_reduction_ratio,
                         "ORB_parameters":ORB_parameters,
                         "source":"run_alignment"
                         },"alignment_data":dict()}
        for image1,image2 in match_combinations:
            image_set=(image1,image2)
            matches,orb1,orb2=generate_match_bf(
                image1=image1,
                image2=image2,
                match_reduction_ratio=match_reduction_ratio,
                OrbM=self.OrbM,
                ORB_parameters=ORB_parameters
                )
            estimated_translation_inliers, estimated_translation_validity = estimate_translation(matches,orb1,orb2) #TODO estimate_translation parameter passthrough
            alignment_data["alignment_data"][image_set]={
                "matches":matches,
                "estimated_translation_inliers":estimated_translation_inliers,
                "estimated_translation_validity":estimated_translation_validity
                }
        self.alignments.append(alignment_data)
        return len(self.alignments)-1
    def get_alignment(self,alignment_id):
        return self.alignments[alignment_id]
    def update_mis(self,
            mis_project:MisFile,
            alignment_id,
            valid_only=True)->MisFile:
        alignment_results=self.alignments[alignment_id]
        match_combinations=alignment_results["alignment_parameters"]["match_combinations"]
        for mc in match_combinations:
            mc_alignment_result=alignment_results["alignment_data"][tuple(mc)]
            if valid_only and not mc_alignment_result["estimated_translation_validity"]["overall"]:
                print(f"Warning: Match {mc} not valid. No relation saved.")
                continue
            mis_project._relations.append(Relation(
                mc[0],
                mc[1],
                'p',
                [([int(x) for x in pt1],[int(x) for x in pt2]) for (pt1,pt2),individual_valid in zip(mc_alignment_result['estimated_translation_inliers'],mc_alignment_result["estimated_translation_validity"]["individual"]) if individual_valid] ))        
    def get_valid_match_combinations(self,alignment_id):
        return [mc for mc in self.alignments[alignment_id]["alignment_parameters"]["match_combinations"] if self.alignments[alignment_id]["alignment_data"][tuple(mc)]["estimated_translation_validity"]["overall"]]
    def get_invalid_match_combinations(self,alignment_id):
        return [mc for mc in self.alignments[alignment_id]["alignment_parameters"]["match_combinations"] if not self.alignments[alignment_id]["alignment_data"][tuple(mc)]["estimated_translation_validity"]["overall"]]
    def alignment_parameter_progression(self,step=0):
        return {"match_reduction_ratio":(1/2),"ORB_parameters":{"nfeatures": 500*(2**step),"edgeThreshold": 5 }}
    def merge_alignments(self,alignment_ids:list):
        alignment_data={"alignment_parameters":
                        {"match_combinations":list(set([tuple(mc) for match_combinations in [self.alignments[alignment_id]["alignment_parameters"]["match_combinations"] for alignment_id in alignment_ids] for mc in match_combinations])),
                            "source":"merge_alignments"},
                        "alignment_data":dict()}
        for alignment_id in alignment_ids:
            alignment=self.alignments[alignment_id]
            for mc in alignment["alignment_parameters"]["match_combinations"]:
                alignment_data["alignment_data"][tuple(mc)]=alignment["alignment_data"][tuple(mc)]
                # naturally overwrite earlier results with later results.
        self.alignments.append(alignment_data)
        return len(self.alignments)-1
            
