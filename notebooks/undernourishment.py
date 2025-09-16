# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "altair==5.4.1",
#     "marimo",
#     "pandas==2.2.3",
#     "datetime",
#     "requests",
# ]
# ///

import marimo

__generated_with = "0.15.2"
app = marimo.App(width="full")

@app.cell
def _():
    # Import dependencies
    import datetime
    import marimo as mo
    import altair as alt
    import pandas as pd
    import requests
    return alt, datetime, mo, pd


@app.cell
def _(mo):
    mo.md(
        """
    # World Undernourishment Over Time
    ## By: Nils Indreiten
    A deep dive into world undernourishment rates by region over time. Undernourishment is a condition where a person's habitual food consumption is insufficient to provide the dietary energy levels required to maintain a normal, active, and healthy life.
    The regions included in this application are the FAO (Food and Agriculture Organisation regions). The data was obtained from [Our World in Data](https://ourworldindata.org/grapher/prevalence-of-undernourishment), using the Python api.
    """
    )
    return


@app.cell
def _(alt, mo):
    # Apply carbonwhite theme:
    alt.themes.enable('carbonwhite')
    mo.output.clear()
    return


@app.cell
def _(pd):
    # Retrieve the data:
    df = pd.read_csv("https://ourworldindata.org/grapher/prevalence-of-undernourishment.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
    df.rename(columns={df.columns[-1]: "undernourishment"}, inplace=True)
    df = df.drop(columns=['Code'])
    return (df,)


@app.cell
def _(mo):
    # Set up region options:
    options = ["World","Northern Africa (FAO)","South-eastern Asia (FAO)","South America (FAO)","Central Asia (FAO)","Sub-Saharan Africa (FAO)"]
    multiselect = mo.ui.multiselect(options=options,value=["Northern Africa (FAO)","South-eastern Asia (FAO)","South America (FAO)","Central Asia (FAO)","Sub-Saharan Africa (FAO)"],label="Select Region:")
    return (multiselect,)


@app.cell
def _(datetime, mo):
    # Set up date controls:
    start_date = datetime.date(2001,1,1).year
    end_date = datetime.date(2023,1,1).year
    date_range_slider = mo.ui.range_slider(
        start= start_date,
        stop = end_date,
        value=(start_date,end_date),
        label= "Select Year"
    )
    return (date_range_slider,)


@app.cell
def _(date_range_slider, mo, multiselect):
    mo.hstack([date_range_slider,multiselect])
    return


@app.cell
def _(date_range_slider):
    min = date_range_slider.value[0]
    max = date_range_slider.value[1]
    return max, min


@app.cell
def _(df, max, min, multiselect, pd):
    # First dataframe just filters the base one:
    df1 =df[df['Entity'].isin(multiselect.value) & (df['Year']>= min) & (df['Year'] <= max)]

    # A 'World' only dataframe:
    world_data = df[df['Entity'] == 'World'][['Year','undernourishment']]
    world_data.rename(columns={world_data.columns[-1]: "global_value"}, inplace=True)
    # Second dataframe, for variance calculationa nd yearly aggregation:
    df2 = df1.merge(world_data,left_on ='Year',right_on ='Year')
    df2['variance_to_world'] = df2['undernourishment'] - df2['global_value']
    yearly_agg = df2[df2['Entity'] != 'World'].groupby('Year').agg({
            'undernourishment': ['mean', 'median', 'min', 'max'],
            'global_value': 'first', 
            'variance_to_world': ['mean', 'median', 'min', 'max']
        }).reset_index()

    # Munge the yearly aggregated dataframe:
    yearly_agg.columns = ['_'.join(col).strip('_') for col in yearly_agg.columns.values]
    most_recent = df2[df2['Year'] == max]
    earliest = df2[df2['Year'] == min]
    undernourishment_change = pd.concat([earliest,most_recent])

    # Get some of the sumamry statistic values & compare vs world:
    min_year = df2[df2['Entity'] != 'World'].loc[df2[df2['Entity'] != 'World']['undernourishment'].idxmin(), 'Year']
    min_entity = df2[df2['Entity'] != 'World'].loc[df2[df2['Entity'] != 'World']['undernourishment'].idxmin(), 'Entity']
    max_year = df2[df2['Entity'] != 'World'].loc[df2[df2['Entity'] != 'World']['undernourishment'].idxmax(), 'Year']
    max_entity = df2[df2['Entity'] != 'World'].loc[df2[df2['Entity'] != 'World']['undernourishment'].idxmax(), 'Entity']
    average_undernourishment_rate = round(df2['undernourishment'].mean(),2)
    average_undernourishment_rate_world = round(world_data['global_value'].mean(),2)
    undernourishment_change['undernourishment_lag'] = undernourishment_change.groupby('Entity')['undernourishment'].shift(1)
    average_vs_world = round(average_undernourishment_rate -average_undernourishment_rate_world,2)

    # Calculate difference between current and lagged values:
    undernourishment_change['undernourishment_change'] = undernourishment_change['undernourishment'] - undernourishment_change['undernourishment_lag']
    undernourishment_change[undernourishment_change['undernourishment_change'].notna()]
    entity_w_most_improv = undernourishment_change[undernourishment_change['Entity'] != 'World'].loc[undernourishment_change[undernourishment_change['Entity'] != 'World']['undernourishment_change'].idxmin(), 'Entity']

    percent_w_most_improv = round(undernourishment_change[undernourishment_change['Entity'] != 'World'].loc[undernourishment_change[undernourishment_change['Entity'] != 'World']['undernourishment_change'].idxmin(), 'undernourishment_change'],2)
    return (
        average_undernourishment_rate,
        average_vs_world,
        df2,
        entity_w_most_improv,
        max_entity,
        max_year,
        min_entity,
        min_year,
        percent_w_most_improv,
        undernourishment_change,
        yearly_agg,
    )


@app.cell
def _(
    average_undernourishment_rate,
    average_vs_world,
    entity_w_most_improv,
    max,
    max_entity,
    max_year,
    min,
    min_entity,
    min_year,
    mo,
    percent_w_most_improv,
):
    # Define the KPI Cards:
    average_undernourishment_stat = mo.stat(
        label = "Average Undernourishment Rate",
        bordered=True,
        caption = f"{average_vs_world/100:.2%} {'Lower' if average_vs_world < 0 else 'Higher'} than world average",
        value =  f"{average_undernourishment_rate/100:.2%}",
        direction="increase"
            if average_vs_world < 0
            else "decrease"
    )

    year_low_undernourishment_stat = mo.stat(
        label = "Year with Lowest Undernourishment Rate",
        bordered=True,
        caption = f"Entity: {min_entity}",
        value =  f"{min_year}"
    )

    year_high_undernourishment_stat = mo.stat(
        label = "Year with Highest Undernourishment Rate",
        bordered=True,
        caption = f"Entity: {max_entity}",
        value =  f"{max_year}"
    )

    most_improved_entity_stat = mo.stat(
        label = "Best Undernourishment Rate improvement",
        bordered=True,
        caption = f"Entity: {entity_w_most_improv}, {min} - {max}",
        value =  f"{percent_w_most_improv/100:.2%}",
        direction="increase"
            if percent_w_most_improv < 0
            else "decrease",
    )
    mo.hstack([average_undernourishment_stat,year_low_undernourishment_stat,year_high_undernourishment_stat,most_improved_entity_stat],widths="equal")
    return


@app.cell
def _(alt, df2, max, min, mo):
    # First chart, undernourishment over time by region:

    chart1 = alt.Chart(df2).mark_line(
            point=alt.OverlayMarkDef(
                size=45,  
                shape='circle',  
                filled=True, 
                stroke='white', 
                strokeWidth=1  
            ),
            strokeWidth=4  
        ).encode(
            x=alt.X('Year:Q', 
                    axis=alt.Axis(format='d', title='Year'),
                    scale=alt.Scale(domain=[min-0.5, max+0.5])), 
            y=alt.Y('undernourishment:Q', 
                    axis=alt.Axis(title='Undernourishment Prevalence (%)'),
                    scale=alt.Scale(domain=[0, df2['undernourishment'].max()+2])),
            color='Entity',
            tooltip=[
                alt.Tooltip('Entity', title='Entity:'),
                alt.Tooltip('Year', title='Year:'),
                alt.Tooltip('undernourishment', title='Undernourishment:', format='.1f', formatType='number')
            ]
        ).properties(
            title='Prevalence of Undernourishment Over Time by Region',
            font="Lato"
        ).configure_legend(
            orient="bottom",
            title=None    ).interactive()

    mo.ui.altair_chart(chart1)
    return


@app.cell
def _(alt, max, min, multiselect, yearly_agg):
    # Chart 2, selected average undernourishment variance to world average:

    selected_regions = ", ".join(multiselect.value)    

    # Cuistome tool tip text:
    yearly_agg['variance_description'] = yearly_agg['variance_to_world_mean'].apply(
        lambda x: f"{abs(x):.1f}% {'Lower' if x < 0 else 'Higher'} than world average"
    )

    # Blue and red color scale:
    color_scale_2 = alt.condition(
                alt.datum.variance_to_world_mean < 0,
                alt.value("steelblue"),  
                alt.value("indianred")  
        )

    # Second chart variance to world mean with custom tooltip text:
    chart2 = alt.Chart(yearly_agg[['Year','undernourishment_mean','variance_to_world_mean', 'variance_description']]).mark_bar(size=20).encode(
                        x=alt.X('Year:Q', axis=alt.Axis(format='d', title=None), scale=alt.Scale(domain=[min-0.5,max+0.5])),
                        y=alt.Y('variance_to_world_mean:Q', axis=alt.Axis(title='Variance to World Average')),
                        color=color_scale_2,  
                        tooltip=[ 
                            alt.Tooltip('Year', title='Year:'),
                            alt.Tooltip('undernourishment_mean', title='Undernourishment:', format='.1f'),
                            alt.Tooltip('variance_description', title='Comparison:')
                        ]
                    ).properties(
                        title='Average Undernourishment Rate Variance to World Undernourishment Rate',
                        font="Lato",
                        width="container",
                        height=370
                    ).configure_legend(orient="bottom", title=None).interactive()
    return (chart2,)


@app.cell
def _(alt, max, min, undernourishment_change):
    # Chart 3, change from min. to max year by entity:
    chart3 = alt.Chart(undernourishment_change).mark_line(
                strokeWidth=3
            ).encode(
                x=alt.X('Year:Q',
                        axis=alt.Axis(labelAngle=0, format='d', values=undernourishment_change['Year'].unique()),
                        scale=alt.Scale(domain=[undernourishment_change['Year'].min()-1, undernourishment_change['Year'].max()+1.01])),
                y=alt.Y('undernourishment:Q', 
                        axis=alt.Axis(title='Undernourishment Prevalence (%)'),
                        scale=alt.Scale(domain=[0, undernourishment_change['undernourishment'].max()*1.1])),
                color=alt.Color('Entity:N', legend=alt.Legend(orient='bottom',columns=3 ,title=None)),
                tooltip=['Entity', 'Year', 'undernourishment']
            )

    # Add points to the line chart:
    points = alt.Chart(undernourishment_change).mark_circle(
                size=80,
                opacity=1,
                stroke='white',
                strokeWidth=1
            ).encode(
                x='Year:Q',
                y='undernourishment:Q',
                color='Entity:N',
                tooltip=[alt.Tooltip('Entity',title='Entity:'),
                         alt.Tooltip('Year',title='Year:'),
                        alt.Tooltip('undernourishment', title='Undernourishment:', format='.1f')]
            )

    # Add text labels for tooltip:
    text = alt.Chart(undernourishment_change).mark_text(
                align='left',
                baseline='middle',
                dx=7,
                dy=-10,
                fontSize=10
            ).encode(
                x='Year:Q',
                y='undernourishment:Q',
                text=alt.Text('undernourishment:Q', format='.1f'),
                color='Entity:N'
            )

    # Final shart with configurations:
    slope_chart = (chart3 + points + text).properties(
                title=f"Change in Undernourishment ({min}-{max})",
                width="container",
                height=373
            ).configure_view(
                    strokeWidth=0
                ).interactive()
    return (slope_chart,)


@app.cell
def _(chart2, mo, multiselect, slope_chart):
    # Output the two charts together:
    mo.hstack([mo.vstack([
                        mo.ui.altair_chart(chart2),
                        mo.md(f"*Selected regions: {', '.join([region for region in multiselect.value if region != 'World'])} vs. World*") if multiselect.value else mo.md("")
                    ]),
                    mo.ui.altair_chart(slope_chart)
                ], widths=["70%", "30%"])
    return


if __name__ == "__main__":
    app.run()
