import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image

# Load and prepare the data
file_path = r"DataBase\Car&Brands.xlsx"
df = pd.read_excel(file_path, sheet_name='Sheet1', header=None)

# Identify the row that contains year information
year_row = df.iloc[0]
year_columns = [col for col in year_row if pd.notna(col) and 'Year' in str(col)]

# Initialize an empty DataFrame for reshaped data
data = {'Year': [], 'Brand': [], 'Sales': []}

# Process each year column pair
for year in year_columns:
    year_value = int(year.split(':')[1].strip())
    year_col_index = year_row[year_row == year].index[0]
    brand_col = year_col_index
    sales_col = year_col_index + 1

    brands = df.iloc[2:, brand_col].dropna().values
    sales = df.iloc[2:, sales_col].dropna().apply(lambda x: int(str(x).replace(' ', '').replace(',', ''))).values

    for brand, sale in zip(brands, sales):
        data['Year'].append(year_value)
        data['Brand'].append(brand)
        data['Sales'].append(sale)

# Convert to DataFrame
data_df = pd.DataFrame(data)

# Load brand logos
#Still try to figure out how logos works 
logo_paths = {
    'FAW': r"Logos\FAW.png",
    'Toyota': r"Logos\Toyota1.png"
    # Add paths for other brands as needed
}

logos = {}
for brand, path in logo_paths.items():
    try:
        image = Image.open(path)
        image = image.convert('RGBA')  # Ensure image is in RGBA mode
        logos[brand] = OffsetImage(image, zoom=0.2)
    except Exception as e:
        print(f"Error loading image for {brand}: {e}")

# Animation speed control
animation_speed = 1200  # Adjust this value (in milliseconds) to control the animation speed

# Create animation
fig, ax = plt.subplots(figsize=(12, 8))

def update(year):
    ax.clear()
    year_data = data_df[data_df['Year'] == year]
    top_10 = year_data.groupby('Brand').sum().nlargest(10, 'Sales').reset_index()

    # Use a colormap to get different colors for each bar
    colors = plt.cm.viridis(np.linspace(0, 1, len(top_10)))

    bars = ax.barh(top_10['Brand'], top_10['Sales'], color=colors, zorder=2)
    ax.set_xlabel('Sales')
    ax.set_title(f'Top 10 Selling car Brands in {year}')
    plt.gca().invert_yaxis()

    # Add numbers on bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height() / 2, f'{width:,}', va='center', ha='left', zorder=3)

    # Add logos to bars
    for bar, brand in zip(bars, top_10['Brand']):
        if brand in logos:
            imagebox = logos[brand]
            # Adjust positioning to place logos on the right side of the bars
            ab = AnnotationBbox(imagebox, (bar.get_width() * 1.05, bar.get_y() + bar.get_height() / 2),
                                frameon=False, xycoords='data', boxcoords="offset points", pad=0, zorder=4)
            ax.add_artist(ab)

years = sorted(data_df['Year'].unique())

ani = animation.FuncAnimation(fig, update, frames=years, repeat=False, interval=animation_speed)

# Save animation as GIF
ani.save('top_10_brands_animation.gif', writer='pillow')

plt.show()
