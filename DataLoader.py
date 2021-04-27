import pandas as pd
import warnings
import os
import pickle as pkl

"""
Author: Chris Magnano
02/15/21

Methods and intermediate state for loading data and putting it into pandas tables for use by pathway reconstruction algorithms. We'll probably want to eventually roll these up as a part of another class.
"""

class DataLoader:

    NODE_ID = "NODEID"
    warning_threshold = 0.05 #Threshold for scarcity of columns to warn user

    def __init__(self, dataset_dict):
        self.label = None
        self.interactome = None
        self.node_table = None
        self.edge_table = None
        self.node_set = set()
        self.other_files = []
        self.load_files_from_config(dataset_dict)
        return

    def to_file(self, file_name):
        '''
        Saves dataset object to pickle file
        '''
        with open(file_name, "wb") as f:
            pkl.dump(self, f)
        return

    @classmethod
    def from_file(cls, file_name):
        '''
        Loads dataset object from a pickle file.
        Usage: dataset = Dataset.from_file(pickle_file)
        '''
        with open(file_name, "rb") as f:
            return pkl.load(f)
        return

    # TODO when loading the config file, support a list of datasets
    def load_files_from_config(self, dataset_dict):
        '''
        Loads data files from config, which is assumed to be a nested dictionary
        from a loaded yaml config file with the fields in Config-Files/config.yaml.
        Populates node_table, edge_table, and interactome.

        node_table is a single merged pandas table.

        When loading data files, files of only a single column with node
        identifiers are assumed to be a binary feature where all listed nodes are
        True.

        We might want to eventually add an additional "algs" argument so only
        subsets of the entire config file are loaded, alternatively this could
        be handled outside this class.

        returns: none
        '''

        self.label = dataset_dict["label"]

        #Get file paths from config
        # TODO support multiple edge files
        interactome_loc = dataset_dict["edge_files"][0]
        node_data_files = dataset_dict["node_files"]
        edge_data_files = [""] #Currently None
        data_loc = dataset_dict["data_dir"]

        #Load everything as pandas tables
        self.interactome = pd.read_table(os.path.join(data_loc,interactome_loc), names = ["Interactor1","Interactor2","Weight"])
        node_set = set(self.interactome.Interactor1.unique())
        node_set = node_set.union(set(self.interactome.Interactor2.unique()))

        #Load generic node tables
        self.node_table = pd.DataFrame(node_set, columns=[self.NODE_ID])
        for node_file in node_data_files:
            single_node_table = pd.read_table(os.path.join(data_loc,node_file))
            #If we have only 1 column, assume this is an indicator variable
            if len(single_node_table.columns)==1:
                single_node_table = pd.read_table(os.path.join(data_loc,node_file),header=None)
                single_node_table.columns = [self.NODE_ID]
                new_col_name = node_file.split(".")[0]
                single_node_table[new_col_name] = True

            self.node_table = self.node_table.merge(single_node_table, how="left", on=self.NODE_ID, suffixes=("", "_DROP")).filter(regex="^(?!.*DROP)")
        self.other_files = dataset_dict["other_files"]
        return

    def request_node_columns(self, col_names):
        '''
        returns: A table containing the requested column names and node IDs
        for all nodes with at least 1 of the requested values being non-empty
        '''
        col_names.append(self.NODE_ID)
        filtered_table = self.node_table[col_names]
        filtered_table = filtered_table.dropna(axis=0, how='all',subset=filtered_table.columns.difference([self.NODE_ID]))
        percent_hit = (float(len(filtered_table))/len(self.node_table))*100
        if percent_hit <= self.warning_threshold*100:
            warnings.warn("Only %0.2f of data had one or more of the following columns filled:"%(percent_hit) + str(col_names))
        return filtered_table

    def request_edge_columns(self, col_names):
        return None

    def get_other_files(self):
        return self.other_files.copy()

    def get_interactome(self):
        return self.interactome.copy()
