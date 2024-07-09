import numpy as np
import pandas as pd
from tqdm import tqdm
import os
import sys

"""SYSTEM PARAMETERS"""
num_trials = int(sys.argv[-1])

"""NOMINAL VALUES"""
tech_params = [0.8, 22e-9, 1.05e-9, 1.05e-9, 1.05e-9, 8e-10, 1.1e-9, 1.1e-9, 1.1e-9, 7.2e-9, 7.2e-9, 5.5e+18, 4.4e+18]

"""DISTRIBUTION FUNCTIONS"""
def uniform(low, high):
    unif_val = np.random.uniform(low, high)
    return unif_val

def monte_carlo(mean):
    std = mean / 30
    mc_val = np.random.normal(mean, std)
    return mc_val

"""FILE NAMES"""
netlist_file = f"./c499/C499.net"
mod_netlist_file = f"./temp_mod.net"
output_file = "out.txt"

"""RANDOM PARAMETERS"""

pvdd_nom, wmin_nom, toxe_n_nom, toxm_n_nom, toxref_n_nom, toxp_par_nom, toxe_p_nom, toxm_p_nom, toxref_p_nom, xj_n_nom, xj_p_nom, ndep_p_nom, ndep_n_nom = tech_params

temp_low, temp_high = -55, 125
cqload_low, cqload_high = 0.01e-15, 5e-15
pvdd_low, pvdd_high = pvdd_nom * 0.9, pvdd_nom * 1.1

lmin_nom = wmin_nom
lmin_mean = lmin_nom + 2e-9
wmin_mean = wmin_nom + 209e-9

"""REPLACE SOURCES"""
def replace_sources(content):
    source_names = ["Vin1", "Vin5", "Vin9", "Vin13", "Vin17", "Vin21", "Vin25", "Vin29", "Vin33", "Vin37", "Vin41", "Vin45", "Vin49", "Vin53", "Vin57", "Vin61", "Vin65", "Vin69", "Vin73", "Vin77", "Vin81", "Vin85", "Vin89", "Vin93", "Vin97", "Vin101", "Vin105", "Vin109", "Vin113", "Vin117", "Vin121", "Vin125", "Vin129", "Vin130", "Vin131", "Vin132", "Vin133", "Vin134", "Vin135", "Vin136", "Vin137"]

    node_names = ["nodeIN1", "nodeIN5", "nodeIN9", "nodeIN13", "nodeIN17", "nodeIN21", "nodeIN25", "nodeIN29", "nodeIN33", "nodeIN37", "nodeIN41", "nodeIN45", "nodeIN49", "nodeIN53", "nodeIN57", "nodeIN61", "nodeIN65", "nodeIN69", "nodeIN73", "nodeIN77", "nodeIN81", "nodeIN85", "nodeIN89", "nodeIN93", "nodeIN97", "nodeIN101", "nodeIN105", "nodeIN109", "nodeIN113", "nodeIN117", "nodeIN121", "nodeIN125", "nodeIN129", "nodeIN130", "nodeIN131", "nodeIN132", "nodeIN133", "nodeIN134", "nodeIN135", "nodeIN136", "nodeIN137"]

    source_voltages = np.random.uniform(0, 1, 41)
    source_voltages = (source_voltages > 0.5).astype(int)

    for s, n, v in zip(source_names, node_names, source_voltages):
        content = content.replace(f"{s} {n} gnd 1", f"{s} {n} gnd {v}")
    
    return source_voltages, content

def replace_params(content):
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

    params = [temp, pvdd, cqload, lmin, wmin, toxe_n, toxm_n, toxref_n, toxp_par, toxe_p, toxm_p, toxref_p, xj_n, xj_p, ndep_p, ndep_n]

    content = content.replace("set temp", f"set temp = {temp}")
    content = content.replace(".param pvdd", f".param pvdd = {pvdd}")
    content = content.replace(".param cqload", f".param cqload = {cqload}")

    content = content.replace(".param lmin", f".param lmin = {lmin}")
    content = content.replace(".param wmin", f".param wmin = {wmin}")

    content = content.replace(f".csparam toxe_n", f".csparam toxe_n = {toxe_n}")
    content = content.replace(f".csparam toxm_n", f".csparam toxm_n = {toxm_n}")
    content = content.replace(f".csparam toxref_n", f".csparam toxref_n = {toxref_n}")
    content = content.replace(f".csparam toxp_par", f".csparam toxp_par = {toxp_par}")
    content = content.replace(f".csparam toxe_p", f".csparam toxe_p = {toxe_p}")
    content = content.replace(f".csparam toxm_p", f".csparam toxm_p = {toxm_p}")
    content = content.replace(f".csparam toxref_p", f".csparam toxref_p = {toxref_p}")
    content = content.replace(f".csparam xj_n", f".csparam xj_n = {xj_n}")
    content = content.replace(f".csparam xj_p", f".csparam xj_p = {xj_p}")
    content = content.replace(f".csparam ndep_p", f".csparam ndep_p = {ndep_p}")
    content = content.replace(f".csparam ndep_n", f".csparam ndep_n = {ndep_n}")

    return params, content


data = []

for i in tqdm(range(num_trials), ncols=100, desc="For C499 circuit with 22nm_HP tech:"):

    """REPLACE CONTENT"""
    with open(netlist_file, "r") as f:
        content = f.read()
        source_vals, content = replace_sources(content)
        params, content = replace_params(content)

    with open(mod_netlist_file, "w") as f:
        f.write(content)

    """RUN FILE"""
    os.system(f"ngspice -b {mod_netlist_file} > /dev/null")

    with open(output_file, "r") as f:
        P_leak = f.read().split()[-1]
        data_elem = list(source_vals) + params + [P_leak, ]
        data.append(data_elem)

csv_file = "./c499/samples.csv"

columns = [f"V{n + 1}" for n in range(41)] + ["temp", "pvdd", "cqload", "lmin", "wmin", "toxe_n", "toxm_n", "toxref_n", "toxe_p", "toxm_p", "toxref_p", "toxp_par", "xj_n", "xj_p", "ndep_n", "ndep_p", "P_leak"]

data_df = pd.DataFrame(data, columns=columns)
data_df.to_csv(csv_file)

os.remove(mod_netlist_file)
os.remove(output_file)