import json
import matplotlib.pyplot as plt
import numpy as np
import os

# Set the working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load training data
with open('data/training_curves.json', 'r') as f:
    data = json.load(f)

# Set style
plt.style.use('default')
plt.rcParams['figure.figsize'] = [15, 10]
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Create subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

# Plot 1: Training and Validation Loss
ax1.plot(data['epochs'], data['epoch_losses'], 'b-o', label='Training Loss')
ax1.plot(data['epochs'], data['validation_losses'], 'r-o', label='Validation Loss')
ax1.set_title('Training and Validation Loss')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Loss')
ax1.grid(True)
ax1.legend()

# Plot 2: Command Recognition Accuracy
ax2.plot(data['epochs'], data['command_accuracy'], 'g-o')
ax2.set_title('Command Recognition Accuracy')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Accuracy (%)')
ax2.grid(True)

# Plot 3: Response Time
ax3.plot(data['epochs'], data['response_time'], 'm-o')
ax3.set_title('Response Time')
ax3.set_xlabel('Epoch')
ax3.set_ylabel('Time (s)')
ax3.grid(True)

# Plot 4: Step-wise Loss
ax4.plot(data['steps'], data['step_losses'], 'c-')
ax4.set_title('Step-wise Training Loss')
ax4.set_xlabel('Step')
ax4.set_ylabel('Loss')
ax4.grid(True)

# Adjust layout and save
plt.tight_layout()
plt.savefig('figures/training_curves.png', dpi=300, bbox_inches='tight')
plt.close()

# Create task-specific performance bar chart
tasks = ['Stand', 'Sit', 'Rotate', 'Forward/Backward', 'Turn Left/Right', 
         'Step Count', 'Obstacle Avoidance', 'Target Approach', 'Photo Capture']
accuracies = [92, 88, 85, 82, 80, 78, 75, 78, 90]

plt.figure(figsize=(12, 6))
bars = plt.bar(tasks, accuracies)
plt.title('Task-Specific Performance')
plt.xlabel('Task')
plt.ylabel('Accuracy (%)')
plt.xticks(rotation=45, ha='right')
plt.grid(True, axis='y')

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height)}%',
             ha='center', va='bottom')

plt.tight_layout()
plt.savefig('figures/task_performance.png', dpi=300, bbox_inches='tight')
plt.close() 