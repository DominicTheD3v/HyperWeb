from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Existing route for getting VM IDs
@app.route('/api/vms/ids', methods=['GET'])
def get_vms():
    try:
        # Run PowerShell to get VM Ids
        result = subprocess.run(
            ['powershell', '-Command', 'Get-VM | Select-Object -ExpandProperty Id'],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            return jsonify({'error': 'Failed to retrieve VM IDs', 'details': result.stderr}), 500

        # Extract VM IDs
        vm_ids = result.stdout.strip().split('\n')
        vm_ids = [vm_id for vm_id in vm_ids if vm_id]

        return jsonify({'vm_ids': vm_ids[2:]})  # Skipping first two entries

    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# Map numeric state values to human-readable states
state_mapping = {
    2: "Running",  # Assuming 1 means "Running"
    3: "Off",      # Assuming 2 means "Off"
    1: "Paused",   # Assuming 3 means "Paused"
    # Add more mappings as needed...
}

@app.route('/api/vms/details', methods=['POST'])
def get_vms_details():
    try:
        # Get the list of VM IDs from the request body
        vm_ids = request.json.get('vm_ids')

        if not vm_ids or not isinstance(vm_ids, list):
            return jsonify({'error': 'Invalid or missing vm_ids array'}), 400

        # List to store VM details
        vm_details_list = []

        for vm_id in vm_ids:
            try:
                # Run PowerShell command to get the VM details for each ID
                command = (
                    f"Get-VM -Id '{vm_id}' | "
                    "Select-Object Name, @{Name='IP';Expression={(Get-VMNetworkAdapter -VMName (Get-VM -Id '{vm_id}').Name).IPAddress}}, "
                    "MemoryAssigned, ProcessorCount, State"
                )

                result = subprocess.run(
                    ['powershell', '-Command', command],
                    capture_output=True, text=True
                )

                if result.returncode != 0:
                    raise Exception(f"Failed to retrieve details for VM {vm_id}: {result.stderr}")

                # Parse the output and handle the case where Name might be missing
                vm_details = result.stdout.strip().split('\n')

                if not vm_details or len(vm_details) < 5:
                    continue  # If no details found for this VM or not enough data, skip

                # Extract values from the command output
                vm_name = vm_details[0].split(":")[1].strip() if len(vm_details) > 0 else "Unknown"
                vm_ip = vm_details[1].split(":")[1].strip() if len(vm_details) > 1 else "N/A"
                vm_ram = vm_details[2].split(":")[1].strip() if len(vm_details) > 2 else "Unknown"
                vm_cpu = vm_details[3].split(":")[1].strip() if len(vm_details) > 3 else "Unknown"
                state_label = vm_details[4].split(":")[1].strip() if len(vm_details) > 4 else "Unknown"  # Default to 0 if state is missing

                vm_info = {
                    'id': vm_id,
                    'name': vm_name,
                    'ip': vm_ip,
                    'ram': vm_ram,
                    'cpu': vm_cpu,
                    'state': state_label
                }

                vm_details_list.append(vm_info)

            except Exception as e:
                return jsonify({'error': f"Error processing VM ID {vm_id}", 'details': str(e)}), 500

        return jsonify(vm_details_list)

    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
