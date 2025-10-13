"""
Find complex, diverse workflows for testing.
Looks for workflows with high node counts and diverse characteristics.
"""

# Known complex workflows from n8n.io (manually curated)
COMPLEX_WORKFLOWS = [
    {
        'id': '1954',
        'name': 'AI agent chat',
        'complexity': 'Medium',
        'nodes': 5,
        'features': ['LangChain', 'AI', 'Chat', 'Memory'],
        'reason': 'AI workflow with multiple LangChain nodes'
    },
    {
        'id': '2462',
        'name': 'Angie, Personal AI Assistant with Telegram',
        'complexity': 'High',
        'nodes': '10+',
        'features': ['Telegram', 'Voice', 'AI', 'Multimodal'],
        'reason': 'Complex AI assistant with voice and text'
    },
    {
        'id': '9343',
        'name': 'Monitor iOS App Store Reviews',
        'complexity': 'Medium',
        'nodes': '8+',
        'features': ['Scheduled', 'API', 'Email', 'Monitoring'],
        'reason': 'Real-world monitoring workflow'
    },
    {
        'id': '2134',
        'name': 'Extract emails from website HTMLs',
        'complexity': 'Low-Medium',
        'nodes': '5+',
        'features': ['Scraping', 'Regex', 'Data extraction'],
        'reason': 'Data processing workflow'
    },
    {
        'id': '3456',
        'name': 'Discord Chatbot with Gemini 2.0',
        'complexity': 'Medium',
        'nodes': '7+',
        'features': ['Discord', 'AI', 'Chat', 'Integration'],
        'reason': 'Bot integration with AI'
    },
    {
        'id': '1828',
        'name': 'Advanced workflow (if exists)',
        'complexity': 'Unknown',
        'nodes': 'Unknown',
        'features': ['To be discovered'],
        'reason': 'Testing different workflow ID'
    }
]

print("\n" + "="*80)
print("🔍 COMPLEX WORKFLOWS FOR TESTING")
print("="*80)

for i, wf in enumerate(COMPLEX_WORKFLOWS, 1):
    print(f"\n{i}. Workflow #{wf['id']} - {wf['name']}")
    print(f"   Complexity: {wf['complexity']}")
    print(f"   Nodes: {wf['nodes']}")
    print(f"   Features: {', '.join(wf['features'])}")
    print(f"   Reason: {wf['reason']}")

print("\n" + "="*80)
print("✅ Test Plan:")
print("="*80)
print("\nPhase 2 Testing (Visual Layout):")
print("  • Test on workflows: 2462, 9343, 1954")
print("  • Validate: Node positions, canvas state, spatial metrics")
print("\nPhase 3 Testing (Enhanced Text):")
print("  • Test on workflows: 2462, 3456, 1954")
print("  • Validate: Text extraction, categorization")
print("\nPhase 4 Testing (Media):")
print("  • Test on workflows: 9343, 2462, 2134")
print("  • Validate: Image/video extraction, categorization")
print("\n")

