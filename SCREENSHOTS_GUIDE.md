# Screenshots Guide for Public Release

**Purpose**: Capture professional screenshots that showcase the project's key features for the README.

---

## 📸 Required Screenshots

### 1. Hero Screenshot (Main Interface)
**File**: `docs/images/hero-screenshot.png`  
**What to show**:
- Full application interface with chat on left, canvas on right
- A complete architecture visible on canvas (e.g., API Gateway → Lambda → DynamoDB)
- Chat showing a natural conversation
- Professional, clean state (no errors, good example)

**How to capture**:
```bash
# Run the app
cd apps/backend && uv run uvicorn scaffold_ai.main:app --reload &
cd apps/web && pnpm dev

# Navigate to http://localhost:3000
# Create a sample architecture: "Build a REST API with DynamoDB"
# Take full-window screenshot (1920x1080 or higher)
```

**Tips**:
- Use a clean browser window (no bookmarks bar)
- Zoom to 100%
- Show a complete, professional architecture
- Make sure the chat shows a good example conversation

---

### 2. Multi-Agent Workflow
**File**: `docs/images/workflow-diagram.png`  
**What to show**:
- Visual representation of the LangGraph workflow
- Nodes: Interpreter → Architect → Security → Code Generator
- Arrows showing flow
- State transitions

**How to create**:
Option A: Use LangGraph's built-in visualization
```python
from scaffold_ai.graph.workflow import create_workflow

graph = create_workflow()
graph.get_graph().draw_mermaid_png(output_file_path="docs/images/workflow-diagram.png")
```

Option B: Create a simple diagram with draw.io or Excalidraw showing:
```
┌─────────────┐
│ User Input  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Interpreter │ (Classify intent)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Architect  │ (Design architecture)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Security   │ (Validate & score)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Code Gen  │ (Generate IaC)
└─────────────┘
```

---

### 3. Security Gate in Action
**File**: `docs/images/security-gate.png`  
**What to show**:
- Chat showing a security failure
- Example: "Build an API with public S3 bucket"
- Security specialist blocking the architecture
- Error message explaining why (security score < 70)

**How to capture**:
```bash
# In the chat, type:
"Create an API that stores data in a public S3 bucket"

# The security gate should block this
# Screenshot the chat showing the security failure message
```

---

### 4. Generated Code Modal
**File**: `docs/images/code-generation.png`  
**What to show**:
- Code viewer modal open
- Tabs showing different formats (CDK TypeScript, CloudFormation, Terraform)
- Clean, syntax-highlighted code
- Professional appearance

**How to capture**:
```bash
# After generating a valid architecture, click "Generate Code"
# Screenshot the modal with code visible
# Make sure tabs are visible at the top
```

---

### 5. Canvas with Multiple Services
**File**: `docs/images/canvas-editor.png`  
**What to show**:
- React Flow canvas with 5-7 AWS service nodes
- Example: API Gateway → Lambda → DynamoDB → S3 → CloudWatch
- Connections between nodes
- Professional layout

**How to capture**:
```bash
# Create a more complex architecture:
"Build a serverless API with authentication, database, file storage, and monitoring"

# Screenshot just the canvas area (right side)
# Make sure all nodes are visible and well-arranged
```

---

### 6. AWS Cloudscape UI Components
**File**: `docs/images/cloudscape-ui.png`  
**What to show**:
- Close-up of Cloudscape components
- Example: Header, side navigation, buttons, cards
- Shows professional AWS Console aesthetic

**How to capture**:
```bash
# Screenshot the header and navigation area
# Highlight the professional AWS Console look
```

---

## 🎨 Screenshot Standards

### Technical Requirements
- **Resolution**: Minimum 1920x1080
- **Format**: PNG (for transparency and quality)
- **File Size**: <500KB each (optimize with tinypng.com)
- **Browser**: Chrome or Firefox (latest)
- **Zoom**: 100% (no browser zoom)

### Visual Standards
- **Clean State**: No errors, loading states, or incomplete data
- **Professional**: Use realistic example data
- **Consistent**: Same theme (light or dark) across all screenshots
- **Cropped**: Remove unnecessary browser chrome
- **Annotated**: Optional arrows/highlights for key features

### Example Data to Use
```
Good examples:
- "Build a REST API for a todo app with authentication"
- "Create a serverless image processing pipeline"
- "Design a real-time chat application with WebSockets"

Avoid:
- "test"
- "hello world"
- Incomplete or error states
```

---

## 📝 Adding Screenshots to README

Once you have the screenshots, update the README:

```markdown
## 🖼️ Screenshots

### Main Interface
![Scaffold AI Interface](docs/images/hero-screenshot.png)
*Natural language architecture design with real-time canvas visualization*

### Multi-Agent Workflow
![LangGraph Workflow](docs/images/workflow-diagram.png)
*Dynamic routing through specialized AI agents*

### Security Gate
![Security Validation](docs/images/security-gate.png)
*Automated security scoring blocks insecure architectures*

### Code Generation
![Generated IaC Code](docs/images/code-generation.png)
*Multi-format infrastructure as code (CDK, CloudFormation, Terraform)*
```

---

## 🎥 Optional: Demo GIF

**File**: `docs/images/demo.gif`  
**What to show**:
- 10-15 second loop
- User typing in chat
- Architecture appearing on canvas
- Code generation modal opening

**Tools**:
- **macOS**: QuickTime + gifski
- **Windows**: ScreenToGif
- **Linux**: Peek or SimpleScreenRecorder + ffmpeg

**Command to convert video to GIF**:
```bash
# Using ffmpeg
ffmpeg -i demo.mp4 -vf "fps=10,scale=1280:-1:flags=lanczos" -c:v gif demo.gif

# Optimize with gifsicle
gifsicle -O3 --colors 256 demo.gif -o demo-optimized.gif
```

**GIF Requirements**:
- **Duration**: 10-15 seconds
- **Size**: <5MB
- **FPS**: 10-15
- **Resolution**: 1280x720

---

## ✅ Checklist

Before public release:
- [ ] Hero screenshot captured
- [ ] Workflow diagram created
- [ ] Security gate screenshot captured
- [ ] Code generation modal screenshot captured
- [ ] Canvas editor screenshot captured
- [ ] Cloudscape UI screenshot captured
- [ ] All images optimized (<500KB each)
- [ ] Images added to `docs/images/` directory
- [ ] README updated with image references
- [ ] Optional: Demo GIF created
- [ ] All screenshots use consistent theme
- [ ] All screenshots show professional example data

---

## 🎯 Priority Order

If time is limited, capture in this order:

1. **Hero screenshot** (most important - shows full app)
2. **Workflow diagram** (explains architecture)
3. **Code generation modal** (shows output)
4. **Security gate** (unique feature)
5. **Canvas editor** (visual appeal)
6. **Demo GIF** (optional but impressive)

---

## 📊 Impact

Good screenshots will:
- ✅ Increase GitHub stars (visual appeal)
- ✅ Help recruiters understand the project quickly
- ✅ Demonstrate UI/UX skills
- ✅ Make the README more engaging
- ✅ Showcase the professional AWS Cloudscape design

**Estimated time**: 30-45 minutes to capture all screenshots
