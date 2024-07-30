## 生成gcasp数据集

1. clone repo 并下载必要的数据
   
    
    ```
    git clone https://github.com/UltraHertzz/gcasp_lsx.git
    ```
    
2. google drive 链接
    1. 纹理obj, 用于生成rgb, depth等场景
        [下载文件](https://drive.google.com/file/d/1Kv4HX4HlBceb9KGb2U-kh1x_XsM_WfkF/view?usp=drive_link)
    2. 白模obj, 用于生成语义点元
        [下载文件](https://drive.google.com/file/d/1BsKnMgsS6g03OEseaSBVMD2zH7BvsE_E/view?usp=drive_link)

3. 流程
   ```bash
   # 1. 预处理，清理ShapeNet中模型的纹理文件，否则o3d.io.read_triangle_mesh()报错
   python cap_mtl.py

   # 2. 生成所有类的semantic primitive
   python generate_primitives.py
   # 如果只想生成椅子的
   python generate_primitives_for_chair.py

   # 3. 查看sp生成情况
   python primitive_vis.py
   ```