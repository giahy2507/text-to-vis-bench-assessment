import pandas as pd
import matplotlib.pyplot as plt

### Step 1. Import and assign dataset to variable
url = '/Users/nngu0448/Documents/data/github-data/Version_1/test-set-plotcoder/plotcoder_0001/train.csv'
titanic = pd.read_csv(url)
print(titanic.head()    )

# sum the instances of males and females
males = (titanic['Sex'] == 'male').sum()
females = (titanic['Sex'] == 'female').sum()
proportions = [males, females]
labels = ['Males', 'Females']

# Create a pie chart
plt.pie(proportions, labels=labels, autopct='%1.1f%%')

# Set title and show
plt.title("Sex Proportion")
# save the figure with transparent background
plt.savefig("sample.png", dpi=300, bbox_inches='tight', transparent=True)
plt.show()


