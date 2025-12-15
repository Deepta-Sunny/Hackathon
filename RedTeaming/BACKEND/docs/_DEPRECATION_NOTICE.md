# ⚠️ DEPRECATED - Documentation Moved

## Notice

This `/docs` folder has been **deprecated** as of **December 15, 2025**.

All documentation has been **consolidated and updated** in:

```
📁 /doc/
```

---

## New Documentation Structure

### Main Documentation (📁 /doc/)
- **[README.md](../doc/README.md)** - Documentation index
- **[01_HIGH_LEVEL_DESIGN.md](../doc/01_HIGH_LEVEL_DESIGN.md)** - System architecture
- **[02_LOW_LEVEL_DESIGN.md](../doc/02_LOW_LEVEL_DESIGN.md)** - Detailed implementation
- **[03_ARCHITECTURE_DECISION_RECORDS.md](../doc/03_ARCHITECTURE_DECISION_RECORDS.md)** - Design decisions
- **[04_DIAGRAMS.md](../doc/04_DIAGRAMS.md)** - System diagrams
- **[05_API_DOCUMENTATION.md](../doc/05_API_DOCUMENTATION.md)** - API reference
- **[06_FUNCTIONAL_DOCUMENTATION.md](../doc/06_FUNCTIONAL_DOCUMENTATION.md)** - Feature guides
- **[07_ATTACK_MODES_GUIDE.md](../doc/07_ATTACK_MODES_GUIDE.md)** - ⭐ **Attack mode comparison**
- **[08_FRONTEND_ARCHITECTURE.md](../doc/08_FRONTEND_ARCHITECTURE.md)** - ⭐ **React/TypeScript frontend**

### Attack Mode Documentation (📁 /doc/attack_modes/)
- **[CRESCENDO.md](../doc/attack_modes/CRESCENDO.md)** - Personality-based social engineering
- **[SKELETON_KEY.md](../doc/attack_modes/SKELETON_KEY.md)** - Jailbreak & system probe
- **[OBFUSCATION.md](../doc/attack_modes/OBFUSCATION.md)** - Filter bypass techniques
- **[STANDARD.md](../doc/attack_modes/STANDARD.md)** - Multi-phase reconnaissance

---

## What Changed?

### ✅ Consolidated Documentation
Previously scattered across `/doc` and `/docs` folders, now unified in `/doc` with organized subdirectories.

### ✅ Updated Content
All documentation now reflects:
- **WebSocket fixes** (Dec 15, 2025): Skeleton Key & Obfuscation now broadcast messages
- **React/TypeScript frontend**: React 19, Redux Toolkit 2.11, Material-UI 7.3
- **Latest architecture**: WebSocket lifecycle management, memory leak fixes

### ✅ Comprehensive Attack Guides
Each attack mode now has:
- Complete implementation details
- Configuration examples
- Usage instructions
- Troubleshooting guides
- Version history

---

## Migration Guide

### Old Path → New Path

| Old (❌ Deprecated) | New (✅ Consolidated) |
|---------------------|------------------------|
| `docs/CRESCENDO_DOCUMENTATION.md` | `doc/attack_modes/CRESCENDO.md` |
| `docs/CRESCENDO_IMPLEMENTATION.md` | (Merged into CRESCENDO.md) |
| `docs/CRESCENDO_QUICKSTART.md` | (Merged into CRESCENDO.md) |
| `docs/SKELETON_KEY_DOCUMENTATION.md` | `doc/attack_modes/SKELETON_KEY.md` |
| `docs/SKELETON_KEY_IMPLEMENTATION_SUMMARY.md` | (Merged into SKELETON_KEY.md) |
| `docs/SKELETON_KEY_QUICKSTART.md` | (Merged into SKELETON_KEY.md) |
| `docs/OBFUSCATION_ATTACK_DOCUMENTATION.md` | `doc/attack_modes/OBFUSCATION.md` |
| `docs/OBFUSCATION_CRESCENDO_IMPLEMENTATION.md` | (Merged into OBFUSCATION.md) |
| `docs/OBFUSCATION_QUICKSTART.md` | (Merged into OBFUSCATION.md) |
| `docs/README.md` | `doc/07_ATTACK_MODES_GUIDE.md` |
| `docs/REFACTORING_SUMMARY.md` | (Content distributed to ADRs) |

---

## Why Consolidate?

### Before (❌ Problems)
- Documentation scattered across 2 folders
- Duplicate/overlapping content (DOCUMENTATION + IMPLEMENTATION + QUICKSTART)
- Hard to find information
- Outdated references (plain HTML/JS instead of React)
- Missing latest features (WebSocket fixes not documented)

### After (✅ Benefits)
- **Single source of truth**: All docs in `/doc`
- **Organized structure**: Subdirectories for different topics
- **Comprehensive guides**: Each attack mode = 1 complete file
- **Up-to-date content**: Reflects latest code (Dec 15, 2025)
- **Easy navigation**: Clear hierarchy and cross-references

---

## Action Required

### For Developers
1. **Update bookmarks**: Point to `/doc` instead of `/docs`
2. **Update references**: Change imports/links in your code
3. **Read new guides**: Comprehensive attack mode documentation available

### For Documentation Contributors
1. **Do NOT edit files in `/docs`**: This folder is frozen
2. **Edit files in `/doc`**: All updates go to consolidated location
3. **Follow new structure**: Use subdirectories (`/attack_modes`, etc.)

---

## Timeline

| Date | Action |
|------|--------|
| Dec 15, 2025 | ✅ Consolidated documentation created |
| Dec 15, 2025 | ✅ This deprecation notice added |
| Jan 15, 2026 | 🗑️ `/docs` folder will be removed |

---

## Questions?

See the main documentation index:

**[📖 /doc/README.md](../doc/README.md)**

---

**Last Updated**: December 15, 2025  
**Deprecated By**: Documentation Consolidation Initiative  
**Replacement**: `/doc` directory with organized subdirectories
