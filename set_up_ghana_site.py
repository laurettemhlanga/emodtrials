
import os
import pandas as pd
import copy
from dtk.vector.species import set_species, set_larval_habitat
from dtk.interventions.habitat_scale import scale_larval_habitats
from dtk.interventions.outbreakindividual import recurring_outbreak
from interventions import add_MTTT,add_MTTT_2, add_special_migration
from load_paths import load_box_paths

datapath, projectpath = load_box_paths()


def set_up_basic_params(cb, years) :

    cb.update_params({'Enable_Vital_Dynamics': 1,
                      'Enable_Births': 1,
                      'Birth_Rate_Dependence': 'FIXED_BIRTH_RATE',
                      'Disable_IP_Whitelist': 1,
                      'Maternal_Antibodies_Type': 'CONSTANT_INITIAL_IMMUNITY',
                      "Incubation_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
                      'Parasite_Smear_Sensitivity': 0.02,
                      "Report_Detection_Threshold_Blood_Smear_Parasites": 10,
                      "Report_Detection_Threshold_PCR_Parasites": 0.1, # (EMOD default: 0.05) (historic: 0.1) (lit: 3.2)
                      'logLevel_JsonConfigurable': 'ERROR',
                      'logLevel_SusceptibilityMalaria': 'ERROR',
                      'Simulation_Duration': years * 365,
                      'Memory_Usage_Halting_Threshold_Working_Set_MB' : 500000
                      })


def set_up_input_files(cb, input_file_name):

    cb.update_params({'Demographics_Filenames': [os.path.join('demographics', '%s_demographics.json' % input_file_name)],
                      "Air_Temperature_Filename": os.path.join('climate', '%s_air_temperature_daily.bin' % input_file_name),
                      "Land_Temperature_Filename": os.path.join('climate', '%s_air_temperature_daily.bin' % input_file_name),
                      "Rainfall_Filename": os.path.join('climate', '%s_rainfall_daily.bin' % input_file_name),
                      "Relative_Humidity_Filename": os.path.join('climate', '%s_relative_humidity_daily.bin' % input_file_name),
                      'Age_Initialization_Distribution_Type': 'DISTRIBUTION_COMPLEX'})


def set_up_larval_habitat(cb, habitat_df) :

    set_species(cb, ['gambiae'])

    ls_hab_ref = {'Capacity_Distribution_Number_Of_Years': 1,
                  'Capacity_Distribution_Over_Time': {
                      'Times': [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334],
                      'Values': [0, 0, 0, 0, 0, 0.0014, 0.0011434760050832527, 0, 0, 0, 0, 0.0009734590867061002]
                  },
                  'Max_Larval_Capacity': pow(10, 10.028)}

    set_larval_habitat(cb, {'gambiae': {'LINEAR_SPLINE': ls_hab_ref,
                                        'CONSTANT': pow(10, 6.929446837587772)}})

    if habitat_df is not None :
        scale_habitats_from_file(cb, copy.copy(habitat_df))


def scale_habitats_from_file(cb, habitat_df) :

    # handle node-specific habitat scaling
    hab_list = []
    for species_params in cb.get_param("Vector_Species_Params"):
        habitats = species_params["Larval_Habitat_Types"]
        hab_list += [h for (h, v) in habitats.items()]
    hab_list = list(set(hab_list))

    for hab_type in ['TEMPORARY_RAINFALL', 'CONSTANT', 'LINEAR_SPLINE', 'WATER_VEGETATION'] :
        if hab_type in hab_list :
            habitat_df[hab_type] = copy.copy(habitat_df['habitat_scale'])
    del habitat_df['habitat_scale']
    scale_larval_habitats(cb, habitat_df)


def set_up_human_migration(cb) :

    stem = 'ghana_nxtek_4node'
    cb.update_params({
        # Migration
        'Migration_Model': 'FIXED_RATE_MIGRATION',
        'Migration_Pattern': 'SINGLE_ROUND_TRIPS',

        'Enable_Local_Migration': 0,
        'Local_Migration_Roundtrip_Duration': 5,
        'Local_Migration_Roundtrip_Probability': 1,
        'x_Local_Migration': 0.02,  # 0.1 -> 5 trips per person per year to each node
        'Local_Migration_Filename': 'migration/%s_Local_Migration.bin' % stem,

        'Enable_Regional_Migration': 0,
        'Regional_Migration_Roundtrip_Duration': 30,
        'Regional_Migration_Roundtrip_Probability': 1,
        'x_Regional_Migration': 0.1,  # 0.1 -> 1 trip per person per year from node 1 or 2 to node 3
        'Regional_Migration_Filename': 'migration/%s_Regional_Migration.bin' % stem,
    })


def set_up_vector_migration(cb) :

    stem = 'ghana_nxtek_4node'
    cb.update_params({
        'Enable_Vector_Migration': 1,
        "Vector_Migration_Base_Rate": 0.15,
        'Vector_Migration_Food_Modifier': 0,
        'Vector_Migration_Habitat_Modifier': 0,
        'Vector_Migration_Modifier_Equation': 'LINEAR',
        'Vector_Migration_Stay_Put_Modifier': 0,
        'Enable_Vector_Migration_Local': 1,
        'x_Vector_Migration_Local': 0.01,
        'Vector_Migration_Filename_Local': 'migration/%s_Vector_Local_Migration.bin' % stem,
    })


def set_up_biting_risk(cb):
    cb.update_params({
        'Enable_Demographics_Risk': 1})


def set_up_serialization(cb, serialize, pull_from_serialization, serialize_year, pull_year) :

    # note this function does NOT set up the Serialized_Population_Path when picking up a burnin!
    if serialize:
        cb.update_params({
            'Serialization_Time_Steps': [365 * serialize_year],
            'Serialization_Type': 'TIMESTEP',
            'Serialized_Population_Writing_Type': 'TIMESTEP',
            'Serialized_Population_Reading_Type': 'NONE',
            'Serialization_Mask_Node_Write': 0,
            'Serialization_Precision': 'REDUCED'
        })
    elif pull_from_serialization:
        cb.update_params({
            'Serialized_Population_Reading_Type': 'READ',
            'Serialized_Population_Filenames': ['state-%05d.dtk' % (pull_year*365)],
            'Enable_Random_Generator_From_Serialized_Population': 0,
            'Serialization_Mask_Node_Read': 0,
            'Enable_Default_Reporting' : 0
        })


def setup_simulation(cb, years, input_file_name='ghana_nxtek_4node_withMalaria_withledger',
                     migration=True, special_migration=False, MTTT= False, MTTT_Coverage=1.0, outbreak=True,
                     serialize=False, pull_from_serialization=False,
                     serialize_year=0, pull_year=0,
                     habitat_df=None):

    set_up_basic_params(cb, years)
    set_up_input_files(cb, input_file_name=input_file_name)
    set_up_larval_habitat(cb, habitat_df=habitat_df)
    set_up_biting_risk(cb)
    if migration :
        set_up_human_migration(cb)
        #set_up_vector_migration(cb)
    if special_migration:
        add_special_migration(cb)
    if MTTT:
        add_MTTT_2(cb, start=260, rounds=4, interval=120, coverage=MTTT_Coverage, tracking_only=True)

    if outbreak :
        recurring_outbreak(cb, start_day=180, repetitions=years, tsteps_btwn=365, outbreak_fraction=0.01)
    if serialize or pull_from_serialization :
        set_up_serialization(cb, serialize=serialize, pull_from_serialization=pull_from_serialization,
                             serialize_year=serialize_year, pull_year=pull_year)
    else :
        cb.update_params({
            'Serialization_Type': 'NONE',
            'Serialized_Population_Writing_Type': 'NONE'
        })

    if habitat_df is None :
        return {}
    else :
        return {
            'node_%d_hab' % row['NodeID']: row['habitat_scale'] for r, row in habitat_df.iterrows()
        }