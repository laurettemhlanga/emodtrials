import os
import copy
import pandas as pd
import sys
sys.path.append('../helpers/')
from load_paths import load_box_paths
from malaria.interventions.health_seeking import add_health_seeking
from malaria.interventions.malaria_diagnostic import add_diagnostic_survey
from malaria.interventions.malaria_drug_campaigns import add_drug_campaign
from malaria.interventions.adherent_drug import configure_adherent_drug
from dtk.interventions.migrate_to import add_migration_event

datapath, projectpath = load_box_paths()

# Study MTTT Interventions

def add_MTTT(cb, start=244, interval=90, rounds=4, coverage=1, tracking_only=False):
    cb.update_params({'Report_Event_Recorder': 1,
                      'Report_Event_Recorder_Ignore_Events_In_List': 0,
                      'Report_Event_Recorder_Events': ['RDT_Positive_DT1',
                                                       'RDT_Positive_DT2'],
                      'Report_Event_Recorder_Individual_Properties': ['Ledger'],
                      'Custom_Individual_Events': ['MTTT_Done',
                                                   'RDT_Positive_MTTT',
                                                   'Received_MTTT_Drugs',
                                                   'DT1_Done', 'RDT_Positive_DT1',
                                                   'DT2_Done', 'RDT_Positive_DT2']})
    DT1 = 0.09
    DT2 = 0.1
    Sens1 = 0.5
    Sens2 = 0.87
    Spec1 = 0.95
    Spec2 = 0.95
    if tracking_only == True:
        pass
    else:
        # Hard-coded (for now) loop through 10 start_days
        for d in range(10):
        # Quarterly RDT on assigned start day
        # Node 1 - Nxtek
            add_diagnostic_survey(cb=cb, start_day=start + d + 1,
                                  repetitions=rounds, tsteps_btwn_repetitions=interval,
                                  diagnostic_type="PF_HRP2", diagnostic_threshold=DT1,
                                  sensitivity= Sens1, specificity=Spec1,
                                  event_name="MTTT", received_test_event="MTTT_Done",
                                  nodeIDs=[1],
                                  IP_restrictions=[{"DOW": str(d)}],
                                  positive_diagnosis_configs=[{"class": "BroadcastEvent",
                                                               "Broadcast_Event": 'RDT_Positive_MTTT'}])
        # Node 2- SDBioline
            add_diagnostic_survey(cb=cb, start_day=start + d + 1,
                                  repetitions=rounds, tsteps_btwn_repetitions=interval,
                                  diagnostic_type="PF_HRP2", diagnostic_threshold=DT2,
                                  sensitivity=Sens2, specificity=Spec2,
                                  event_name="MTTT", received_test_event="MTTT_Done",
                                  nodeIDs=[2],
                                  IP_restrictions=[{"DOW": str(d)}],
                                  positive_diagnosis_configs=[{"class": "BroadcastEvent",
                                                               "Broadcast_Event": 'RDT_Positive_MTTT'}])
        # Drugs given if RDT positive
        #adherent_drug_configs= mttt_adherence_configuration(cb,adherence)
        add_drug_campaign(cb=cb, campaign_type="MDA", drug_code="AL", start_days=[1],
                          coverage=coverage, trigger_condition_list=["RDT_Positive_MTTT"],
                          receiving_drugs_event_name="Received_MTTT_Drugs",
                          nodeIDs=[1, 2], target_residents_only=0)

    # Other 'Listening' RDTs to track RDT prevalence throughout study period (not just during MTTT rounds)
    # Should NOT trigger any intervention / drug campaign

    add_diagnostic_survey(cb=cb, start_day=250, repetitions=400, tsteps_btwn_repetitions=5,
                          diagnostic_type="PF_HRP2", diagnostic_threshold=DT1, sensitivity=Sens1, specificity=Spec1,
                          event_name="DT1", received_test_event="DT1_Done",
                          nodeIDs=[1, 2],
                          positive_diagnosis_configs=[{"class": "BroadcastEvent",
                                                       "Broadcast_Event": 'RDT_Positive_DT1'}])
    add_diagnostic_survey(cb=cb, start_day=250, repetitions=400, tsteps_btwn_repetitions=5,
                          diagnostic_type="PF_HRP2", diagnostic_threshold=DT2, sensitivity=Sens2, specificity=Spec2,
                          event_name="DT2", received_test_event="DT2_Done",
                          nodeIDs=[1, 2],
                          positive_diagnosis_configs=[{"class": "BroadcastEvent",
                                                       "Broadcast_Event": 'RDT_Positive_DT2'}])

    return {
        'MTTT_Coverage': coverage
    }

def add_MTTT_2(cb, start=244, interval=90, rounds=4, coverage=1, tracking_only=False):
    cb.update_params({'Report_Event_Recorder': 1,
                      'Report_Event_Recorder_Ignore_Events_In_List': 0,
                      'Report_Event_Recorder_Events': ['RDT_Positive_DT1',
                                                       'RDT_Positive_DT2'],
                      'Report_Event_Recorder_Individual_Properties': ['Ledger'],
                      'Custom_Individual_Events': ['MTTT_Done',
                                                   'RDT_Positive_MTTT',
                                                   'Received_MTTT_Drugs',
                                                   'DT1_Done', 'RDT_Positive_DT1',
                                                   'DT2_Done', 'RDT_Positive_DT2']})
    DT1 = 3.2 # (default PCR detection threshold, from malaria/symptoms.py which should match insetChart reported PCR_Parasite_Prevalence used for Calibration)
    DT2 = 3.2
    Sens1 = 0.742 # Values from Linda's paper
    Sens2 = 0.755
    Spec1 = 0.846
    Spec2 = 0.861
    if tracking_only == True:
        pass
    else:
        # Hard-coded (for now) loop through 10 start_days
        for d in range(10):
        # Quarterly RDT on assigned start day
        # Node 1 - Nxtek
            add_diagnostic_survey(cb=cb, start_day=start + d + 1,
                                  repetitions=rounds, tsteps_btwn_repetitions=interval,
                                  diagnostic_type="PCR_PARASITES", diagnostic_threshold=DT1,
                                  sensitivity= Sens1, specificity=Spec1,
                                  event_name="MTTT", received_test_event="MTTT_Done",
                                  nodeIDs=[1],
                                  IP_restrictions=[{"DOW": str(d)}],
                                  positive_diagnosis_configs=[{"class": "BroadcastEvent",
                                                               "Broadcast_Event": 'RDT_Positive_MTTT'}])
        # Node 2- SDBioline
            add_diagnostic_survey(cb=cb, start_day=start + d + 1,
                                  repetitions=rounds, tsteps_btwn_repetitions=interval,
                                  diagnostic_type="PCR_PARASITES", diagnostic_threshold=DT2,
                                  sensitivity=Sens2, specificity=Spec2,
                                  event_name="MTTT", received_test_event="MTTT_Done",
                                  nodeIDs=[2],
                                  IP_restrictions=[{"DOW": str(d)}],
                                  positive_diagnosis_configs=[{"class": "BroadcastEvent",
                                                               "Broadcast_Event": 'RDT_Positive_MTTT'}])
        # Drugs given if RDT positive
        #adherent_drug_configs= mttt_adherence_configuration(cb,adherence)
        add_drug_campaign(cb=cb, campaign_type="MDA", drug_code="AL", start_days=[1],
                          coverage=coverage, trigger_condition_list=["RDT_Positive_MTTT"],
                          receiving_drugs_event_name="Received_MTTT_Drugs",
                          nodeIDs=[1, 2], target_residents_only=0)

    # Other 'Listening' RDTs to track RDT prevalence throughout study period (not just during MTTT rounds)
    # Should NOT trigger any intervention / drug campaign

    add_diagnostic_survey(cb=cb, start_day=250, repetitions=400, tsteps_btwn_repetitions=5,
                          diagnostic_type="PCR_PARASITES", diagnostic_threshold=DT1, sensitivity=Sens1, specificity=Spec1,
                          event_name="DT1", received_test_event="DT1_Done",
                          nodeIDs=[1, 2],
                          positive_diagnosis_configs=[{"class": "BroadcastEvent",
                                                       "Broadcast_Event": 'RDT_Positive_DT1'}])
    add_diagnostic_survey(cb=cb, start_day=250, repetitions=400, tsteps_btwn_repetitions=5,
                          diagnostic_type="PCR_PARASITES", diagnostic_threshold=DT2, sensitivity=Sens2, specificity=Spec2,
                          event_name="DT2", received_test_event="DT2_Done",
                          nodeIDs=[1, 2],
                          positive_diagnosis_configs=[{"class": "BroadcastEvent",
                                                       "Broadcast_Event": 'RDT_Positive_DT2'}])

    return {
        'MTTT_Coverage': coverage
    }





def smc_adherent_configuration(cb, adherence):
    smc_adherent_config = configure_adherent_drug(cb,
                                                  doses=[["Sulfadoxine", "Pyrimethamine",'Amodiaquine'],
                                                         ['Amodiaquine'],
                                                         ['Amodiaquine']],
                                                  dose_interval=1,
                                                  non_adherence_options=['Stop'],
                                                  non_adherence_distribution=[1],
                                                  adherence_config={
                                                        "class": "WaningEffectMapCount",
                                                        "Initial_Effect": 1,
                                                        "Durability_Map": {
                                                            "Times": [
                                                                1.0,
                                                                2.0,
                                                                3.0
                                                            ],
                                                            "Values": [
                                                                1,
                                                                adherence,
                                                                adherence
                                                            ]
                                                        }
                                                    }
    )
    return smc_adherent_config



def health_seeking(cb, kid_coverage, adult_scalar=0.6, start_day=0, nodeIDs=None) :

    school_age_scalar = 1 - ((1 - adult_scalar)*0.5)
    coverage_dict = [
        {'agemin' : 0,
         'agemax' : 5,
         'trigger' : 'NewClinicalCase',
         'coverage' : kid_coverage,
         'seek' : 1,
         'rate' : 0.3},
        {'agemin': 5,
         'agemax': 15,
         'trigger': 'NewClinicalCase',
         'coverage': kid_coverage*school_age_scalar,
         'seek': 1,
         'rate': 0.3},
        {'agemin': 15,
         'agemax': 120,
         'trigger': 'NewClinicalCase',
         'coverage': kid_coverage*adult_scalar,
         'seek': 1,
         'rate': 0.3},
        {'agemin': 0,
         'agemax': 120,
         'trigger': 'NewSevereCase',
         'coverage': max([0.8, kid_coverage]),
         'seek': 1,
         'rate': 0.2},
    ]

    add_health_seeking(cb, start_day=start_day, targets=coverage_dict, drug=["Artemether", "Lumefantrine"],
                       nodeIDs=nodeIDs)
    return {
        'child_coverage' : kid_coverage,
        'adult_coverage' : kid_coverage*adult_scalar
    }


def add_health_seeking_from_df(cb, start_day, hs_df, adult_scalar=0.6) :

    for r, row in hs_df.iterrows() :
        health_seeking(cb, start_day=start_day, kid_coverage=row['child_coverage'],
                       nodeIDs=[int(row['node'])], adult_scalar=adult_scalar)
    return {
        'node_%d_hs' % row['node'] : row['child_coverage'] for r, row in hs_df.iterrows()
    }


def read_in_habitat_from_baseline_calib(habs_to_run_fname, numsamples) :

    adf = pd.read_csv(os.path.join(projectpath, 'simulation_output', 'baseline', habs_to_run_fname))
    df = pd.DataFrame()
    for node, ndf in adf.groupby('node') :
        sdf = copy.copy(ndf.sort_values(by='diff').head(numsamples))
        sdf = sdf.reset_index()
        sdf['rank'] = sdf.index
        df = pd.concat([df, sdf])
    df['NodeID'] = df['node']
    df['habitat_scale'] = df['x_Temporary_Larval_Habitat']

    return df


def add_special_migration(cb):
    # Set Is_Moving = False
    # Set Dont_Allow_Duplicates = False
    mig_events = pd.read_csv(os.path.join('%s' % projectpath, 'simulation_inputs', 'migration',
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
                                   "Duration_Before_Leaving_Min": 15,
                                   "Duration_Before_Leaving_Max": 112}

        add_migration_event(cb,
                            start_day=start,
                            nodesfrom=[node_from],
                            nodeto=node_to,
                            coverage=1.0,
                            duration_at_node=duration_at_node,
                            duration_before_leaving=duration_before_leaving,
                            ind_property_restrictions=[{"Ledger": ledger}],
                            repetitions=1)