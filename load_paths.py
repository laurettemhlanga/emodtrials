import os


# def load_box_paths(user_path=None, Location=None):
#     if Location is None:
#         if os.name == "posix":
#             Location = "NUCLUSTER"
#         else:
#             Location = "HPC"
#
#     if Location == 'NUCLUSTER':
#         user_path = '/projects/b1139/'
#         home_path = os.path.join(user_path, 'urban_malaria')
#         data_path = os.path.join(home_path, 'simulation_inputs')
#     else:
#         if not user_path:
#             user_path = os.path.expanduser('~')
#
#         home_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'projects', 'urban_malaria')
#         data_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'data')
#
#
#     return home_path, data_path,

def load_box_paths(user_path=None, parser_default='HPC'):
# adapt the code to suite you file structure

    if not user_path :
        user_path = os.path.expanduser('~')
        if 'lml6626' in user_path :
            home_path = os.path.join(user_path, 'Documents', 'urban_malaria')
            # data_path = os.path.join(home_path, 'input', 'demographics')
        else :
            home_path = os.path.join(user_path, 'Documents', 'urban_malaria', "github_clones")

    inputs_path = os.path.join(home_path,'emodtrials','input', 'demographics', 'Ghana')

    return home_path, inputs_path



