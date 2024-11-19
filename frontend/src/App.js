import React, { useEffect, useState } from 'react';
import axios from 'axios';

const App = () => {
  const [vms, setVms] = useState([]);
  const [vmDetails, setVmDetails] = useState([]);
  const [loading, setLoading] = useState(true);

  // Function to get the status color based on the state
  const getStatusColor = (state) => {
    switch (state) {
      case 'Running':
        return 'bg-green-500'; // Green for Running
      case 'Off':
        return 'bg-red-500';   // Red for Off
      case 'Paused':
        return 'bg-yellow-500';// Yellow for Paused
      default:
        return 'bg-gray-500';  // Gray for unknown state
    }
  };

  // Fetch VM IDs
  useEffect(() => {
    axios
      .get('http://home-lab:5000/api/vms/ids')
      .then((response) => {
        setVms(response.data.vm_ids);
        setLoading(false);
      })
      .catch((error) => {
        console.error('There was an error fetching the VM data!', error);
        setLoading(false);
      });
  }, []);

  // Fetch VM details based on the IDs
  useEffect(() => {
    if (vms.length > 0) {
      const fetchVmDetails = async () => {
        try {
          const response = await axios.post('http://home-lab:5000/api/vms/details', { vm_ids: vms });
          setVmDetails(response.data); // Set the VM details after fetching
        } catch (error) {
          console.error('Error fetching VM details:', error);
        }
      };

      fetchVmDetails(); // Call the function to fetch details
    }
  }, [vms]); // Only run this effect when vms are available

  if (loading) {
    return <div>Loading VM IDs...</div>;
  }

  return (
    <div className="p-5">
      <h1 className="text-3xl font-bold">Hyper-V Management</h1>
      <div className="mt-5">
        <h2 className="text-2xl font-semibold">Virtual Machines</h2>
        <div className="space-y-4 mt-4">
          {vmDetails.length > 0 ? (
            vmDetails.map((vm) => (
              <div key={vm.id} className="p-4 border rounded-lg shadow-md flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span
                    className={`w-4 h-4 rounded-full ${getStatusColor(vm.state)}`}
                  ></span>
                  <span className="font-semibold">{vm.name}</span>
                </div>
                <div>
                  <p className="text-gray-500">IP: {vm.ip}</p>
                  <p className="text-gray-500">RAM: {vm.ram}</p>
                  <p className="text-gray-500">CPU: {vm.cpu}</p>
                  <p className="text-gray-500">Status: {vm.state}</p>
                </div>
              </div>
            ))
          ) : (
            <div>No VM details available</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
