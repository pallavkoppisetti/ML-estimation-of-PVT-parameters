import numpy as np
import pandas as pd
from tqdm import tqdm
import os
import sys

"""SYSTEM PARAMETERS"""
cell_name = sys.argv[-2]
num_inp = int(sys.argv[-1])

"""PROCESS VARIABLES FOR DIFFERENT TECH FILES"""
tech_params = [
    ["16nm_HP", 0.7, 16e-9, 9.5e-10, 9.5e-10, 9.5e-10, 7e-10, 1e-9, 1e-9, 1e-9, 5e-9, 5e-9, 7e+18, 5.5e+18],
    ["22nm_HP", 0.8, 22e-9, 1.05e-9, 1.05e-9, 1.05e-9, 8e-10, 1.1e-9, 1.1e-9, 1.1e-9, 7.2e-9, 7.2e-9, 5.5e+18, 4.4e+18],
    ["22nm_MGK", 0.8, 22e-9, 6.5e-10, 6.5e-10, 6.5e-10, 4e-10, 6.7e-10, 6.7e-10, 6.7e-10, 7.2e-9, 7.2e-9, 1.2e+19, 4.4e+18],
    ["32nm_HP", 0.9, 32e-9, 1.15e-9, 1.15e-9, 1.15e-9, 9e-10, 1.2e-9, 1.2e-9, 1.2e-9, 1e-8, 1e-8, 4.12e+18, 3.07e+18],
    ["32nm_MGK", 0.9, 32e-9, 7.5e-10, 7.5e-10, 7.5e-10, 5e-10, 7.7e-10, 7.7e-10, 7.7e-10, 1e-8, 1.008e-8, 8.7e+18, 3.5e+18],
    ["45nm_HP", 1, 45e-9, 1.25e-9, 1.25e-9, 1.25e-9, 1e-9, 1.3e-9, 1.3e-9, 1.3e-9, 1.4e-8, 1.4e-8, 2.44e+18, 3.44e+18],
    ["45nm_MGK", 1, 45e-9, 9e-10, 9e-10, 9e-10, 6.5e-10, 9.2e-10, 9.2e-10, 9.2e-10, 1.4e-8, 1.4e-8, 6.5e+18, 2.8e+18]
]

"""DISTRIBUTION FUNCTIONS"""
def uniform(low, high):
    unif_val = np.random.uniform(low, high)
    return unif_val

def monte_carlo(mean):
    std = mean / 30
    mc_val = np.random.normal(mean, std)
    return mc_val

"""INPUT FILE NAMES"""
leakage_netlist_file = f"./leakage/netlists/HS65_GH_{cell_name}.net"
delay_netlist_file = f"./delay/netlists/HS65_GH_{cell_name}.net"
mod_netlist_file = f"./temp_mod.net"
output_file = "out.txt"

"""TRUTH TABLE"""
def truth_table(n):
    table = []
    for i in range(2**n):
        line = [i//2**j%2 for j in reversed(range(n))]
        table.append(line)
    return table

table = truth_table(num_inp)

"""REPLACE CONTENT IN PARENT FILES"""
def replace_content(content):
    content_mod = content.replace(".include", f".include ./model/{tech}.pm")

    content_mod = content_mod.replace("set temp", f"set temp = {temp}")
    content_mod = content_mod.replace(".param pvdd", f".param pvdd = {pvdd}")
    content_mod = content_mod.replace(".param cqload", f".param cqload = {cqload}")

    content_mod = content_mod.replace(".param lmin", f".param lmin = {lmin}")
    content_mod = content_mod.replace(".param wmin", f".param wmin = {wmin}")

    content_mod = content_mod.replace(f".csparam toxe_n", f".csparam toxe_n = {toxe_n}")
    content_mod = content_mod.replace(f".csparam toxm_n", f".csparam toxm_n = {toxm_n}")
    content_mod = content_mod.replace(f".csparam toxref_n", f".csparam toxref_n = {toxref_n}")
    content_mod = content_mod.replace(f".csparam toxp_par", f".csparam toxp_par = {toxp_par}")
    content_mod = content_mod.replace(f".csparam toxe_p", f".csparam toxe_p = {toxe_p}")
    content_mod = content_mod.replace(f".csparam toxm_p", f".csparam toxm_p = {toxm_p}")
    content_mod = content_mod.replace(f".csparam toxref_p", f".csparam toxref_p = {toxref_p}")
    content_mod = content_mod.replace(f".csparam xj_n", f".csparam xj_n = {xj_n}")
    content_mod = content_mod.replace(f".csparam xj_p", f".csparam xj_p = {xj_p}")
    content_mod = content_mod.replace(f".csparam ndep_p", f".csparam ndep_p = {ndep_p}")
    content_mod = content_mod.replace(f".csparam ndep_n", f".csparam ndep_n = {ndep_n}")
    return content_mod

"""LOOP FOR EACH TECH FILE"""
for data in tech_params:
    tech, pvdd_nom, wmin_nom, toxe_n_nom, toxm_n_nom, toxref_n_nom, toxp_par_nom, toxe_p_nom, toxm_p_nom, toxref_p_nom, xj_n_nom, xj_p_nom, ndep_p_nom, ndep_n_nom = data

    """NOMINAL VALUES"""
    temp_low, temp_high = -55, 125
    cqload_low, cqload_high = 0.01e-15, 5e-15
    pvdd_low, pvdd_high = pvdd_nom * 0.9, pvdd_nom * 1.1

    lmin_nom = wmin_nom
    lmin_mean = lmin_nom + 2e-9
    wmin_mean = wmin_nom + 209e-9

    """OUTPUT FILE NAMES"""
    csv_file_leakage = f"./leakage/data/HS65_GH_{cell_name}_{tech}.csv"
    csv_file_delay = f"./delay/data/HS65_GH_{cell_name}_{tech}.csv"

    """STORE DATASETS"""
    data_list_leakage = []
    data_list_delay = []

    for i in tqdm(range(30000), ncols=100, desc=f"Cell: {cell_name}, Tech: {tech}"):
        """GET RANDOM PVT VALUES"""
        temp = uniform(temp_low, temp_high)
        pvdd = uniform(pvdd_low, pvdd_high)
        cqload = uniform(cqload_low, cqload_high)

        lmin = monte_carlo(lmin_mean)
        wmin = monte_carlo(wmin_mean)

        toxe_n = monte_carlo(toxe_n_nom)
        toxm_n = monte_carlo(toxm_n_nom)
        toxref_n = monte_carlo(toxref_n_nom)
        toxp_par = monte_carlo(toxp_par_nom)
        toxe_p = monte_carlo(toxe_p_nom)
        toxm_p = monte_carlo(toxm_p_nom)
        toxref_p = monte_carlo(toxref_p_nom)
        xj_n = monte_carlo(xj_n_nom)
        xj_p = monte_carlo(xj_p_nom)
        ndep_p = monte_carlo(ndep_p_nom)
        ndep_n = monte_carlo(ndep_n_nom)

        """GENERATING LEAKAGE DATA"""
        with open(leakage_netlist_file, "r") as f:
            content = f.read()
            content_mod = replace_content(content)
        
        with open(mod_netlist_file, "w") as f:
            f.write(content_mod)
        
        os.system(f"ngspice -b {mod_netlist_file} > /dev/null")

        with open(output_file, "r") as f:
            output_text = f.read().splitlines()
            output_text = [line.split()[-1] for line in output_text]
            output_text = [word for word in output_text if 'e' in word]
            
            P_leaks = []
            for ele in output_text:
                try:
                    P_leaks.append(float(ele))
                except ValueError:
                    continue

            for i, comb in enumerate(table):
                data_elem = comb + [temp, pvdd, cqload, lmin, wmin, toxe_n, toxm_n, toxref_n, toxe_p, toxm_p, toxref_p, toxp_par, xj_n, xj_p, ndep_n, ndep_p, P_leaks[i]]
                data_list_leakage.append(data_elem)
        
        """GENERATING DELAY DATA"""
        with open(delay_netlist_file, "r") as f:
            content = f.read()
            content_mod = replace_content(content)
        
        with open(mod_netlist_file, "w") as f:
            f.write(content_mod)
        
        os.system(f"ngspice -b {mod_netlist_file} > /dev/null")

        with open(output_file, "r") as f:
            output_text = f.read().split()
            delay_lh = [float(output_text[3*k+2]) for k in range(num_inp)]
            delay_hl = [float(output_text[-3*k-1]) for k in range(num_inp)]
            delay_hl = delay_hl[::-1]

            data_elem = [temp, pvdd, cqload, lmin, wmin, toxe_n, toxm_n, toxref_n, toxe_p, toxm_p, toxref_p, toxp_par, xj_n, xj_p, ndep_n, ndep_p] + delay_lh + delay_hl
            data_list_delay.append(data_elem)
    
    """LEAKAGE DATASET"""
    columns_leakage = [f"Vin_{chr(i + ord('A'))}" for i in range(num_inp)] + ["temp", "pvdd", "cqload", "lmin", "wmin", "toxe_n", "toxm_n", "toxref_n", "toxe_p", "toxm_p", "toxref_p", "toxp_par", "xj_n", "xj_p", "ndep_n", "ndep_p", "P_leak"]
    
    data_df = pd.DataFrame(data_list_leakage, columns=columns_leakage)
    data_df.to_csv(csv_file_leakage)

    """DELAY DATASET"""
    columns_delay = ["temp", "pvdd", "cqload", "lmin", "wmin", "toxe_n", "toxm_n", "toxref_n", "toxe_p", "toxm_p", "toxref_p", "toxp_par", "xj_n", "xj_p", "ndep_n", "ndep_p"] + [f"delay_lh_node{chr(i+ord('a'))}" for i in range(num_inp)] + [f"delay_hl_node{chr(i+ord('a'))}" for i in range(num_inp)]
    
    data_df = pd.DataFrame(data_list_delay, columns=columns_delay)
    data_df.to_csv(csv_file_delay)

"""REMOVE EXTRA FILES"""
os.remove(mod_netlist_file)
os.remove(output_file)
