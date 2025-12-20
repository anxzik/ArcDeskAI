# ArcDesk.AI SVG Assets

A comprehensive collection of vector graphics designed specifically for the ArcDesk.AI Electron application, including UI components and dashboard elements.

## 📁 Directory Structure

```
arcdesk-ai-assets/
├── icons/                      # AI model icons
│   ├── openai-gpt.svg
│   ├── claude-anthropic.svg
│   ├── google-gemini.svg
│   ├── meta-llama.svg
│   └── mistral-ai.svg
├── buttons/                    # Interactive button components
│   ├── primary-button.svg
│   ├── secondary-button.svg
│   └── play-button.svg
├── nodes/                      # Workflow node components
│   ├── ai-model-node.svg
│   └── data-processor-node.svg
├── ui-elements/                # General UI controls
│   ├── toggle-switch.svg
│   ├── slider-control.svg
│   └── dropdown-select.svg
├── dashboard/                  # Dashboard visualization elements
│   ├── charts/                 # Data visualization charts
│   │   ├── line-chart.svg
│   │   ├── bar-chart.svg
│   │   ├── donut-chart.svg
│   │   └── area-chart.svg
│   ├── widgets/                # Dashboard widgets
│   │   ├── circular-gauge.svg
│   │   ├── stat-card.svg
│   │   ├── progress-ring.svg
│   │   └── activity-heatmap.svg
│   ├── panels/                 # Information panels
│   │   ├── system-status.svg
│   │   └── mini-metrics.svg
│   └── indicators/             # Live data indicators
│       └── data-stream.svg
├── showcase.html               # UI components preview
└── dashboard-showcase.html     # Dashboard elements preview
```

## 🎨 Design Features

- **Unique Visual Identity**: Each AI model has a distinctive icon design avoiding generic AI aesthetics
- **Dark Theme Optimized**: All assets are designed for dark mode interfaces
- **Interactive States**: Hover effects and state variations included
- **Scalable Vectors**: Resolution-independent graphics perfect for any display
- **Consistent Design Language**: Unified color schemes and visual style
- **Animated Elements**: Many dashboard components include smooth animations
- **Real-time Indicators**: Live data visualization components

## 📊 Dashboard Elements

### Charts
- **Line Chart**: Animated performance metrics with gradient fills
- **Bar Chart**: Quarterly data visualization with entrance animations
- **Donut Chart**: Segmented circular chart with legend
- **Area Chart**: Multi-series area chart for time-based data

### Widgets
- **Circular Gauge**: Speedometer-style metric display
- **Stat Card**: KPI card with trend indicators and sparklines
- **Progress Ring**: Circular progress indicator with percentage
- **Activity Heatmap**: GitHub-style contribution visualization

### Panels & Indicators
- **System Status Panel**: Multi-service health monitoring
- **Mini Metrics Panel**: Compact KPI dashboard
- **Data Stream**: Real-time data flow visualization

## 🚀 Usage in Electron

### Basic Implementation

```javascript
// In your main process
const { app, BrowserWindow } = require('electron');
const path = require('path');

// Reference assets
const assetsPath = path.join(__dirname, 'arcdesk-ai-assets');
```

### In HTML

```html
<!-- Using in your HTML -->
<img src="./arcdesk-ai-assets/icons/openai-gpt.svg" alt="GPT Model">
<button class="btn-primary">
  <img src="./arcdesk-ai-assets/buttons/primary-button.svg" alt="Action">
</button>
```

### In React Components

```jsx
// Import SVGs as React components
import { ReactComponent as GPTIcon } from './assets/icons/openai-gpt.svg';

function ModelSelector() {
  return (
    <div className="model-selector">
      <GPTIcon />
      <span>Select AI Model</span>
    </div>
  );
}
```

### Dynamic Loading

```javascript
// Dynamically load icons based on model type
const modelIcons = {
  'gpt': './assets/icons/openai-gpt.svg',
  'claude': './assets/icons/claude-anthropic.svg',
  'gemini': './assets/icons/google-gemini.svg',
  'llama': './assets/icons/meta-llama.svg',
  'mistral': './assets/icons/mistral-ai.svg'
};

function loadModelIcon(modelType) {
  const iconPath = modelIcons[modelType];
  return iconPath;
}
```

### Dashboard Integration

```javascript
// Create a real-time dashboard
const Dashboard = () => {
  return (
    <div className="dashboard-grid">
      {/* Top metrics row */}
      <div className="metrics-row">
        <img src="./assets/dashboard/widgets/stat-card.svg" alt="Revenue" />
        <img src="./assets/dashboard/widgets/circular-gauge.svg" alt="CPU Usage" />
        <img src="./assets/dashboard/widgets/progress-ring.svg" alt="Progress" />
      </div>
      
      {/* Charts section */}
      <div className="charts-section">
        <img src="./assets/dashboard/charts/line-chart.svg" alt="Performance" />
        <img src="./assets/dashboard/charts/area-chart.svg" alt="Network" />
      </div>
      
      {/* Status panel */}
      <div className="status-section">
        <img src="./assets/dashboard/panels/system-status.svg" alt="System Health" />
        <img src="./assets/dashboard/indicators/data-stream.svg" alt="Live Data" />
      </div>
    </div>
  );
};

// Dynamic chart loading based on data type
const chartComponents = {
  'timeseries': './dashboard/charts/line-chart.svg',
  'comparison': './dashboard/charts/bar-chart.svg',
  'distribution': './dashboard/charts/donut-chart.svg',
  'trend': './dashboard/charts/area-chart.svg'
};

function selectChart(dataType) {
  return chartComponents[dataType] || chartComponents['timeseries'];
}
```

## 🎯 Color Palette

The assets use a carefully selected color palette:

- **Primary**: `#6366F1` - `#4F46E5` (Indigo gradient)
- **Success**: `#10B981` - `#059669` (Emerald gradient)
- **OpenAI**: `#10a37f` - `#1a7f64`
- **Anthropic**: `#D4A574` - `#B8956A`
- **Google**: `#4285F4` - `#1557B0`
- **Meta**: `#0866FF` - `#0653D3`
- **Mistral**: `#F7931E` - `#ED6A0C`

## 🛠️ Customization

All SVGs are easily customizable:

1. **Colors**: Edit gradient definitions in the `<defs>` section
2. **Sizes**: SVGs are scalable - use CSS or width/height attributes
3. **Animations**: Add CSS animations for enhanced interactivity

Example CSS customization:
```css
.ai-model-icon {
  width: 48px;
  height: 48px;
  transition: transform 0.3s ease;
}

.ai-model-icon:hover {
  transform: scale(1.1);
}
```

## 📝 License

These assets are created specifically for the ArcDesk.AI project. Please ensure proper attribution if used elsewhere.

## 🔧 Tips

1. Use the `showcase.html` file to preview UI components in a browser
2. Use the `dashboard-showcase.html` file to preview dashboard elements
3. SVGs can be embedded inline for maximum control
4. Consider using a build tool to optimize SVGs for production
5. The node components include connection ports for visual programming interfaces
6. Dashboard elements include animated components - check browser performance
7. All animations are CSS-based for optimal performance

---

For questions or additional asset requests, please refer to the ArcDesk.AI documentation.