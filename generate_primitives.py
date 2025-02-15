import os
import yaml
import json
import torch
import open3d
import argparse
import warnings
import numpy as np
warnings.filterwarnings('ignore')
from tqdm import tqdm
from DualSDFHandler import DualSDFHandler

class ShapeNetNOCS(torch.utils.data.Dataset,):
    def __init__(self, datadir, split, category):
        self.objs = []
        self.shape_id = []
        with open(split,'r') as f:
            self.fp = json.load(f)
        for model_dir in self.fp['ShapeNetV2'][category]:
            if category == '03797390':
                continue # 跳过bottle, 其在read_triangle_mesh过程中出现问题
            if category == '03001627':
                obj_path = os.path.join(datadir,category,model_dir, 'models','model_normalized.obj')
                
            else:
                obj_path = os.path.join(datadir,category,model_dir, 'model.obj')
                print(f"Loading OBJ file from path: {obj_path}")
                
                if not os.path.exists(obj_path):
                    print(f"File does not exist: {obj_path}")
                    continue
            try:
                obj = open3d.io.read_triangle_mesh(obj_path)
            except Exception as e:
                print(f"Error loading file {model_dir}: {e}")

            if obj.is_empty():
                print(f"Failed to load mesh from: {obj_path}")
                continue
            self.objs.append(obj)
            self.shape_id.append(model_dir)
            """
            ## Loading OBJ file from path: ./eval_datas/obj_models/train/02876657/abe557fa1b9d59489c81f0389df0e98a/model.obj
            Not a JPEG file: starts with 0x89 0x50 在读取过程中出现错误
            """
            

    def __getitem__(self, index):
        return self.objs[index], self.shape_id[index]

    def __len__(self):
        return len(self.objs)

def get_args():    
    def dict2namespace(config):
        namespace = argparse.Namespace()
        for key, value in config.items():
            if isinstance(value, dict):
                new_value = dict2namespace(value)
            else:
                new_value = value
            setattr(namespace, key, new_value)
        return namespace

    # parse config file
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    config = dict2namespace(config)

    return args, config

def pc_normalize(pc):
    centroid = (np.amax(pc, axis=-2, keepdims=True) + np.amin(pc, axis=-2, keepdims=True))/2
    pc = pc - centroid
    l = np.sqrt(np.sum(pc**2, axis=-1, keepdims=True))
    m = np.amax(l, axis=-2,keepdims=True)
    pc = pc / m
    return pc, m, centroid

if __name__ == "__main__":
    
    id2name = {
        '02946921' : 'can',
        '03797390' : 'mug',
        '02876657' : 'bottle',
        '03642806' : 'laptop',
        '02942699' : 'camera',
        '02880940' : 'bowl',
        '03001627' : 'chair',
    }

    class Args:
        def __init__(self):
            self.config = None
            self.pretrained = None

    args = Args()
    num_spheres = [256]
    save_dir = './train_datas/NOCS_primitives'
    os.makedirs(save_dir,exist_ok=True)

    all_attrs = {}

    for item in id2name.items():
        if not os.path.exists(f'./datasets/splits/sv2_{item[1]}_all.json'):
            print(f'Could not find sv2_{item[1]}_all.json')
            continue
        dataset = ShapeNetNOCS('./eval_datas/obj_models/train', f'./datasets/splits/sv2_{item[1]}_all.json', item[0])
        print(item)
        for n_sphere in num_spheres:
            print(n_sphere)
            args.config = f'./config/dualsdf_{item[1]}_{n_sphere}.yaml'
            ckpts = []
            for p in os.scandir(f'./eval_datas/DualSDF_ckpts/{item[1]}/{n_sphere}'):
                ckpts.append(p.path)
            # print(sorted(ckpts))
            args.pretrained = sorted(ckpts)[-1]
            print(args.pretrained)
            args, cfg = get_args()
            runner = DualSDFHandler(args, cfg)
            runner.trainer.eval()

            attrs_dict = {}

            for i,(mesh,shape_id) in enumerate(dataset):
                print(shape_id+f"_{n_sphere}")

                attrs = runner.sample(i)
                vertices, norm_scale, norm_shift = pc_normalize(np.array(mesh.vertices))
                
                attrs[:,1:] = attrs[:,1:]*norm_scale+norm_shift
                attrs[:,2] = -attrs[:,2]
                attrs[:,0] = attrs[:,0] + np.log(norm_scale)

                attrs_dict[shape_id] = attrs.tolist()
                all_attrs[shape_id+f"_{n_sphere}"] = attrs.tolist()
            
            with open(os.path.join(save_dir,f'attrs_{item[0]}_{item[1]}_{n_sphere}.json'),'w') as f:
                json.dump(attrs_dict, f)