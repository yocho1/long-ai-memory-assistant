import React, { useState, useEffect } from 'react';
import { chatAPI } from '../../services/api';

interface Conversation {
  role: string;
  text: string;
  created_at: string;
}

const ConversationHistory: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await chatAPI.getHistory();
      setConversations(response.data.history || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    try {
      // Note: You'll need to add a clear history endpoint to your backend
      // For now, we'll just clear the local state
      setConversations([]);
    } catch (err: any) {
      setError('Failed to clear history');
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Conversation History</h3>
        <button
          onClick={clearHistory}
          className="btn-secondary text-sm"
          disabled={conversations.length === 0}
        >
          Clear All
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4">
          {error}
        </div>
      )}

      {conversations.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-4xl mb-4">🕒</div>
          <p className="text-gray-500">No conversation history yet.</p>
          <p className="text-sm text-gray-400 mt-2">
            Start chatting to see your history here.
          </p>
        </div>
      ) : (
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {conversations.map((conv, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg ${
                conv.role === 'user' 
                  ? 'bg-primary-50 border border-primary-100' 
                  : 'bg-gray-50 border border-gray-100'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  conv.role === 'user' 
                    ? 'bg-primary-600 text-white' 
                    : 'bg-gray-600 text-white'
                }`}>
                  {conv.role === 'user' ? 'U' : 'A'}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 mb-1">
                    {conv.role === 'user' ? 'You' : 'Assistant'}
                  </p>
                  <p className="text-gray-700 whitespace-pre-wrap">{conv.text}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(conv.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ConversationHistory;