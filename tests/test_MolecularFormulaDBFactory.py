__author__ = "Yuri E. Corilo"
__date__ = "Jul 22, 2019"


import pickle

from pathlib import Path
import time, sys, os, pytest
sys.path.append(".")


from corems.encapsulation.constant import Labels
from corems.molecular_id.factory.MolecularLookupTable import  MolecularCombinations
from corems.molecular_id.factory.molecularSQL import MolForm_SQL
from corems.molecular_id.factory.molecularMongo import MolForm_Mongo
from corems.molecular_id.input.nistMSI import ReadNistMSI
from corems.encapsulation.settings.processingSetting import MolecularSearchSettings


def create_lookup_dict():
    
    MolecularCombinations().runworker(MolecularSearchSettings)

def xtest_query_mongo():
    
    #from pymongo import MongoClient
    #import pymongo
    #client = MongoClient("mongodb://corems-client:esmlpnnl2019@localhost:27017/corems")
    #db = client.corems.drop_collection('molform')
    with MolForm_Mongo() as mongo_db:
       formula = mongo_db.get_all()
       print(formula[0])
       print(pickle.loads(formula[0]['mol_formula']).mz_theor)

def test_nist_to_sql():

    file_location = Path.cwd() / "tests/tests_data/gcms/" / "PNNLMetV20191015.MSL"

    sqlLite_obj = ReadNistMSI(file_location).get_sqlLite_obj()

    sqlLite_obj.query_min_max_ri((1637.30, 1638.30)) 
    sqlLite_obj.query_min_max_rt((17.111, 18.111))            
    sqlLite_obj.query_min_max_ri_and_rt((1637.30, 1638.30),(17.111, 18.111)) 

def test_query_sql():

    with MolForm_SQL() as sqldb:
        #sqldb.clear_data()

        ion_type = Labels.protonated_de_ion
        print('ion_type', ion_type)
        classe = 'O8'
        nominal_mz = 501
        print('total mol formulas found: ', len(sqldb.get_entries(classe, ion_type, nominal_mz, MolecularSearchSettings)))

def test_molecular_lookup_db():    
    
    #margin_error needs to be optimized by the data rp and sn
    #min_mz,max_mz  needs to be optimized by the data
    MolecularSearchSettings.min_mz = 100
    MolecularSearchSettings.max_mz = 800
    # C, H, N, O, S and P atoms are ALWAYS needed in the dictionary
    #the defaults values are defined at the encapsulation MolecularSpaceTableSetting    
    MolecularSearchSettings.usedAtoms['C'] = (1,90)
    MolecularSearchSettings.usedAtoms['H'] = (4,200)
    MolecularSearchSettings.usedAtoms['O'] = (1,8)
    MolecularSearchSettings.usedAtoms['N'] = (0,0)
    MolecularSearchSettings.usedAtoms['S'] = (0,0)

    MolecularSearchSettings.isRadical = True
    MolecularSearchSettings.isProtonated = False
    #some atoms has more than one covalence state and the most commun will be used
    # adduct atoms needs covalence 0
    MolecularSearchSettings.usedAtoms['Cl'] = (0,0)
    valence_one = 1
    
    # if you want to specify it in needs to be changed here
    # otherwise it will use the lowest covalence, PS needs insure propagation to isotopologues
    MolecularSearchSettings.used_atom_valences['Cl'] =  valence_one
    
    time0 = time.time()
    create_lookup_dict()
    time1 = time.time()
    print("create the molecular lookup table took %.2f seconds", time1-time0)
    
if __name__ == '__main__':
    
    from corems.encapsulation.settings.io import settings_parsers

    #settings_parsers.load_search_setting_yaml()
    #settings_parsers.load_search_setting_json()
   
    test_query_sql()
    #xtest_query_mongo()
    test_molecular_lookup_db()