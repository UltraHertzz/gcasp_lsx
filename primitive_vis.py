import json
import open3d as o3d
import torch
import numpy as np
import colorsys


def generate_colors(num_colors):
    colors = []
    for i in range(num_colors):
        hue = i / num_colors
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        colors.append(rgb)
    return colors

def json_load(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
    
if __name__ == "__main__":
    # Load the data
    # data = json_load('./train_datas/NOCS_primitives/attrs_02946921_can_256.json')
    # data = json_load('./train_datas/NOCS_primitives/attrs_03797390_mug_256.json')
    data = json_load('./train_datas/NOCS_primitives/attrs_03001627_chair_256.json')

    # generate colors for semantic primitives
    colors = generate_colors(256)

    transform = torch.tensor([[1, 0, 0, 0],
                              [0, 1, 0, 0],
                              [0, 0, 1, 0],
                              [0, 0, 0, 1]])
    
    all_spheres = []

    for i , (obj_id, attrs) in enumerate(data.items()):
        if i == 5:
            break
        
        for j, attr in enumerate(attrs):
            r, x, y, z = attr
            sphere = o3d.geometry.TriangleMesh.create_sphere()
            sphere.compute_vertex_normals()
            sphere.scale(np.exp(r), center=(0, 0, 0))
            sphere.translate((x, y+i, z))
            sphere.paint_uniform_color(colors[j])


            all_spheres.append(sphere)


    # Visualize the point cloud
    o3d.visualization.draw(all_spheres)