import React, { useState } from 'react';
import ChatInterface from '../components/chat/ChatInterface';
import FileUpload from '../components/files/FileUpload';
import ConversationHistory from '../components/chat/ConversationHistory';

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'files' | 'history'>('chat');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">AI Memory Assistant</h1>
        <p className="text-gray-600 mt-2">Chat with your documents and memories</p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'chat' as const, name: 'Chat', icon: '💬' },
            { id: 'files' as const, name: 'Upload Files', icon: '📁' },
            { id: 'history' as const, name: 'History', icon: '🕒' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'files' && <FileUpload />}
          {activeTab === 'history' && <ConversationHistory />}
        </div>
        
        <div className="lg:col-span-1">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Tips</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Upload PDF, DOCX, or TXT files to add to your memory</li>
              <li>• Ask questions about your uploaded documents</li>
              <li>• View conversation history anytime</li>
              <li>• The AI will search through your documents to find relevant information</li>
            </ul>
          </div>

          <div className="card mt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Memory</h3>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Documents stored:</span>
                <span className="font-medium">All uploaded files</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Chat sessions:</span>
                <span className="font-medium">Saved automatically</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;