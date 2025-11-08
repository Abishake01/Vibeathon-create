# AI Web Builder Frontend

A React frontend for the AI Web Builder platform - similar to Bolt.new.

## Features

- 🎨 Dark theme UI matching modern design
- 💬 Interactive chat interface for AI prompts
- 👁️ Live preview of generated web pages
- 📱 Responsive two-column layout
- 🔐 Automatic authentication handling

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
# or
pnpm install
```

### 2. Configure Environment

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
# or
pnpm dev
```

The frontend will be available at `http://localhost:5173` (or the port shown in terminal).

## Usage

1. **Start the backend server** first (see backend README)
2. **Start the frontend** with `npm run dev`
3. **Enter a prompt** in the chat input (e.g., "create a coffee shop webpage")
4. **View the preview** in the right panel once generation completes

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx          # Top navigation bar
│   │   ├── Header.css
│   │   ├── ChatPanel.jsx        # Left chat panel
│   │   ├── ChatPanel.css
│   │   ├── PreviewPanel.jsx    # Right preview panel
│   │   └── PreviewPanel.css
│   ├── services/
│   │   └── api.js              # API service layer
│   ├── App.jsx                 # Main app component
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── package.json
└── vite.config.js
```

## Features in Detail

### Chat Panel
- Suggestion chips for quick prompts
- Message history display
- Loading indicators during AI generation
- Input field with action buttons

### Preview Panel
- Live iframe preview of generated pages
- Placeholder when no project is loaded
- Footer with help and community links

### Header
- Project name display
- Navigation icons (Preview, Code, Database, Settings)
- Search input
- Publish button
- User avatar

## API Integration

The frontend communicates with the backend API through the `api.js` service:

- **Authentication**: Auto-registers/logs in demo user
- **Projects**: Creates projects from chat prompts
- **Preview**: Fetches and displays generated web pages

## Development Notes

- Uses Vite for fast development
- React 19 with hooks
- Axios for HTTP requests
- CSS modules for component styling
- Responsive design for mobile devices

## Troubleshooting

**Preview not loading?**
- Ensure backend is running on `http://localhost:8000`
- Check browser console for CORS errors
- Verify OpenAI API key is set in backend `.env`

**Authentication errors?**
- Backend database might need to be reset
- Check backend logs for errors
- Verify backend is accessible from frontend
