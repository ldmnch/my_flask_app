from flask import render_template, request
from flaskapp import app
from flaskapp.models import UkData
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

ELECTION_COLUMNS = ['Turnout19', 'ConVote19', 'LabVote19', 'LDVote19',
    'SNPVote19', 'PCVote19', 'UKIPVote19', 'GreenVote19',
    'BrexitVote19', 'TotalVote19']

DEMOGRAPHIC_COLUMNS = [
    'c11PopulationDensity', 'c11Female', 'c11FulltimeStudent',
    'c11Retired', 'c11HouseOwned', 'c11HouseholdMarried'
]

@app.route("/")
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    """First dashboard with bar chart by country"""
    selected_var = request.args.get('variable', 'TotalVote19')
    
    # Get data
    df = get_dataframe(['country', selected_var])
    country_means = df.groupby('country')[selected_var].mean().reset_index()
    
    # Create plot
    plot_data = create_bar_plot(
        data=country_means,
        x='country',
        y=selected_var,
        title=f'Average {selected_var} by Country'
    )
    
    return render_template(
        'dashboard.html',
        plot_data=plot_data,
        numeric_columns=ELECTION_COLUMNS,
        selected_var=selected_var
    )

@app.route('/relationships')
def relationships():
    """Second dashboard with faceted scatter plots"""
    x_var = request.args.get('x_var', 'c11PopulationDensity')
    y_var = request.args.get('y_var', 'Turnout19')
    
    # Get data
    df = get_dataframe(['country', x_var, y_var])
    
    # Create plot
    plot_data = create_scatter_plot(
        data=df,
        x_var=x_var,
        y_var=y_var,
        title=f'{y_var} vs {x_var} by Country'
    )
    
    return render_template(
        'relationships.html',
        plot_data=plot_data,
        demog_columns = DEMOGRAPHIC_COLUMNS,
        election_columns = ELECTION_COLUMNS,
        x_var=x_var,
        y_var=y_var
    )

# Helper functions
def get_dataframe(columns):
    """Get DataFrame with specified columns from database"""
    data = UkData.query.all()

    df = pd.DataFrame([{
        'id': c.id,
        'constituency_name': c.constituency_name,
        'country': c.country,
        'region': c.region,
        'Turnout19': c.Turnout19,
        'ConVote19': c.ConVote19,
        'LabVote19': c.LabVote19,
        'LDVote19': c.LDVote19,
        'SNPVote19': c.SNPVote19,
        'PCVote19': c.PCVote19,
        'UKIPVote19': c.UKIPVote19,
        'GreenVote19': c.GreenVote19,
        'BrexitVote19': c.BrexitVote19,
        'TotalVote19': c.TotalVote19,
        'c11PopulationDensity': c.c11PopulationDensity,
        'c11Female': c.c11Female,
        'c11FulltimeStudent': c.c11FulltimeStudent,
        'c11Retired': c.c11Retired,
        'c11HouseOwned': c.c11HouseOwned,
        'c11HouseholdMarried': c.c11HouseholdMarried
    } for c in data])

    return df

def create_bar_plot(data, x, y, title):
    """Create a bar plot with values annotated"""
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    ax = sns.barplot(x=x, y=y, data=data, palette="Blues_d")
    
    # Add values on bars
    for p in ax.patches:
        ax.annotate(
            f"{p.get_height():,.1f}",
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center', va='center', xytext=(0, 10),
            textcoords='offset points'
        )
    
    plt.title(title, pad=20)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return save_plot_to_base64()

def create_scatter_plot(data, x_var, y_var, title):
    """Create a scatter plot with regression line"""
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    ax = sns.regplot(x=x_var, y=y_var, data=data, scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    
    plt.title(title, pad=20)
    plt.xlabel(x_var)
    plt.ylabel(y_var)
    plt.tight_layout()
    
    return save_plot_to_base64()

def save_plot_to_base64():
    """Save current plot to base64 encoded string"""
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    return plot_data
