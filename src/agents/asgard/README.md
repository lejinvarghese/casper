# ⚡ Asgard Citadel - Your AI Drone Swarm

An Odin-commanded citadel of specialized AI drones dwelling together, always alive and working to help with daily planning, creative projects, and life management.

## 🤖 Meet Your Drone Swarm

- **⚡ Odin** - All-Father Commander & Drone Orchestrator (GPT-4o)
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
python3 -m src.agents.asgard.citadel --request "Plan dinner for tonight" --staff "chef"

# Weekly meal prep
python3 -m src.agents.asgard.citadel --request "Plan healthy meals for the week" --staff "chef"

# Special occasion menu
python3 -m src.agents.asgard.citadel --request "Plan a romantic dinner menu" --staff "chef"
```

### 🎨 Creative Projects
```bash
# Generate artwork
python3 -m src.agents.asgard.citadel --request "Create a serene landscape painting" --staff "artist"

# Creative inspiration
python3 -m src.agents.asgard.citadel --request "Give me ideas for a creative hobby project" --staff "artist"
```

### 🎯 Life Guidance
```bash
# Deep thinking
python3 -m src.agents.asgard.citadel --request "Help me think through a difficult decision" --staff "philosopher"

# Life philosophy
python3 -m src.agents.asgard.citadel --request "What's the meaning of a fulfilling life?" --staff "philosopher"
```

### 🎉 Fun & Entertainment
```bash
# Spontaneous fun
python3 -m src.agents.asgard.citadel --request "Surprise me with something fun" --staff "devil"

# Date night ideas
python3 -m src.agents.asgard.citadel --request "Plan a mischievous date night" --staff "devil"
```


## 🏙️ Toronto-Aware Features

All agents are familiar with Toronto, Ontario and provide location-specific recommendations:

- **Seasonal ingredients** (Niagara peaches, Ontario corn, etc.)
- **Local attractions** (CN Tower, Harbourfront, High Park)
- **Ontario VQA wines** for pairings
- **Weather-appropriate activities** for each season
- **Toronto neighborhoods** and transit considerations

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

### Butler Orchestration
The Butler (Jeeves) acts as a **CodeAgent** that manages other specialized agents:

- When you request day planning, the butler coordinates multiple staff members
- Uses **managed agents** pattern for proper delegation
- Each specialist provides their expertise, butler synthesizes the response

### Agent Specialization
- **Chef Auguste**: Uses seasonal Toronto ingredients, considers nutrition and dietary needs
- **Sophia**: Knows Toronto events, neighborhoods, and activity recommendations  
- **Leonardo**: Creates artwork via Runware API integration
- **Aristotle**: Provides thoughtful philosophical perspectives
- **Imp**: Adds creativity and spontaneous fun to any plan

### Smart Context
- Automatically detects current date/time for seasonal appropriateness
- Toronto-based recommendations and local knowledge
- No need to specify location or preferences - agents make smart assumptions

## 🔧 Advanced Usage

### Verbose Mode
```bash
python3 -m src.agents.asgard.citadel --request "Plan my day" --verbose
```
Shows detailed agent interactions and decision-making process.

### Direct Staff Access
You can bypass the butler and go directly to any staff member:
```bash
--staff "chef"        # Chef Auguste
--staff "planner"     # Sophia  
--staff "artist"      # Leonardo
--staff "philosopher" # Aristotle
--staff "devil"       # Imp
```

### Integration Examples
```python
from src.agents.asgard.citadel import SymphoniumEnsemble

# Create household
household = SymphoniumEnsemble(verbose=True)

# Full day planning (butler orchestrates)
day_plan = household.serve("Plan my whole day")

# Direct staff access
dinner_plan = household.direct_staff("chef", "Plan dinner for 4 people")
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
   Solution: Wait a moment and try again, or use staff members without search requirements

### Performance Tips

- Use `--staff` for specific requests to avoid butler coordination overhead
- The butler is best for complex, multi-faceted requests
- Individual staff members are faster for specialized requests

## 🎯 Examples Gallery

### Perfect Weekend Day
```bash
python3 -m src.agents.asgard.citadel --request "Plan a perfect Toronto weekend day with great food, culture, and fun"
```

### Dinner Party Planning  
```bash
python3 -m src.agents.asgard.citadel --request "Plan a dinner party for 6 friends" --staff "chef"
```

### Creative Inspiration
```bash
python3 -m src.agents.asgard.citadel --request "I'm feeling creatively stuck, help me" --staff "artist"
```

### Life Decision Support
```bash
python3 -m src.agents.asgard.citadel --request "I'm considering a career change, help me think through this" --staff "philosopher"
```

---

*Welcome to your AI household! Your distinguished staff awaits your requests.* 🏠✨