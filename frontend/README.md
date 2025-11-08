# Web Builder Frontend

A React frontend for the Web Builder platform - similar to Bolt.new. A code editor for creating HTML, CSS, and JavaScript projects.

## Features

- 🎨 Dark theme UI matching modern design
- 📝 Code editor with tabs for HTML, CSS, and JavaScript
- 👁️ Live preview of web pages
- 📁 Project management (create, list, select projects)
- 💾 Auto-save functionality
- 📱 Responsive three-column layout
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
3. **Create a new project** by clicking the "+" button in the sidebar
4. **Edit code** in the editor panel (HTML, CSS, JS tabs)
5. **View live preview** in the right panel (auto-updates on save)
6. **Switch between projects** by clicking on them in the sidebar

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx          # Top navigation bar
│   │   ├── Header.css
│   │   ├── ProjectList.jsx     # Sidebar project list
│   │   ├── ProjectList.css
│   │   ├── CodeEditor.jsx      # Code editor with tabs
│   │   ├── CodeEditor.css
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

### Project List (Sidebar)
- List of all user projects
- Create new project button
- Click to select and load project
- Active project highlighting

### Code Editor
- Three tabs: HTML, CSS, JavaScript
- Syntax highlighting ready (monospace font)
- Auto-save after 1 second of inactivity
- Unsaved changes indicator
- File info display

### Preview Panel
- Live iframe preview of web pages
- Auto-refreshes on file save
- Loading indicator
- Placeholder when no project is loaded
- Footer with help and community links

### Header
- Project name display
- Navigation icons (Preview, Code, Database, Settings)
- Search input
- Refresh button
- Publish button
- User avatar

## API Integration

The frontend communicates with the backend API through the `api.js` service:

- **Authentication**: Auto-registers/logs in demo user
- **Projects**: Create, list, update, delete projects
- **Files**: Get and update HTML, CSS, JS files
- **Preview**: Fetches and displays live preview

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
- Verify project files are saved correctly

**Authentication errors?**
- Backend database might need to be reset
- Check backend logs for errors
- Verify backend is accessible from frontend
