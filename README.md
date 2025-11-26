# AI Memory Assistant 🤖

A full-stack application that allows you to upload documents and chat with an AI that remembers your documents and provides intelligent responses based on your personal knowledge base.

## 🚀 Features

### Backend
- **Document Processing**: Upload and process PDF, DOCX, and TXT files
- **Intelligent Chat**: AI-powered responses based on your uploaded documents
- **Vector Database**: ChromaDB for efficient document retrieval
- **Authentication**: JWT-based user authentication
- **Memory Management**: Local embedding models with fallback options
- **Security**: Automatic sensitive data masking (TOTP secrets, emails, etc.)

### Frontend
- **Modern UI**: Clean React interface with Tailwind CSS
- **File Upload**: Drag & drop file upload with progress indicators
- **Real-time Chat**: Interactive chat interface with message history
- **Dashboard**: Tab-based navigation for different features
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **ChromaDB** - Vector database for document storage
- **Sentence Transformers** - Local embedding models
- **JWT** - Authentication tokens
- **PyPDF2/python-docx** - Document text extraction

### Frontend
- **React** - Frontend framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - API communication
- **React Router** - Navigation

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git
