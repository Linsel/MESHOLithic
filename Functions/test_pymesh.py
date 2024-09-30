import pymesh

# def difference_procedure ():

#     path = '/media/linsel/Extreme Pro/3D/TEST_DATA/'

#     mesh_A = pymesh.load_mesh(f"{path}0_000_GMCF.ply")
#     mesh_B = pymesh.load_mesh(f"{path}0_001_GMCF.ply")
#     output_mesh = pymesh.boolean(mesh_A, mesh_B,
#                                 operation="intersection",
#                                 engine="igl")

#     del mesh_A,mesh_B

#     pymesh.save_mesh(f"{path}0_000-001_intersection.ply",output_mesh)



# def __main__(args):
path = '/media/linsel/Extreme Pro/3D/TEST_DATA/'

# mesh_A = pymesh.load_mesh(f"{path}0_000_GMCF_simp.ply")
# # mesh_A = pymesh.load_mesh(f"{path}RF.c-6.ply")
# mesh_B = pymesh.load_mesh(f"{path}0_001_GMCF_O_simp.ply")
# # mesh_B = pymesh.load_mesh(f"{path}RF.c-7.ply")

mesh_A = pymesh.load_mesh(f"{path}0_000_GMCF_simp05-05.ply")
mesh_B = pymesh.load_mesh(f"{path}0_001_GMCF_O_simp05-05.ply")



output_mesh = pymesh.boolean(mesh_A, mesh_B,
                            operation="difference",
                            engine="igl")

del mesh_A,mesh_B

pymesh.save_mesh(f"{path}0_001_GMCF_difference.ply",output_mesh)
