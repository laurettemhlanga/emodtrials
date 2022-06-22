import os


def load_box_paths(user_path=None, Location=None):
    if Location is None:
        if os.name == "posix":
            Location = "NUCLUSTER"
        else:
            Location = "HPC"

    if Location == 'NUCLUSTER':
        user_path = '/projects/b1139/'
        home_path = os.path.join(user_path, 'urban_malaria')
        data_path = os.path.join(home_path, 'simulation_inputs')
    else:
        if not user_path:
            user_path = os.path.expanduser('~')

        home_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'projects', 'urban_malaria')
        data_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'data')


    return home_path, data_path,


