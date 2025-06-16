import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useContracts } from '../contexts/ContractsContext';
import { useAuth } from '../contexts/AuthContext';
import { PlusCircle, FileCode, Clock, CheckCircle, Code, Database, FileText, ArrowRight } from 'lucide-react';

const Dashboard = () => {
  const { currentUser } = useAuth();
  const { listContracts, loading } = useContracts();
  const [contracts, setContracts] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    deployed: 0,
    drafts: 0,
  });

  useEffect(() => {
    const fetchContracts = async () => {
      try {
        const data = await listContracts();
        setContracts(data);
        
        // Calculate stats
        setStats({
          total: data.length,
          deployed: data.filter(contract => contract.deployed_address).length,
          drafts: data.filter(contract => !contract.deployed_address).length,
        });
      } catch (error) {
        console.error('Error fetching contracts:', error);
      }
    };

    fetchContracts();
  }, [listContracts]);

  const getContractTypeIcon = (type) => {
    switch (type) {
      case 'token':
        return <Code className="h-5 w-5 text-blue-600" />;
      case 'nft':
        return <FileText className="h-5 w-5 text-purple-600" />;
      case 'dao':
        return <Database className="h-5 w-5 text-green-600" />;
      default:
        return <FileCode className="h-5 w-5 text-gray-600" />;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(date);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-gray-500">
            Manage your smart contracts and deployments
          </p>
        </div>
        <div className="mt-4 md:mt-0">
          <Link
            to="/create"
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <PlusCircle className="mr-2 h-4 w-4" />
            Create New Contract
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
                <FileCode className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500 truncate">
                  Total Contracts
                </p>
                <p className="mt-1 text-3xl font-semibold text-gray-900">
                  {stats.total}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-100 rounded-md p-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500 truncate">
                  Deployed Contracts
                </p>
                <p className="mt-1 text-3xl font-semibold text-gray-900">
                  {stats.deployed}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-yellow-100 rounded-md p-3">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500 truncate">
                  Draft Contracts
                </p>
                <p className="mt-1 text-3xl font-semibold text-gray-900">
                  {stats.drafts}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Contracts List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div className="px-4 py-5 sm:px-6">
          <h2 className="text-lg leading-6 font-medium text-gray-900">
            Your Contracts
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            List of all your smart contracts
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-48">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : contracts.length === 0 ? (
          <div className="text-center py-12 px-4">
            <FileCode className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No contracts yet
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating a new smart contract.
            </p>
            <div className="mt-6">
              <Link
                to="/create"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <PlusCircle className="mr-2 h-4 w-4" />
                Create New Contract
              </Link>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Contract
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Type
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Created
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Status
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {contracts.map((contract) => (
                  <tr key={contract.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center bg-blue-100 rounded-full">
                          {getContractTypeIcon(contract.contract_type)}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {contract.name}
                          </div>
                          <div className="text-sm text-gray-500 max-w-xs truncate">
                            {contract.description}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        {contract.contract_type.charAt(0).toUpperCase() +
                          contract.contract_type.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(contract.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {contract.deployed_address ? (
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          Deployed
                        </span>
                      ) : (
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                          Draft
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Link
                        to={`/contracts/${contract.id}`}
                        className="text-blue-600 hover:text-blue-900 inline-flex items-center"
                      >
                        View <ArrowRight className="ml-1 h-4 w-4" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Quick Actions
          </h3>
          <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <div className="border rounded-lg p-5 hover:shadow-md transition-shadow">
              <h3 className="text-lg font-medium text-gray-900">
                Browse Templates
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Explore pre-built contract templates for quick deployment.
              </p>
              <div className="mt-4">
                <Link
                  to="/library"
                  className="text-blue-600 hover:text-blue-900 font-medium flex items-center"
                >
                  Go to Library <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </div>
            </div>

            <div className="border rounded-lg p-5 hover:shadow-md transition-shadow">
              <h3 className="text-lg font-medium text-gray-900">
                Create Custom Contract
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Describe your requirements and get AI-generated smart contracts.
              </p>
              <div className="mt-4">
                <Link
                  to="/create"
                  className="text-blue-600 hover:text-blue-900 font-medium flex items-center"
                >
                  Create Contract <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </div>
            </div>

            <div className="border rounded-lg p-5 hover:shadow-md transition-shadow">
              <h3 className="text-lg font-medium text-gray-900">
                Learn Smart Contracts
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Tutorials and guides to help you understand smart contracts.
              </p>
              <div className="mt-4">
                <Link
                  to="/learn"
                  className="text-blue-600 hover:text-blue-900 font-medium flex items-center"
                >
                  View Resources <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;