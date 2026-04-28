import React, { useState } from 'react';
import { Upload, AlertCircle, CheckCircle, FileText } from 'lucide-react';
import { uploadDataFile, syncSmsData } from '../services/api';

const DataSyncPanel = ({ onSyncComplete, onDataReceived }) => {
  const [loading, setLoading] = useState(false);
  const [syncMessage, setSyncMessage] = useState('');
  const [syncData, setSyncData] = useState(null);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('upload');
  const [smsInput, setSmsInput] = useState('');

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError('');
    setSyncMessage('Processing your file...');

    try {
      // Use api.js service that has correct BASE_URL
      const data = await uploadDataFile(file);
      setSyncData(data);
      setSyncMessage(`✓ File processed successfully. Found ${data.summary.length} transactions.`);
      
      if (onDataReceived) {
        onDataReceived(data);
      }
      if (onSyncComplete) {
        onSyncComplete(data);
      }
    } catch (err) {
      setError(err.message);
      setSyncMessage('');
    } finally {
      setLoading(false);
    }
  };

  const handleSMSSync = async () => {
    if (!smsInput.trim()) {
      setError('Please enter at least one SMS message');
      return;
    }

    setLoading(true);
    setError('');
    setSyncMessage('Processing SMS messages...');

    try {
      const messages = smsInput.split('\n').filter(m => m.trim());
      
      // Use api.js service that has correct BASE_URL
      const data = await syncSmsData(messages);
      setSyncData(data);
      setSyncMessage(`✓ SMS processed successfully. Found ${data.summary.length} transactions.`);
      
      if (onDataReceived) {
        onDataReceived(data);
      }
      if (onSyncComplete) {
        onSyncComplete(data);
      }
    } catch (err) {
      setError(err.message);
      setSyncMessage('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center mb-6">
        <Upload className="w-6 h-6 text-blue-600 mr-3" />
        <h2 className="text-2xl font-bold text-gray-800">Data Synchronization</h2>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab('upload')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'upload'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Upload Files
        </button>
        <button
          onClick={() => setActiveTab('sms')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'sms'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          SMS Messages
        </button>
      </div>

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div className="space-y-4">
          <div className="border-2 border-dashed border-blue-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors cursor-pointer"
            onClick={(e) => e.currentTarget.querySelector('input').click()}
          >
            <FileText className="w-12 h-12 text-blue-400 mx-auto mb-2" />
            <p className="text-gray-600 mb-2">
              <span className="font-semibold">Click to upload</span> or drag and drop
            </p>
            <p className="text-sm text-gray-500">CSV or Excel files</p>
            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileUpload}
              disabled={loading}
              className="hidden"
            />
          </div>
        </div>
      )}

      {/* SMS Tab */}
      {activeTab === 'sms' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Paste Bank SMS Messages (one per line)
            </label>
            <textarea
              value={smsInput}
              onChange={(e) => setSmsInput(e.target.value)}
              placeholder="Debit of ₹5,000 credited from Salary..."
              disabled={loading}
              className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>
          <button
            onClick={handleSMSSync}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            {loading ? 'Processing...' : 'Process SMS Messages'}
          </button>
        </div>
      )}

      {/* Status Messages */}
      {syncMessage && (
        <div className="mt-6 flex items-start p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <CheckCircle className="w-5 h-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
          <p className="text-blue-800">{syncMessage}</p>
        </div>
      )}

      {error && (
        <div className="mt-6 flex items-start p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Sync Results Summary */}
      {syncData && (
        <div className="mt-6 space-y-4">
          <h3 className="font-semibold text-lg text-gray-800">Detected Financial Data</h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Monthly Income</p>
              <p className="text-2xl font-bold text-green-700">₹{syncData.detected.monthly_income?.toLocaleString('en-IN') || '0'}</p>
            </div>
            <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Monthly Expenses</p>
              <p className="text-2xl font-bold text-red-700">₹{syncData.detected.monthly_expenses?.toLocaleString('en-IN') || '0'}</p>
            </div>
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Monthly SIP</p>
              <p className="text-2xl font-bold text-blue-700">₹{syncData.detected.monthly_sip?.toLocaleString('en-IN') || '0'}</p>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600">EMI</p>
              <p className="text-2xl font-bold text-purple-700">₹{syncData.detected.emi?.toLocaleString('en-IN') || '0'}</p>
            </div>
            <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Rent</p>
              <p className="text-2xl font-bold text-orange-700">₹{syncData.detected.rent?.toLocaleString('en-IN') || '0'}</p>
            </div>
            <div className="bg-gradient-to-br from-teal-50 to-teal-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Surplus</p>
              <p className="text-2xl font-bold text-teal-700">₹{syncData.detected.surplus?.toLocaleString('en-IN') || '0'}</p>
            </div>
          </div>

          {/* Processing Summary */}
          {syncData.summary?.length > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="font-semibold text-gray-800 mb-2">Processing Summary:</p>
              <ul className="text-sm text-gray-700 space-y-1">
                {syncData.summary.slice(0, 5).map((msg, idx) => (
                  <li key={idx}>• {msg}</li>
                ))}
                {syncData.summary.length > 5 && (
                  <li className="text-gray-500">... and {syncData.summary.length - 5} more transactions</li>
                )}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DataSyncPanel;
