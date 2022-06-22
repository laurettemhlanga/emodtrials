import os
import pandas as pd
import json
import requests
from dtk.tools.demographics.DemographicsGeneratorConcern import WorldBankBirthRateConcern, EquilibriumAgeDistributionConcern, DefaultIndividualAttributesConcern
from dtk.tools.demographics.DemographicsGenerator import DemographicsGenerator
from dtk.tools.climate.ClimateGenerator import ClimateGenerator
from simtools.SetupParser import SetupParser
import sys
sys.path.append('../')
from load_paths import load_box_paths

# home_path, data_path = load_box_paths()

location = "Ghana"
dhs_year = "2003"
input = "all"

user_path = os.path.expanduser("~")
# home_path = os.path.join(user_path, 'Documents', 'urban_malaria', "github_clones" )
# data_path = os.path.join(home_path, 'emodtrials', 'input')
# project_path = os.path.join(data_path, 'Ghana')


if os.name == "posix":
    inputs_path = os.path.join(data_path, 'simulation_inputs')
else:
    home_path = os.path.join(user_path, 'Documents', 'urban_malaria', "github_clones", "emodtrials")

# choice of state to produce the simulation
    inputs_path = os.path.join(home_path, 'input', 'demographics', 'Ghana')

def generate_demographics(demo_df, hfca, demo_fname, use_DHS_birth_rates=False) :
    if not SetupParser.initialized:
        SetupParser.init('HPC')

    demo_df = demo_df.loc[demo_df['Village'] == hfca]

    br_concern = WorldBankBirthRateConcern(country="Ghana", birthrate_year=2016)
# my name is laurette
    chain = [
        DefaultIndividualAttributesConcern(),
        br_concern,
        EquilibriumAgeDistributionConcern(default_birth_rate=br_concern.default_birth_rate),
    ]

    current = DemographicsGenerator.from_dataframe(demo_df,
                                                   population_column_name='population',
                                                   latitude_column_name='lat',
                                                   longitude_column_name='lon',
                                                   node_id_from_lat_long=False,
                                                   concerns=chain,
                                                   load_other_columns_as_attributes=True,
                                                   include_columns=['Village', 'Village']
                                                   ) #computes both daily rate and annual rate here https://github.com/InstituteforDiseaseModeling/dtk-tools/blob/master/dtk/tools/demographics/DemographicsGeneratorConcern.py#L669
   # current['Nodes'][0]['Village'] = 1
    with open(demo_fname, 'w') as fout :
        json.dump(current, fout, sort_keys=True,indent=4, separators=(',', ': '))


def generate_climate(demo_fname, hfca) :
# climate is generated by assessing IDM climate files on COMPS

    cg = ClimateGenerator(demographics_file_path=demo_fname, work_order_path='./wo.json',
                          climate_files_output_path=os.path.join(inputs_path, hfca),
                          climate_project='IDM-Ghana',
                          start_year='2016', num_years='1')
    cg.generate_climate_files()


if __name__ == '__main__' :

    master_csv = os.path.join(inputs_path, 'my_node.csv')

    df = pd.read_csv(master_csv, encoding='latin')
    df['Village'] = df['Village'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    if input == "all":
        for hfca in df['Village'].unique() :
            print(hfca)
            if not os.path.exists(os.path.join(inputs_path, hfca)):
                os.makedirs(os.path.join(inputs_path, hfca))
            demo_fname = os.path.join(inputs_path, hfca, '%s_demographics.json' % hfca)
            generate_demographics(df, hfca, demo_fname, True)

            if os.path.exists(os.path.join(inputs_path, hfca,  '%s_rainfall_daily_2016.bin' % hfca)) :
                continue
            generate_climate(demo_fname, hfca)

        #use this to change the names of the climate files
            for tag in ['air_temperature', 'rainfall', 'relative_humidity'] :
                os.replace(os.path.join(inputs_path, hfca, 'Ghana_30arcsec_%s_daily.bin' % tag),
                       os.path.join(inputs_path, hfca, '%s_%s_daily_2016.bin' % (hfca, tag)))
                os.replace(os.path.join(inputs_path, hfca, 'Ghana_30arcsec_%s_daily.bin.json' % tag),
                       os.path.join(inputs_path, hfca, '%s_%s_daily_2016.bin.json' % (hfca, tag)))
                my_file = os.path.join(inputs_path, hfca, 'Ghana_2.5arcmin_demographics.json')
                if os.path.exists(os.path.join(inputs_path, hfca, 'Ghana_2.5arcmin_demographics.json')):
                    os.remove(os.path.join(inputs_path, hfca, 'Ghana_2.5arcmin_demographics.json'))

    else:
        for hfca in df['Village'].unique():
            print(hfca)
            if not os.path.exists(os.path.join(inputs_path, hfca)):
                os.makedirs(os.path.join(inputs_path, hfca))
            demo_fname = os.path.join(inputs_path, hfca, '%s_demographics_%s.json' % (hfca, dhs_year))
            generate_demographics(df, hfca, demo_fname, True)

# jgerardin,
# wqn45kya