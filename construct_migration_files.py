import json
import os

from input_file_generation.convert_txt_to_bin import convert_txt_to_bin

#C:\Users\lml6626\Documents\urban_malaria\emod_trials\input\Ghana
#C:\Users\User\Documents\urban_malaria\github_clones
user_path = os.path.expanduser("~")
home_path = os.path.join(user_path, 'Documents', 'urban_malaria', "github_clones" )
data_path = os.path.join(home_path, 'emodtrials', 'input')
project_path = os.path.join(data_path, 'Ghana')

demo_fname = os.path.join(data_path, 'Ghana', 'Ghana_demographics.json')

with open(demo_fname) as fin:
    demo = json.loads(fin.read())
id_reference = demo['Metadata']['IdReference']

#C:\Users\lml6626\Documents\urban_malaria\emod_trials\input
# mig_type = 'LOCAL'
convert_txt_to_bin(os.path.join(data_path,'local_migration.csv'),
                   'local_migration.bin',
                    mig_type = 'LOCAL_MIGRATION',
                    id_reference = id_reference)

cb.update_params({
        # Migration
        'Migration_Model': 'FIXED_RATE_MIGRATION', # turn on human migration
        'Migration_Pattern': 'SINGLE_ROUND_TRIPS', # human trips are round trips (see documentation for other options)

        'Enable_Local_Migration': 1,               # turn on Local human migration
        'Local_Migration_Roundtrip_Duration': 5,   # Local trips last 5 days can edit to this to 14 days
        'Local_Migration_Roundtrip_Probability': 1,# traveler returns home in 100% of Local trips
        'x_Local_Migration': 0.02,                 # Scale factor used to fix the average # of trips per person, per year.
        'Local_Migration_Filename': 'local_migration.bin' # path to migration file
    })