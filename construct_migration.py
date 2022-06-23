
import pandas as pd
import json
import numpy as np
import os
import sys

# sys.path.append('../helpers/')
from load_paths import load_box_paths

# requires malaria-toolbox being installed
from input_file_generation.convert_txt_to_bin import convert_txt_to_bin

projectpath, datapath = load_box_paths()
inputs_path = os.path.join(projectpath, 'emodtrials','input')

def generate_all_to_one_migration(outfile_base, id_reference, home_nodeids, to_nodeid, days_between_trips, mig_type):
    # data generation in python ???
    adf = pd.DataFrame({'node1': home_nodeids})
    adf['node2'] = to_nodeid
    adf['rate'] = 1. / days_between_trips
    adf = adf.reindex(columns=['node1', 'node2', 'rate'])
    save_mig_file(outfile_base, id_reference, adf, mig_type)


def generate_all_by_all_migration(outfile_base, id_reference, nodeids, days_between_trips, mig_type, max_neighbors=0):
    adf = pd.DataFrame()
    for node in nodeids:
        to_nodeids = [x for x in nodeids if x != node]
        if max_neighbors > 0:
            to_nodeids = np.random.choice(to_nodeids, max_neighbors, replace=False)
        df = pd.DataFrame({'node2': to_nodeids})
        df['node1'] = node
        df['rate'] = 1. / days_between_trips
        adf = pd.concat([adf, df])

    save_mig_file(outfile_base, id_reference, adf, mig_type)


def save_mig_file(outfile_base, id_reference, df, mig_type):
    df = df.sort_values(by='node1')
    df = df[['node1', 'node2', 'rate']]
    df.to_csv('%s_%s_migration.csv' % (outfile_base, mig_type), index=False, header=False)
    convert_txt_to_bin('%s_%s_Migration.csv' % (outfile_base, mig_type),
                       '%s_%s_Migration.bin' % (outfile_base, mig_type),
                       mig_type='%s_MIGRATION' % mig_type.upper(),
                       id_reference=id_reference)


if __name__ == '__main__':
    inputs_path = load_box_paths()[1]
    master_df = pd.read_csv(os.path.join(inputs_path,  'my_node.csv'))

    input_file_name = 'ghana_nxtek_4node'
    demo_fname = os.path.join(inputs_path, '%s_demographics.json' % input_file_name)

    with open(demo_fname) as fin:
        demo = json.loads(fin.read())

    id_reference = demo['Metadata']['IdReference']

    village_nodes = [1, 2]
    other_node = 3
    allnodes = list(master_df['nodeid'].values)


    outfile_base = os.path.join(inputs_path, 'migration', input_file_name)
    mig_type = 'Regional'
    convert_txt_to_bin('%s_%s_Migration.csv' % (outfile_base, mig_type),
                       '%s_%s_Migration.bin' % (outfile_base, mig_type),
                       mig_type='%s_MIGRATION' % mig_type.upper(),
                       id_reference=id_reference)
    mig_type = 'Local'
    convert_txt_to_bin('%s_Vector_%s_Migration.csv' % (outfile_base, mig_type),
                       '%s_Vector_%s_Migration.bin' % (outfile_base, mig_type),
                       mig_type='%s_MIGRATION' % mig_type.upper(),
                       id_reference=id_reference)

    convert_txt_to_bin('%s_%s_Migration.csv' % (outfile_base, mig_type),
                       '%s_%s_Migration.bin' % (outfile_base, mig_type),
                       mig_type='%s_MIGRATION' % mig_type.upper(),
                       id_reference=id_reference)
