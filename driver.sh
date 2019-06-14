input=inputs/inputs.yml
data=/home/villena/bitbucket/distribution_tariff_simulator/datfiles
output=/home/villena/bitbucket/distribution_tariff_simulator/results

python -m simulator -i $input -d $data -o $output
