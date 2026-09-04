"""
generate_architecture_diagram.py
Generates architecture.png - the visual pipeline diagram for the README/submission.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(12, 9))
ax.set_xlim(0, 12)
ax.set_ylim(0, 14)
ax.axis('off')

def box(x, y, w, h, text, color, fontsize=10, fontweight='normal'):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                           linewidth=1.2, edgecolor='#333333', facecolor=color)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
             fontsize=fontsize, fontweight=fontweight, color='#1a1a1a', wrap=True)

def arrow(x1, y1, x2, y2, color='#444444'):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=14,
                          linewidth=1.3, color=color)
    ax.add_patch(a)

# Title
ax.text(5.5, 13.5, "Women's Safety AI Agent — Architecture", ha='center', fontsize=15, fontweight='bold')

# Trigger layer
box(3.5, 12.0, 4, 0.8, "TRIGGER\nWake word  OR  3x volume-button press", '#FDE9D9')

arrow(5.5, 12.0, 5.5, 11.4)

# Activation
box(3.5, 10.6, 4, 0.7, "Agent activates — starts listening", '#FDE9D9')

arrow(5.5, 10.6, 5.5, 10.0)

# Parallel analysis
box(0.8, 8.6, 4.2, 1.3, "AUDIO FEATURES\n(librosa)\nPitch, energy, stability", '#D9EAFD')
box(6.0, 8.6, 4.2, 1.3, "SPEECH-TO-TEXT\n(Whisper) + KEYWORD CHECK\nEnglish + Hindi distress words", '#D9EAFD')

arrow(5.5, 10.0, 2.9, 9.9)
arrow(5.5, 10.0, 8.1, 9.9)

arrow(2.9, 8.6, 5.3, 7.9)
arrow(8.1, 8.6, 6.2, 7.9)

# Distress scoring
box(3.3, 7.1, 4.4, 0.9, "DISTRESS SCORING\nWeighted combination -> 0-1 score", '#E3D9FD')

arrow(5.5, 7.1, 5.5, 6.5)

# Tier decision
box(3.3, 5.7, 4.4, 0.8, "TIER DECISION", '#F5F5F5', fontweight='bold')

arrow(4.3, 5.7, 1.8, 5.0)
arrow(5.5, 5.7, 5.5, 5.0)
arrow(6.7, 5.7, 9.2, 5.0)

# Three tiers
box(0.3, 3.9, 3.0, 1.0, "LOW\nNo action — log only", '#E8F5E9')
box(4.0, 3.9, 3.0, 1.0, "MEDIUM\nSoft check-in notification\n'Are you safe?'", '#FFF8E1')
box(7.7, 3.9, 4.0, 1.0, "HIGH\nFull alert sequence", '#FFEBEE')

arrow(9.7, 3.9, 9.7, 3.2)

# Alert actions
box(6.2, 2.0, 5.5, 1.1, "ALERT ACTION\nSMS with location  +  automated call\nplaying loud siren sound", '#FFEBEE')

arrow(9.0, 2.0, 9.0, 1.3)

# Logging
box(6.2, 0.3, 5.5, 0.9, "AUDIT LOG\nEvery decision + action timestamped", '#EEEEEE')

# Side note: failure handling
ax.text(0.3, 1.3, "Failure handling:\n• No internet -> SMS fallback\n• Corrupted audio -> skip, don't crash\n• Borderline score -> ask, don't alarm",
        fontsize=8.5, color='#555555', style='italic')

plt.tight_layout()
plt.savefig('/home/claude/women-safety-agent/architecture.png', dpi=150, bbox_inches='tight')
print("Saved architecture.png")
