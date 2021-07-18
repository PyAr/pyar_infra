import subprocess
import json
from time import sleep


POD_NAME = 'staging-wiki-pyar-wiki-8c9646486-5jglf'
SLEEP_TIME = 2

data = {
	'memory': [],
	'cpu': [],
}


while True:
	kubectl_output = subprocess.check_output(['kubectl', 'top', 'pod', POD_NAME]).decode('utf-8')
	header, content, _ = kubectl_output.split('\n')
	content = content.strip()
	if not content:
		raise Exception("Invalid POD name")

	pod_name, cpu, memory = content.split()
	data['memory'].append(memory)
	data['cpu'].append(cpu)
	print(f'{pod_name} - {cpu} - {memory}')
	with open('output.json', 'w') as output_file:
		output_file.write(json.dumps(data))
	sleep(SLEEP_TIME)