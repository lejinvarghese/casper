# ⚡ Asgard

Asgard with an AI drone swarm dwelling together and led by Odin himself, alive and collaborating to help with daily planning, creative projects, and life management.

## 🤖 Meet Your Drone Swarm

- **⚡ Odin** - All Father Commander & Drone Orchestrator
- **🍯 Freya** - Kitchen Drone & Nutritionist (dwelling in the great kitchens)
- **📋 Sága** - Strategic Planning Drone & Event Coordinator (keeping the archives)  
- **🎨 Loki** - Creative Forge Drone & Artist (working the creative forges)
- **🧠 Mimir** - Wisdom Drone & Philosopher (in the wisdom chambers)
- **😈 Luci** - Shadow Drone & Mischief Maker (prowling the dark corners)

## 🚀 Quick Start

### Basic Usage

```bash
# Deploy the full drone swarm for comprehensive day planning
python3 -m src.agents.asgard.citadel --request "Plan my whole day for me"

# Direct mission to kitchen drone for dinner
python3 -m src.agents.asgard.citadel --request "What should I make for dinner?" --drone "freya"

# Task the strategic drone for weekend activities
python3 -m src.agents.asgard.citadel --request "Find me something fun to do this weekend" --drone "saga"

# Command the creative forge drone for artwork
python3 -m src.agents.asgard.citadel --request "Create a beautiful sunset painting" --drone "loki"

# Consult the wisdom drone for life advice
python3 -m src.agents.asgard.citadel --request "How can I find more meaning in my work?" --drone "mimir"

# Unleash the shadow drone for mischievous ideas
python3 -m src.agents.asgard.citadel --request "Suggest something spontaneous and fun" --drone "luci"
```

### Command Options

```bash
python3 -m src.agents.asgard.citadel [OPTIONS]

Options:
  --request TEXT    Your mission request for the drone swarm
  --drone TEXT      Direct request to specific drone (odin, freya, saga, loki, mimir, luci)
  --verbose         Show detailed drone deployment logs
  --help           Show help message
```

## 🎯 Use Cases

### 📅 Daily Planning
```bash
# Comprehensive day planning
python3 -m src.agents.asgard.citadel --request "Plan my whole day for me"

# Weekend planning
python3 -m src.agents.asgard.citadel --request "Plan a perfect Saturday in Toronto"

# Work-life balance
python3 -m src.agents.asgard.citadel --request "Help me balance work and personal time today"
```

### 🍽️ Meal Planning
```bash
# Dinner ideas
python3 -m src.agents.asgard.citadel --request "Plan dinner for tonight" --drone "chef"

# Weekly meal prep
python3 -m src.agents.asgard.citadel --request "Plan healthy meals for the week" --drone "chef"

# Special occasion menu
python3 -m src.agents.asgard.citadel --request "Plan a romantic dinner menu" --drone "chef"
```

### 🎨 Creative Projects
```bash
# Generate artwork
python3 -m src.agents.asgard.citadel --request "Create a serene landscape painting" --drone "artist"

# Creative inspiration
python3 -m src.agents.asgard.citadel --request "Give me ideas for a creative hobby project" --drone "artist"
```

### 🎯 Life Guidance
```bash
# Deep thinking
python3 -m src.agents.asgard.citadel --request "Help me think through a difficult decision" --drone "philosopher"

# Life philosophy
python3 -m src.agents.asgard.citadel --request "What's the meaning of a fulfilling life?" --drone "philosopher"
```

### 🎉 Fun & Entertainment
```bash
# Spontaneous fun
python3 -m src.agents.asgard.citadel --request "Surprise me with something fun" --drone "devil"

# Date night ideas
python3 -m src.agents.asgard.citadel --request "Plan a mischievous date night" --drone "devil"
```


## 🌍 Location Aware Features

All drones are configured for your operational territory and provide location specific intelligence:

- **Seasonal ingredients** and local food sources
- **Local attractions** and cultural landmarks  
- **Regional specialties** for pairings and recommendations
- **Weather-appropriate activities** for each season
- **Neighborhood knowledge** and transit considerations

## ⚙️ Setup Requirements

### Environment Variables
Ensure your `.env` file contains:
```bash
OPENAI_API_KEY=your_openai_api_key_here
RUNWARE_API_KEY=your_runware_api_key_here  # For artwork generation
```

### Dependencies
```bash
# Core dependencies
pip install smolagents openai python-dotenv click

# For artwork generation
pip install runware

# For web search (optional)
pip install duckduckgo-search
```

## 🧠 How It Works

### Drone Swarm Coordination
Odin acts as a **CodeAgent** that commands the specialized drone swarm:

- When you request day planning, Odin deploys multiple specialized drones
- Uses **managed drone** pattern for proper task delegation
- Each drone provides their expertise, Odin synthesizes collective intelligence

### Drone Specialization
- **Freya**: Uses seasonal local ingredients, handles nutrition and dietary needs
- **Sága**: Knows local events, neighborhoods, and activity recommendations  
- **Loki**: Creates artwork via Runware API integration
- **Mimir**: Provides deep philosophical perspectives and wisdom
- **Luci**: Adds creativity, mischief, and spontaneous adventures

### Smart Context
- Automatically detects current date/time for seasonal appropriateness
- Location-based recommendations and local knowledge
- No need to specify location or preferences - drones make smart assumptions

## 🔧 Advanced Usage

### Verbose Mode
```bash
python3 -m src.agents.asgard.citadel --request "Plan my day" --verbose
```
Shows detailed agent interactions and decision-making process.

### Direct Drone Access
You can bypass Odin and go directly to any specialized drone:
```bash
--drone "freya"       # Kitchen Drone
--drone "saga"        # Planning Drone  
--drone "loki"        # Creative Drone
--drone "mimir"       # Wisdom Drone
--drone "luci"        # Shadow Drone
```

### Integration Examples
```python
from src.agents.asgard.citadel import Asgard

# Create Asgard
asgard = Asgard(verbose=True)

# Full day planning (Odin orchestrates drone swarm)
day_plan = asgard.serve("Plan my whole day")

# Direct drone access
dinner_plan = asgard.direct_drone("freya", "Plan dinner for 4 people")
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Missing**
   ```
   ValueError: OPENAI_API_KEY required
   ```
   Solution: Add `OPENAI_API_KEY` to your `.env` file

2. **Runware API Issues** (Artist)
   ```
   ❌ Artwork creation failed: Missing API Key
   ```
   Solution: Add `RUNWARE_API_KEY` to your `.env` file or use other staff members

3. **Web Search Rate Limits**
   ```
   DuckDuckGoSearchException: 202 Ratelimit
   ```
   Solution: Wait a moment and try again, or use direct drone access without search requirements

### Performance Tips

- Use `--drone` for specific requests to avoid full swarm coordination overhead
- Odin's full swarm deployment is best for complex, multi-faceted requests
- Individual drones are faster for specialized requests

## 🎯 Examples Gallery

### Perfect Weekend Day
```bash
python3 -m src.agents.asgard.citadel --request "Plan a perfect weekend day with great food, culture, and fun"
```

### Dinner Party Planning  
```bash
python3 -m src.agents.asgard.citadel --request "Plan a dinner party for 6 friends" --drone "chef"
```

### Creative Inspiration
```bash
python3 -m src.agents.asgard.citadel --request "I'm feeling creatively stuck, help me" --drone "artist"
```

### Life Decision Support
```bash
python3 -m src.agents.asgard.citadel --request "I'm considering a career change, help me think through this" --drone "philosopher"
```

## 🌐 Web Interface

### Running the Complete Application

You can interact with your drone swarm through a modern web interface:

**Terminal 1 (Backend API Server):**
```bash
cd /media/starscream/wheeljack1/projects/casper/src/agents/asgard
python3 -m src.agents.asgard.api
```
The API runs on `http://localhost:8000`

**Terminal 2 (Frontend Interface):**
```bash
cd /media/starscream/wheeljack1/projects/casper/src/agents/asgard/frontend
npm install
npm run dev
```
The web interface runs on `http://localhost:3000`

### Web Interface Features

- **🎨 Modern Asgard UI** - Sleek interface with smooth animations
- **⚡ Interactive Agent Cards** - Visual selection of specialized drones
- **📝 Smart Request Panel** - Quick commands and custom requests
- **🔄 Real-time Processing** - Live feedback and step-by-step execution
- **⚙️ Configuration Panel** - Theme selection and verbose mode settings
- **📊 Response Display** - Formatted responses with copy functionality

### Web API Endpoints

- `GET /agents` - List all available drones
- `POST /request` - Submit requests to drone swarm
- `GET /health` - System health check
- `POST /configure` - Update Asgard settings

---

*Welcome to Asgard! Your drone swarm awaits deployment.* ⚡🤖


## 🤖 Asgard Automation System - Debug Commands

### Quick Status Check
```bash
# System health and recent automations
curl -s http://localhost:8000/health | python3 -m json.tool
curl -s http://localhost:8000/automations/recent | python3 -m json.tool

# Pretty-printed recent activity
curl -s http://localhost:8000/automations/recent | python3 -c "
import json, sys; data = json.load(sys.stdin)
for i, a in enumerate(data['automations'][:3], 1):
    print(f'{i}. {a[\"automation_name\"]} ({a[\"drone\"]}) - {\"✅\" if a[\"success\"] else \"❌\"}')"
```

### Debug & Testing
```bash
# Full system debug
curl -s http://localhost:8000/debug/automations | python3 -m json.tool

# Test automation
curl -X POST http://localhost:8000/automations/test

# Trigger specific automation
curl -X POST http://localhost:8000/automations/morning_energy/trigger
```

### Custom Scheduling (Odin)
```bash
# Create custom daily plan
curl -X POST http://localhost:8000/automations/custom-plan \
  -H "Content-Type: application/json" \
  -d '{
    "date": "'$(date +%Y-%m-%d)'",
    "events": [
      {"id": "test", "name": "Test Event", "drone": "saga", 
       "prompt": "Test automation", "schedule_time": "15:30"}
    ]
  }'
``` 