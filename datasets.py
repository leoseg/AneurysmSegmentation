import os.path as osp
from nibabel.parrec import PSL_TO_RAS
import os
import torch
from torch_geometric.data import Dataset
from pathlib import Path
import utils
import nibabel as nib
import numpy as np

class NiftiDataset(Dataset):
    def __init__(self, root,save_dir,transform=None, pre_transform=None,forceprocessing =False):
        self.forceprocessing = forceprocessing
        self.save_dir =save_dir
        super(NiftiDataset, self).__init__(root, transform, pre_transform)
        
    @property
    def processed_file_names(self):
        if os.path.exists(self.processed_dir) and not self.forceprocessing:
            return ([file for file in os.listdir(self.processed_dir) if file.startswith("data")])
        else:

            return []
    @property
    def raw_file_names(self):
        return os.listdir(self.root)

    
    @property
    def processed_dir(self) -> str:
        return self.save_dir
    def process(self):
        self.cases = set()
     
        for filename in os.listdir(self.root):
            if filename.endswith(".nii"):
                self.cases.add(filename.split('_')[0])
                #g = filename.split('_')[0]
                #cases.setdefault(g, []).append(filename)
        for idx,case in enumerate(self.cases):
            torch.save(self.file_to_data(case), osp.join(self.save_dir, "data_{}.pt".format(idx)))
        self.forceprocessing=False    

    def file_to_data(self,case):
        image = utils.min_max_normalize(nib.load(self.root+ "/"+case+'_orig.nii').get_fdata())
        image_aneursysm = nib.load(self.root + "/"+case+'_masks.nii').get_fdata()
        mask =utils.intensity_segmentation(image,0.34)
        filtered= np.multiply(image,mask)
        return utils.segmented_image_to_graph(filtered,image_aneursysm)
        


    def len(self):
        return len(self.processed_file_names)

    def get(self, idx):
        try:
            data = torch.load(osp.join(self.processed_dir, 'data_{}.pt'.format(idx)))
            return data
        except:
            print(f"Couldnt read data_{idx}.pt")
            return None


if __name__ == '__main__':
    data_path ="/workspaces/project_med/project/data"
    root_path = "/workspaces/project_med/project/data"
    dataset= NiftiDataset(root_path)
