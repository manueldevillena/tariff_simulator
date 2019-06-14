import argparse
import time

from simulator import read_inputs, driver_dynamics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parses the inputs for the module to run.")
    parser.add_argument('-i', '--input', dest='input', required=True, type=str, help="Input YML file.")
    parser.add_argument('-d', '--data', dest='data', required=True, type=str, help='Path to prosumers data.')
    parser.add_argument('-o', '--output', dest='output', required=True, type=str, help="Output folder.")
    args = parser.parse_args()

    inputs = read_inputs(inputs=args.input)

    inputs['output_path'] = args.output
    
    start = time.time() / 60

    print('\n \nNew Simulation with the following prices for volume, capacity, and fixed fees:')
    
    driver_dynamics(inputs, data=args.data)

    end = time.time() / 60

    print('The simulation took ' + str((end - start)) + ' minutes.')
