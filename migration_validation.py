import csv
import os
import pandas as pd
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.SetupParser import SetupParser
from simtools.ModBuilder import ModBuilder, ModFn
import sys

sys.path.append('../helpers/')
from load_paths import load_box_paths
from set_up_ghana_site import setup_simulation

# Emod functions
from dtk.utils.reports.CustomReport import add_human_migration_tracking_report, add_node_demographics_report
from dtk.utils.reports.VectorReport import add_vector_migration_report
from malaria.reports.MalariaReport import add_filtered_spatial_report
from dtk.interventions.migrate_to import add_migration_event

SetupParser.default_block = 'HPC'
projectpath, datapath = load_box_paths()

exp_name = 'ghana_nxtek_SM_ledger_10run'
input_file_name = '' \
                  ''
n_seeds = 1
years = 2
migration_to_test = 'human'
simulation_duration = 365 * years
if migration_to_test == 'vector':
    simulation_duration = 100

cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')

setup_simulation(cb, years, outbreak=False, input_file_name=input_file_name)
cb.update_params({'Demographics_Filenames': [os.path.join('demographics', '%s_demographics.json' % input_file_name)],
                  'Simulation_Duration': simulation_duration,
                  'x_Temporary_Larval_Habitat': 0.01,
                  'Vector_Sampling_Type': 'TRACK_ALL_VECTORS',
                  'Enable_Birth': 0,  # no births in migration testing sims
                  'Enable_Natural_Mortality': 0  # no deaths in migration testing sims
                  })


def add_special_migration(cb):
    # Set Is_Moving = True
    # Set Dont_Allow_Duplicates = False
    mig_events = pd.read_csv(os.path.join('%s' % datapath, 'migration',
                                          'migration_ledgers_events.csv'))
    for index, row in mig_events.iterrows():
        start = int(row["start_day"])
        ledger = str(row["ledger"])
        node_from = int(row["node_from"])
        node_to = int(row["node_to"])
        at_node = int(row["at_node"])

        duration_at_node = {"Duration_At_Node_Distribution": "CONSTANT_DISTRIBUTION",
                            "Duration_At_Node_Constant": at_node}
        duration_before_leaving = {"Duration_Before_Leaving_Distribution": "CONSTANT_DISTRIBUTION",
                                   "Duration_Before_Leaving_Constant": 10}
        duration_before_leaving = {"Duration_Before_Leaving_Distribution": "UNIFORM_DISTRIBUTION",
                                   "Duration_Before_Leaving_Min": 7,
                                   "Duration_Before_Leaving_Max": 112}

        add_migration_event(cb,
                            start_day=start,
                            nodesfrom=[node_from],
                            nodeto=node_to,
                            coverage=1,
                            duration_at_node=duration_at_node,
                            duration_before_leaving=duration_before_leaving,
                            ind_property_restrictions=[{"Ledger": ledger}],
                            repetitions=1)

    return {'SpecialMigration': "ON"}


# def add_special_migration(cb, c=7):
#     # Changed Is_Moving="True"
#     # Changed Dont_Allow_Duplicates="False"
#     duration_at_node = {"Duration_At_Node_Distribution": "GAUSSIAN_DISTRIBUTION",
#                         "Duration_At_Node_Gaussian_Mean": 999,
#                         "Duration_At_Node_Gaussian_Std_Dev": 1}
#     duration_before_leaving = {"Duration_Before_Leaving_Distribution": "GAUSSIAN_DISTRIBUTION",
#                                "Duration_Before_Leaving_Gaussian_Mean": 40,
#                                "Duration_Before_Leaving_Gaussian_Std_Dev": 20}
#     duration_at_node = {"Duration_At_Node_Distribution": "CONSTANT_DISTRIBUTION",
#                         "Duration_At_Node_Constant": 500}
#     duration_before_leaving = {"Duration_Before_Leaving_Distribution": "CONSTANT_DISTRIBUTION",
#                                "Duration_Before_Leaving_Constant": 1}
#
#     filename = os.path.join('%s' % projectpath, 'simulation_inputs', 'migration',
#                             '%s_Special_migration2.csv' % input_file_name)
#     with open(filename) as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=',', )
#         next(csv_reader)  # skip header row
#         for row in csv_reader:
#             start = int(row[1])
#             node_from = int(row[3])
#             node_to = int(row[5])
#             cov = float(row[c])
#
#             add_migration_event(cb,
#                                 start_day=start,
#                                 nodesfrom=[node_from],
#                                 nodeto=node_to,
#                                 coverage=cov,
#                                 duration_at_node=duration_at_node,
#                                 duration_before_leaving=duration_before_leaving,
#                                 repetitions=1
#                                 )
#     return {'sm_cov_col': c}


builder = ModBuilder.from_list([[ModFn(DTKConfigBuilder.set_param, 'Run_Number', x)]
                                for x in range(n_seeds)
                                ])

add_filtered_spatial_report(cb, start=0,
                            channels=['Adult_Vectors', 'Population'])

if migration_to_test == 'human':
    # add_covid_migration(cb, start=0, intervals_of_movement=int(years * 365 / 120), other_node=3, village_nodes=[1, 2])
    add_special_migration(cb)
    add_human_migration_tracking_report(cb)
    add_node_demographics_report(cb, IP_key_to_collect="Ledger")
elif migration_to_test == 'vector':
    add_vector_migration_report(cb)

# run_sim_args is what the `dtk run` command will look for
run_sim_args = {
    'exp_name': exp_name,
    'config_builder': cb,
    'exp_builder': builder
}

if __name__ == "__main__":
    SetupParser.init()
    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(**run_sim_args)














