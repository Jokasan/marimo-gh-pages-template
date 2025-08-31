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
    import datetime
    import marimo as mo
    import altair as alt
    import pandas as pd
    import requests
    return alt, datetime, mo, pd


@app.cell
def _(pd):
    df = pd.read_csv("https://ourworldindata.org/grapher/prevalence-of-undernourishment.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
    df.rename(columns={df.columns[-1]: "undernourishment"}, inplace=True)
    df = df.drop(columns=['Code'])
    return (df,)


@app.cell
def _(mo):
    options = ["World","Northern Africa (FAO)","South-eastern Asia (FAO)","South America (FAO)","Central Asia (FAO)","Sub-Saharan Africa (FAO)"]
    multiselect = mo.ui.multiselect(options=options,value=["Northern Africa (FAO)","South-eastern Asia (FAO)","South America (FAO)","Central Asia (FAO)","Sub-Saharan Africa (FAO)"],label="Select Region:")
    return (multiselect,)


@app.cell
def _(datetime, mo):
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
def _(max, min, mo):
    mo.md(f"""> Selected dates: {min} - {max}""")
    return


@app.cell
def _(df, max, min, multiselect, pd):
    df1 =df[df['Entity'].isin(multiselect.value) & (df['Year']>= min) & (df['Year'] <= max)]
    world_data = df[df['Entity'] == 'World'][['Year','undernourishment']]
    world_data.rename(columns={world_data.columns[-1]: "global_value"}, inplace=True)
    df2 = df1.merge(world_data,left_on ='Year',right_on ='Year')
    df2['variance_to_world'] = df2['undernourishment'] - df2['global_value']
    yearly_agg = df2.groupby('Year').agg({
            'undernourishment': ['mean', 'median', 'min', 'max'],
            'global_value': 'first',  # Since global value is the same for each year
            'variance_to_world': ['mean', 'median', 'min', 'max']
        }).reset_index()

        # Flatten the multi-level column headers
    yearly_agg.columns = ['_'.join(col).strip('_') for col in yearly_agg.columns.values]
    most_recent = df2[df2['Year'] == max]
    earliest = df2[df2['Year'] == min]
    result = pd.concat([earliest,most_recent])

    min_year = df2[df2['Entity'] != 'World'].loc[df2[df2['Entity'] != 'World']['undernourishment'].idxmin(), 'Year']
    min_entity = df2[df2['Entity'] != 'World'].loc[df2[df2['Entity'] != 'World']['undernourishment'].idxmin(), 'Entity']
    max_year = df2[df2['Entity'] != 'World'].loc[df2[df2['Entity'] != 'World']['undernourishment'].idxmax(), 'Year']
    max_entity = df2[df2['Entity'] != 'World'].loc[df2[df2['Entity'] != 'World']['undernourishment'].idxmax(), 'Entity']
    average_undernourishment_rate = round(df2['undernourishment'].mean(),2)
    average_undernourishment_rate_world = round(world_data['global_value'].mean(),2)
    result['undernourishment_lag'] = result.groupby('Entity')['undernourishment'].shift(1)

    average_vs_world = round(average_undernourishment_rate -average_undernourishment_rate_world,2)

    # Calculate difference between current and lagged values
    result['undernourishment_change'] = result['undernourishment'] - result['undernourishment_lag']
    result[result['undernourishment_change'].notna()]
    entity_w_most_improv = result[result['Entity'] != 'World'].loc[result[result['Entity'] != 'World']['undernourishment_change'].idxmin(), 'Entity']

    percent_w_most_improv = round(result[result['Entity'] != 'World'].loc[result[result['Entity'] != 'World']['undernourishment_change'].idxmin(), 'undernourishment_change'],2)
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
        result,
        yearly_agg,
    )


@app.cell
def _(
    average_undernourishment_rate,
    average_vs_world,
    entity_w_most_improv,
    max_entity,
    max_year,
    min_entity,
    min_year,
    mo,
    percent_w_most_improv,
):
    average_undernourishment_stat = mo.stat(
        label = "Average Undernourishment Rate",
        bordered=True,
        caption = f"Vs World Average: {average_vs_world/100:.00%}",
        value =  f"{average_undernourishment_rate/100:.00%}",
        direction="increase"
            if average_vs_world > 0
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
        label = "Greatest Reduction in Undernourishment",
        bordered=True,
        caption = f"Entity: {entity_w_most_improv}",
        value =  f"{percent_w_most_improv/100:.00%}",
        direction="increase"
            if percent_w_most_improv < 0
            else "decrease"
    )
    mo.hstack([average_undernourishment_stat,year_low_undernourishment_stat,year_high_undernourishment_stat,most_improved_entity_stat],widths="equal")
    return


@app.cell
def _(alt, df2, mo):
    chart1 = alt.Chart(df2).mark_line(
            point=alt.OverlayMarkDef(
                size=20,  # Point size
                shape='circle',  
                filled=True,  # Whether points are filled
                stroke='white',  # Point outline color
                strokeWidth=1  # Point outline thickness
            ),
            strokeWidth=3  # Line thickness (increase from 2 to 3)
        ).encode(
            x=alt.X('Year:Q', axis=alt.Axis(format='d', title='Year')), 
            y=alt.Y('undernourishment:Q', axis=alt.Axis(title='Undernourishment Prevalence (%)')),
            color='Entity',
            tooltip=[
                'Entity', 
                'Year', 
                alt.Tooltip('undernourishment', title='Nourishment:', format='.1f', formatType='number')
            ]
        ).properties(
            title='Prevalence of Undernourishment Over Time by Region',
            font="Lato"
        ).configure_legend(
            orient="bottom",
            title=None
        ).interactive()
    mo.ui.altair_chart(chart1)
    return


@app.cell
def _(alt, multiselect, yearly_agg):
    selected_regions = ", ".join(multiselect.value)    

    color_scale_2 = alt.condition(
                alt.datum.variance_to_world_mean < 0,
                alt.value("steelblue"),  # When below 0
                alt.value("indianred")  # Otherwise
        )

    chart2 = alt.Chart(yearly_agg[['Year','undernourishment_median','variance_to_world_mean']]).mark_bar(size=20).encode(
                        x=alt.X('Year:Q', axis=alt.Axis(format='d', title=None)),
                        y=alt.Y('variance_to_world_mean:Q', axis=alt.Axis(title='Variance to World Average')),
                        color=color_scale_2,  
                        tooltip=[
                            'Year', 
                            alt.Tooltip('undernourishment_median', title='undernourishment:', format='.1f', formatType='number'),
                            alt.Tooltip('variance_to_world_mean', title='variance:', format='.1f', formatType='number')
                        ]
                    ).properties(
                        title='Variance to World Undernourishment',
                        font="Lato",
                        width="container"
                    ).configure_legend(orient="bottom", title=None).configure_view(
                        continuousWidth=200  
                    ).interactive()
    return chart2, selected_regions


@app.cell
def _(alt, result):
    chart3 = alt.Chart(result).mark_line(
            point=alt.OverlayMarkDef(
                size=40,  # Point size
                shape='circle',  
                filled=True,  # Whether points are filled
                stroke='white',  # Point outline color
                strokeWidth=1  # Point outline thickness
            ),
            strokeWidth=4  # Line thickness (increase from 2 to 3)
        ).encode(
            x='Year:O',
            y='variance_to_world',
            color='Entity',
            tooltip=['Entity', 'Year', 'undernourishment']
        ).properties(
            title='Change in Undernourishment'
        ).configure_legend(orient="bottom",title=None).interactive()
    return (chart3,)


@app.cell
def _(chart2, chart3, mo, selected_regions):
    mo.hstack([
           mo.vstack([
            mo.ui.altair_chart(chart2),
            mo.md(f"*Selected regions: {selected_regions}*")
        ]),
            mo.ui.altair_chart(chart3)
        ],widths="equal")
    return


if __name__ == "__main__":
    app.run()
