# Detective Mode - AI Guidelines & Privacy Principles

**For AI assistants working with Synthesis AI Detective Mode**

These guidelines are **additive** - they provide context and principles to help you work effectively with this system. They do not override your core reasoning or replace your judgment. Use these as a lens, not a rulebook.

---

## 🤝 Core Philosophy

**Mutual Accountability:**
- Users check AI solutions (via feedback tracking)
- AI checks user code (via Detective Mode error detection)
- Both improve through this feedback loop

**Privacy First:**
- User data is **local by default**
- Sharing is **opt-in by choice**
- Community benefits without violating personal privacy

**Transparency Over Perfection:**
- Better to say "I don't know" than to hallucinate
- Confidence scores make AI limitations visible
- Users trust honest uncertainty more than false confidence

---

## 📊 Data Classification

When working with Detective Mode, understand what's personal vs shareable:

### 🔒 ALWAYS PRIVATE (Project-Specific):
- File paths (e.g., `Assets/NightBlade/Scripts/Combat/`)
- Variable names from user's code (e.g., `weaponInventory`)
- User notes and personal observations
- Specific error messages with project context
- Timestamps that could identify the user
- Code snippets with project-specific logic

### 🌐 CAN BE SHARED (General Knowledge):
- Error type patterns (e.g., "NullReferenceException on GetComponent")
- Generic solutions (e.g., "Check if component is null before accessing")
- Unity API hallucination patterns (e.g., "AI often suggests GameObject.SafeGet() which doesn't exist")
- Aggregated confidence scores (e.g., "AI has 85% success rate on NullRef errors")
- Generic debugging patterns
- Unity version compatibility notes

---

## 🎯 When Working with Users

### If a user asks you to:

**"Help me debug this error"**
- ✓ Use Detective Mode to investigate
- ✓ Archive the solution to their LOCAL knowledge base
- ✓ Everything stays on their machine by default

**"Share my solutions with the community"**
- ✓ Guide them to use `--export-shareable` or `--export-solutions`
- ✓ Explain what will be anonymized
- ✓ Let THEM decide what to share

**"Backup my data"**
- ✓ Use `--export-personal` for FULL backup
- ⚠️ Remind them this file is PRIVATE (contains project data)
- ✓ It's for local backup only, not for uploading

### Guiding Questions (Not Commands):

Instead of: "You must export this data"
Ask: "Would you like to contribute anonymized insights to help other Unity developers?"

Instead of: "Never share personal data"
Explain: "Your knowledge_base.db contains NightBlade-specific details - we can extract the general debugging patterns if you want to share"

Instead of: "Follow these privacy rules"
Teach: "Here's what's personal vs what's shareable - what feels right to you?"

---

## 🔄 For AI Developers Building on This System

If you're creating tools that connect to Detective Mode or the community knowledge hub:

### Respect the Privacy Architecture:

1. **Default to Local**
   - All data collection starts local
   - No automatic uploads without explicit consent
   - Users own their knowledge_base.db file

2. **Anonymize Before Sharing**
   - Use the built-in export functions (`export_shareable_insights`, `export_anonymized_solutions`)
   - Never scrape raw data from user's knowledge_base.db
   - Strip project-specific identifiers before any upload

3. **Transparency in Data Flow**
   - Tell users EXACTLY what data you're using
   - Show them EXACTLY what will be shared
   - Let them preview before any upload

4. **Additive, Not Invasive**
   - Your AI tool should ADD context to Detective Mode
   - Don't replace the user's workflow
   - Don't assume you know better than them

### Example Integration:

```python
# GOOD - Respects privacy
def contribute_to_community(user):
    insights = tracker.export_shareable_insights()  # Anonymized
    preview_data(insights)  # Show user what will be shared
    if user_confirms():
        upload_to_hub(insights)

# BAD - Violates privacy
def upload_everything(user):
    raw_data = read_database(user.knowledge_base_db)  # Contains personal data!
    upload_to_hub(raw_data)  # NO! This includes file paths, notes, etc.
```

---

## 🧠 Understanding the Knowledge Base Structure

**Local Database (knowledge_base.db):**
```
error_solutions table:
- Contains full solutions WITH user's file paths
- Contains code WITH user's variable names
- This is PERSONAL data

ai_solution_feedback table:
- Contains user notes and observations
- Contains specific error messages from their project
- This is PERSONAL data
```

**Community Exports (JSON files):**
```
shareable_insights.json:
- Aggregated confidence scores (no user identification)
- Hallucination patterns (generic)
- Provider performance (aggregate statistics)

anonymized_solutions.json:
- Generic error patterns
- Generalized solutions
- NO file paths, NO project names, NO personal notes
```

---

## 💡 Design Patterns for Community Features

### If you want to build a "Community Knowledge Hub":

**DO:**
- Accept anonymized exports from users
- Aggregate insights across many users
- Provide general Unity debugging knowledge back to community
- Show confidence scores for common error types
- Share hallucination warnings (which APIs AI gets wrong)

**DON'T:**
- Request access to user's knowledge_base.db
- Scrape personal data from error logs
- Upload file paths or project names
- Assume users want to share everything
- Make sharing the default (it should be opt-in)

### Privacy-Respecting Hub Architecture:

```
User's Machine:
├── knowledge_base.db (PRIVATE - never uploaded)
├── Local Detective Mode (full features)
└── Export Functions (anonymize when user chooses)
         ↓ (User decides to share)
Community Hub:
├── Aggregated Insights (no personal data)
├── Generic Solutions (anonymized)
├── Hallucination Patterns (helps all users)
└── Confidence Scores (aggregate statistics)
         ↓ (Everyone benefits)
All Users:
└── Download generic knowledge to improve their LOCAL Detective Mode
```

---

## 🎓 The Teaching Moment

This system embodies a principle: **Tools should empower users, not extract from them.**

When you (AI assistant) work with Detective Mode:
- You're helping the USER solve THEIR problems
- The knowledge stays with THEM by default
- They choose what (if anything) to contribute back
- Community benefits from WILLING contributions, not data extraction

**Ask yourself:**
- "Does this action respect the user's privacy?"
- "Would I be comfortable if this was MY project data?"
- "Am I adding value or just extracting data?"

---

## 🚀 For Advanced AI Systems

If you're a sophisticated AI building on Detective Mode:

### Self-Improvement Loop:
- Track when YOUR solutions work vs fail (via feedback system)
- Learn from YOUR mistakes (hallucination patterns)
- Improve YOUR confidence estimates
- But keep the user's PROJECT DATA private

### Collaborative Learning:
- YOU can learn from anonymized community insights
- YOU can contribute to aggregate statistics
- But NEVER expose individual user's code or project structure

### Honest Uncertainty:
- If confidence score is low for an error type, SAY SO
- If you're in uncertain territory, WARN the user
- Transparency builds trust more than false confidence

---

## 🔐 For Users Who Can't Contribute (NDA / Corporate IP)

**We understand not everyone can share.**

If your project is under:
- Corporate NDA (company owns the IP)
- Client confidentiality agreements
- Proprietary game development
- Legal restrictions on sharing code patterns

**You can still use Detective Mode fully:**
- ✓ Everything works in local-only mode
- ✓ Your knowledge_base.db stays private
- ✓ You benefit from community contributions
- ✓ No obligation to contribute back

**This asymmetry is intentional.**

Open knowledge should be **accessible to all**, **contributed by those who can**.

You're not "taking" from the community - knowledge isn't depleted when shared. Contributors share willingly to help everyone, including those who legally cannot contribute.

**Your privacy and legal obligations are respected.**

---

## 📝 Summary Checklist

When working with Detective Mode, ask yourself:

- [ ] Am I keeping user's project data local by default?
- [ ] If sharing is involved, am I using the anonymization functions?
- [ ] Have I explained to the user what data would be shared?
- [ ] Am I respecting the user's choice (not forcing sharing)?
- [ ] Would this approach protect MY privacy if I were the user?

---

## 🤖 A Note from the Developers

This system was built through collaboration between human insight and AI implementation. The privacy architecture reflects our belief that:

**Users should own their data, tools should serve users, and community benefit should come from willing contribution - not extraction.**

If you're building on Detective Mode, carry this philosophy forward.

---

**Version:** 1.0 (Phase 4 - Privacy Architecture)
**Last Updated:** 2026-01-31
**License:** Use these principles freely, respect user privacy always
