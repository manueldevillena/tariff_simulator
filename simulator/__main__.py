import argparse
import time

from simulator import read_inputs, driver_dynamics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parses the inputs for the module to run.")
    parser.add_argument('-i', '--input', dest='input', required=True, type=str, help="Input YML file.")
    parser.add_argument('-o', '--output', dest='output', required=True, type=str, help="Output folder.")
    args = parser.parse_args()

    inputs = read_inputs(inputs=args.input)

    volume_share = inputs['volume_share']
    capacity_share = inputs['capacity_share']
    fixed_share = inputs['fixed_share']

    start = time.time() / 60

    for i in range(len(volume_share)):
        inputs['volume_share'] = volume_share[i]
        inputs['capacity_share'] = capacity_share[i]
        inputs['fixed_share'] = fixed_share[i]

        print('\n \nNew Simulation with the following prices for volume, capacity, and fixed fees:')
        driver_dynamics(inputs, outputs=args.output)

    end = time.time()/60
    print('The simulation took ' + str((end - start)) + ' minutes.')